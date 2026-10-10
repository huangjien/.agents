// ~/.agents/workflows/critic-loop.js
// Pattern: Evaluator-Optimizer / Critic Loop (taxonomy: Quality control).
// One agent generates an artifact; another evaluates it against explicit
// criteria; a reviser fixes failures. Bounded rounds — default 3, hard
// cap 5 (endless revision loops are a known failure mode).
//
// Args:
//   task: string (required) — what to produce
//   criteria: string[] (optional, default accuracy/clarity/completeness)
//   max_rounds: number (default 3, capped 5)
//
// Returns:
//   { task, rounds, total_rounds, verdict, final }

export const meta = {
  name: "critic_loop",
  description:
    "Evaluator-Optimizer: generate an artifact, evaluate it against explicit criteria, revise on failure, re-evaluate — bounded to a few rounds.",
  phases: [
    { title: "Generate" },
    { title: "Criticize" },
    { title: "Revise" },
  ],
};

const ARTIFACT = {
  type: "object",
  properties: { artifact: { type: "string" } },
  required: ["artifact"],
};

const CRITIQUE = {
  type: "object",
  properties: {
    pass: { type: "boolean" },
    scores: {
      type: "array",
      items: {
        type: "object",
        properties: {
          criterion: { type: "string" },
          pass: { type: "boolean" },
          note: { type: "string" },
        },
        required: ["criterion", "pass"],
      },
    },
    issues: { type: "array", items: { type: "string" } },
  },
  required: ["pass", "scores"],
};

phase("Generate");
const task = args && typeof args.task === "string" ? args.task.trim() : "";
const criteria = Array.isArray(args && args.criteria) && args.criteria.filter(String).length > 0
  ? args.criteria.filter(String)
  : ["accuracy", "clarity", "completeness"];
const maxRounds = args && Number.isFinite(Number(args.max_rounds))
  ? Math.max(1, Math.min(5, Math.floor(Number(args.max_rounds))))
  : 3;
if (!task) return { error: "task argument required" };

let current = await agent(
  "Produce this artifact to a high standard on the first pass:\n\n" + task,
  { label: "critic:generate", schema: ARTIFACT }
);
if (!current || typeof current.artifact !== "string") {
  return { error: "generate stage failed", task };
}

const rounds = [];
for (let round = 1; round <= maxRounds; round++) {
  phase("Criticize (round " + round + ")");
  const critique = await agent(
    "Evaluate this artifact against each criterion. Be specific and strict: " +
    "a criterion passes only on evidence, not charity.\n\n" +
    "Task: " + task + "\nCriteria: " + criteria.join(", ") + "\n\n" +
    "Artifact:\n" + current.artifact + "\n\n" +
    "Return JSON: { pass, scores: [{ criterion, pass, note }], issues: [string] }. " +
    "pass is true only if every criterion passes.",
    { label: "critic:evaluate-" + round, schema: CRITIQUE }
  );
  if (!critique) return { error: "evaluate stage failed in round " + round, task, rounds };

  rounds.push({
    round,
    pass: critique.pass,
    scores: critique.scores,
    issues: critique.issues || [],
  });
  if (critique.pass || round === maxRounds) break;

  phase("Revise");
  const revised = await agent(
    "Revise this artifact to fix every failed criterion. Change only what " +
    "the critique justifies — no rewrites for taste.\n\n" +
    "Task: " + task + "\n\nCritique:\n" + JSON.stringify(critique, null, 2) + "\n\n" +
    "Current artifact:\n" + current.artifact + "\n\n" +
    "Return JSON: { artifact } — the full revised artifact.",
    { label: "critic:revise-" + round, schema: ARTIFACT }
  );
  if (revised && typeof revised.artifact === "string") current = revised;
}

const last = rounds[rounds.length - 1];
return {
  task,
  rounds,
  total_rounds: rounds.length,
  verdict: last && last.pass ? "pass" : "max_rounds_exceeded",
  final: current.artifact,
};
