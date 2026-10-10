// ~/.agents/workflows/plan-execute.js
// Pattern: Plan-and-Execute (taxonomy: Planning).
// A planner decomposes the goal into dependency-ordered steps. Executors
// run each batch (parallel within a batch, sequential across batches).
// An evaluator judges the goal; a bounded replan reworks failed steps.
//
// Args:
//   goal: string (required) — what to achieve
//   context: string (optional) — repo paths, constraints, prior decisions
//   max_replans: number (default 1, capped 3) — bounded revision passes
//   parallelize: boolean (default true) — run independent steps concurrently
//
// Returns:
//   { goal, plan, results, evaluation, replans, status }
//   status: "done" | "needs_attention" (latter doubles as the HITL signal)

export const meta = {
  name: "plan_execute",
  description:
    "Plan-and-Execute: decompose a goal into dependency-ordered steps, execute them in parallel batches, evaluate against the goal, and replan bounded times on failure.",
  phases: [
    { title: "Setup" },
    { title: "Plan" },
    { title: "Execute" },
    { title: "Evaluate" },
    { title: "Replan" },
  ],
};

const STEP_RESULT = {
  type: "object",
  properties: {
    id: { type: "string" },
    status: { type: "string", enum: ["done", "blocked"] },
    deliverable: { type: "string" },
    summary: { type: "string" },
  },
  required: ["id", "status", "summary"],
};

const PLAN = {
  type: "object",
  properties: {
    steps: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          title: { type: "string" },
          instructions: { type: "string" },
          depends_on: { type: "array", items: { type: "string" } },
          deliverable: { type: "string" },
        },
        required: ["id", "title"],
      },
    },
    assumptions: { type: "array", items: { type: "string" } },
    risks: { type: "array", items: { type: "string" } },
  },
  required: ["steps"],
};

const EVAL = {
  type: "object",
  properties: {
    goal_met: { type: "boolean" },
    failed_steps: { type: "array", items: { type: "string" } },
    findings: { type: "array", items: { type: "string" } },
    confidence: { type: "string", enum: ["high", "med", "low"] },
  },
  required: ["goal_met"],
};

phase("Setup");
const goal = args && typeof args.goal === "string" ? args.goal.trim() : "";
const context = args && typeof args.context === "string" ? args.context : "";
const maxReplans = args && Number.isFinite(Number(args.max_replans))
  ? Math.max(0, Math.min(3, Math.floor(Number(args.max_replans))))
  : 1;
const parallelize = args ? args.parallelize !== false : true;
if (!goal) return { error: "goal argument required" };
const ctx = context ? "\n\nContext:\n" + context : "";

const excerpt = (v, n) => JSON.stringify(v ?? "not run").slice(0, n || 1200);

// Kahn's algorithm, level by level: steps in the same batch are independent.
function topoBatches(steps) {
  const byId = new Map(steps.map((s) => [s.id, s]));
  const remaining = new Set(steps.map((s) => s.id));
  const done = new Set();
  const batches = [];
  while (remaining.size > 0) {
    const ready = [...remaining].filter((id) =>
      (byId.get(id).depends_on || []).every((d) => done.has(d))
    );
    if (ready.length === 0) {
      return { error: "cycle or unknown dependency in steps", stuck: [...remaining] };
    }
    batches.push(ready);
    ready.forEach((id) => { done.add(id); remaining.delete(id); });
  }
  return { batches };
}

async function executeSteps(steps, priorOutcomes, outcomes) {
  const { batches, error } = topoBatches(steps);
  if (error) return { error };
  for (const batch of batches) {
    const fns = batch.map((id) => () => {
      const s = steps.find((x) => x.id === id);
      const deps = (s.depends_on || [])
        .map((d) => "  - " + d + ": " + excerpt(outcomes[d] ?? priorOutcomes[d]))
        .join("\n");
      return agent(
        "Goal: " + goal + ctx + "\n\n" +
        "Execute this step and return its deliverable as JSON:\n" +
        JSON.stringify({ id: s.id, title: s.title, instructions: s.instructions || "" }) + "\n\n" +
        (deps ? "Results from steps this one depends on:\n" + deps + "\n\n" : "") +
        'Keep the deliverable concrete (files read/changed, findings, artifacts). ' +
        'Return JSON: { id, status: "done"|"blocked", deliverable, summary }.',
        { label: "execute:" + s.id, schema: STEP_RESULT }
      );
    });
    const ran = parallelize && fns.length > 1
      ? await parallel(fns)
      : await fns.reduce(async (acc, f) => [...(await acc), await f()], Promise.resolve([]));
    batch.forEach((id, i) => { outcomes[id] = ran[i]; });
  }
  return { ok: true };
}

phase("Plan");
const plan = await agent(
  "Decompose this goal into 3-8 concrete steps.\nGoal: " + goal + ctx + "\n\n" +
  "Rules: every step needs a verifiable deliverable; use depends_on only when a step " +
  "genuinely needs another's output; ids are short snake_case.\n\n" +
  "Return JSON: { steps: [{ id, title, instructions, depends_on, deliverable }], assumptions, risks }.",
  { label: "plan:decompose", schema: PLAN }
);

phase("Execute");
const outcomes = {};
const exec = await executeSteps(plan.steps, {}, outcomes);
if (exec.error) return { error: exec.error, goal, plan };

phase("Evaluate");
const evaluate = async () =>
  agent(
    "Goal: " + goal + ctx + "\n\nStep results:\n" +
    plan.steps.map((s) => "- " + s.id + ": " + excerpt(outcomes[s.id], 800)).join("\n") +
    "\n\nJudge whether the combined deliverables meet the goal. " +
    'Return JSON: { goal_met, failed_steps: [id], findings: [string], confidence: "high"|"med"|"low" }.',
    { label: "plan:evaluate", schema: EVAL }
  );
let evaluation = await evaluate();

let replans = [];
let round = 0;
let currentSteps = plan.steps;
while (!evaluation.goal_met && round < maxReplans) {
  round += 1;
  phase("Replan (round " + round + ")");
  const revised = await agent(
    "The plan below did not meet its goal. Produce replacement steps for ONLY the failed parts.\n" +
    "Goal: " + goal + ctx + "\n\n" +
    "Failed steps and evaluator findings:\n" +
    (evaluation.failed_steps || []).map((id) => "- " + id + ": " + excerpt(outcomes[id], 600)).join("\n") +
    "\nFindings: " + JSON.stringify(evaluation.findings || []) + "\n\n" +
    "Return JSON: { steps: [{ id, title, instructions, depends_on, deliverable }] } — ids may reuse failed ones.",
    { label: "plan:replan-" + round, schema: PLAN }
  );
  const rerun = await executeSteps(revised.steps, outcomes, outcomes);
  if (rerun.error) return { error: rerun.error, goal, plan, results: outcomes, evaluation };
  currentSteps = currentSteps
    .filter((s) => !revised.steps.some((r) => r.id === s.id))
    .concat(revised.steps);
  evaluation = await evaluate();
  replans.push({ round, revised_ids: revised.steps.map((s) => s.id), goal_met_after: evaluation.goal_met });
}

return {
  goal,
  plan: { ...plan, steps: currentSteps },
  results: outcomes,
  evaluation,
  replans,
  status: evaluation.goal_met ? "done" : "needs_attention",
};
