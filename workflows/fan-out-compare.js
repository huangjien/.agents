// ~/.agents/workflows/fan-out-compare.js
// Pattern: Parallelization (taxonomy: Workflow).
// One question, N independent angles investigated concurrently, then an
// aggregator reconciles the results. Static split — no planner, no replan
// (that's plan-execute.js / orchestrate-project.js territory).
//
// Args:
//   question: string (required) — the question to investigate
//   branches: string[] (optional) — angles/options to compare (e.g.
//             ["Redis", "Memcached", "in-process LRU"]). If omitted, a
//             splitter agent proposes 3-5.
//   max_branches: number (default 4, capped 6)
//
// Returns:
//   { question, branches, investigations, synthesis }

export const meta = {
  name: "fan_out_compare",
  description:
    "Parallelization: investigate one question from N independent angles in parallel, then reconcile into a single synthesis with agreements, conflicts, and a recommendation.",
  phases: [
    { title: "Setup" },
    { title: "Split" },
    { title: "Investigate (parallel)" },
    { title: "Aggregate" },
  ],
};

const INVESTIGATION = {
  type: "object",
  properties: {
    branch: { type: "string" },
    findings: { type: "array", items: { type: "string" } },
    recommendation: { type: "string" },
    confidence: { type: "string", enum: ["high", "med", "low"] },
  },
  required: ["branch", "findings"],
};

const SYNTHESIS = {
  type: "object",
  properties: {
    synthesis: { type: "string" },
    agreements: { type: "array", items: { type: "string" } },
    conflicts: { type: "array", items: { type: "string" } },
    recommendation: { type: "string" },
    open_questions: { type: "array", items: { type: "string" } },
  },
  required: ["synthesis"],
};

phase("Setup");
const question = args && typeof args.question === "string" ? args.question.trim() : "";
const given = Array.isArray(args && args.branches) ? args.branches.filter(String) : [];
const maxBranches = args && Number.isFinite(Number(args.max_branches))
  ? Math.max(2, Math.min(6, Math.floor(Number(args.max_branches))))
  : 4;
if (!question) return { error: "question argument required" };

phase("Split");
let branches = given.slice(0, maxBranches);
if (branches.length === 0) {
  const split = await agent(
    "Propose 3-" + maxBranches + " independent angles for investigating this question. " +
    "Each angle must be genuinely independent (no shared prerequisite work) and " +
    "add distinct information.\n\nQuestion: " + question + "\n\n" +
    "Return JSON: { branches: [{ label, angle }] }.",
    { label: "fanout:split", schema: {
      type: "object",
      properties: {
        branches: {
          type: "array",
          items: {
            type: "object",
            properties: { label: { type: "string" }, angle: { type: "string" } },
            required: ["label"],
          },
        },
      },
      required: ["branches"],
    } }
  );
  branches = ((split && split.branches) || []).slice(0, maxBranches).map((b) => b.label);
}
if (branches.length === 0) return { error: "no branches to investigate", question };

phase("Investigate (parallel)");
const results = await parallel(
  branches.map((label) => () =>
    agent(
      "Investigate this question strictly from your assigned angle. Do not " +
      "stray into other angles; other agents cover them.\n\n" +
      "Question: " + question + "\nYour angle: " + label + "\n\n" +
      "Ground findings in evidence (files, docs, commands run). " +
      'Return JSON: { branch, findings: [string], recommendation, confidence: "high"|"med"|"low" }.',
      { label: "fanout:" + label, schema: INVESTIGATION }
    )
  )
);
const investigations = branches.map((label, i) => ({
  branch: label,
  status: results[i] === null ? "failed" : "complete",
  result: results[i],
}));
const complete = investigations.filter((x) => x.status === "complete");
if (complete.length === 0) {
  return { error: "all branches failed", question, investigations };
}

phase("Aggregate");
const synthesis = await agent(
  "Reconcile these independent investigations of one question into a single " +
  "synthesis. Surface agreements and conflicts explicitly — do not average " +
  "incompatible conclusions; if the evidence conflicts, say so and recommend " +
  "how to resolve it.\n\n" +
  "Question: " + question + "\n\n" +
  "Investigations:\n" + complete.map((x) => JSON.stringify(x.result)).join("\n") + "\n\n" +
  "Return JSON: { synthesis, agreements, conflicts, recommendation, open_questions }.",
  { label: "fanout:aggregate", schema: SYNTHESIS }
);

return { question, branches, investigations, synthesis };
