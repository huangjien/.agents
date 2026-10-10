// ~/.agents/workflows/orchestrate-project.js
// Pattern: Orchestrator-Workers (taxonomy: Multi-agent).
// Unlike fan-out-compare.js (same question, N angles), here a decomposer
// breaks a PROJECT into distinct workstreams; each worker is autonomous
// within its brief; an integrator merges the handoffs.
//
// Args:
//   project: string (required) — the project or large task
//   context: string (optional) — repo paths, constraints, prior decisions
//   max_workers: number (default 4, capped 6)
//
// Returns:
//   { project, workstreams, worker_results, integration }

export const meta = {
  name: "orchestrate_project",
  description:
    "Orchestrator-Workers: decompose a project into distinct workstreams, delegate each to an autonomous worker in parallel, then integrate the handoffs into one coherent result.",
  phases: [
    { title: "Setup" },
    { title: "Decompose" },
    { title: "Delegate (parallel)" },
    { title: "Integrate" },
  ],
};

const DECOMPOSITION = {
  type: "object",
  properties: {
    workstreams: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          title: { type: "string" },
          brief: { type: "string" },
          success_criteria: { type: "string" },
        },
        required: ["id", "title", "brief"],
      },
    },
    interfaces: { type: "array", items: { type: "string" } },
  },
  required: ["workstreams"],
};

const HANDOFF = {
  type: "object",
  properties: {
    workstream: { type: "string" },
    status: { type: "string", enum: ["done", "partial", "blocked"] },
    deliverable: { type: "string" },
    summary: { type: "string" },
    handoff: { type: "string" },
  },
  required: ["workstream", "status", "summary", "handoff"],
};

const INTEGRATION = {
  type: "object",
  properties: {
    integrated_summary: { type: "string" },
    conflicts: { type: "array", items: { type: "string" } },
    gaps: { type: "array", items: { type: "string" } },
    next_steps: { type: "array", items: { type: "string" } },
  },
  required: ["integrated_summary"],
};

phase("Setup");
const project = args && typeof args.project === "string" ? args.project.trim() : "";
const context = args && typeof args.context === "string" ? args.context : "";
const maxWorkers = args && Number.isFinite(Number(args.max_workers))
  ? Math.max(1, Math.min(6, Math.floor(Number(args.max_workers))))
  : 4;
if (!project) return { error: "project argument required" };
const ctx = context ? "\n\nContext:\n" + context : "";

phase("Decompose");
const decomposition = await agent(
  "Decompose this project into 2-" + maxWorkers + " distinct workstreams. " +
  "Each workstream must be executable autonomously: a worker gets the brief " +
  "and no further orchestration. Define what each workstream hands back to " +
  "the integrator.\n\nProject: " + project + ctx + "\n\n" +
  "Return JSON: { workstreams: [{ id, title, brief, success_criteria }], " +
  "interfaces: [what the integrator should watch for when merging] }.",
  { label: "orchestrate:decompose", schema: DECOMPOSITION }
);
const streams = ((decomposition && decomposition.workstreams) || []).slice(0, maxWorkers);
if (streams.length === 0) return { error: "decomposition produced no workstreams", project };
const dropped = ((decomposition && decomposition.workstreams) || []).length - streams.length;

phase("Delegate (parallel)");
const results = await parallel(
  streams.map((s) => () =>
    agent(
      "You own one workstream of a larger project. Work autonomously within " +
      "your brief; do NOT do other workstreams' work.\n\n" +
      "Project: " + project + ctx + "\n\n" +
      "Your workstream:\n" + JSON.stringify(s, null, 2) + "\n\n" +
      "Return JSON: { workstream, status: \"done\"|\"partial\"|\"blocked\", " +
      "deliverable, summary, handoff } where handoff is exactly what the " +
      "integrator needs to merge your result with the others.",
      { label: "worker:" + s.id, schema: HANDOFF }
    )
  )
);
const worker_results = streams.map((s, i) => ({
  workstream: s.id,
  status: results[i] === null ? "failed" : "complete",
  result: results[i],
}));
const complete = worker_results.filter((x) => x.status === "complete");
if (complete.length === 0) {
  return { error: "all workers failed", project, worker_results };
}

phase("Integrate");
const integration = await agent(
  "Integrate these workstream handoffs into one coherent result for the project.\n\n" +
  "Project: " + project + ctx + "\n\n" +
  (decomposition && decomposition.interfaces
    ? "Watch for these interface concerns:\n" + JSON.stringify(decomposition.interfaces) + "\n\n"
    : "") +
  "Handoffs:\n" + complete.map((x) => JSON.stringify(x.result)).join("\n") + "\n\n" +
  "Name conflicts between workstreams explicitly instead of merging silently. " +
  "Return JSON: { integrated_summary, conflicts, gaps, next_steps }.",
  { label: "orchestrate:integrate", schema: INTEGRATION }
);

return {
  project,
  workstreams: streams.map((s) => s.id),
  workstreams_dropped: dropped > 0 ? dropped : undefined,
  worker_results,
  integration,
};
