// ~/.agents/workflows/chain-draft.js
// Pattern: Prompt Chaining / Sequential Workflow (taxonomy: Workflow).
// Each stage's output becomes the next stage's input:
//   Analyze -> Draft -> Review -> Finalize
// Stages are fixed in advance (unlike plan-execute.js, which replans).
//
// Args:
//   task: string (required) — the writing/artifact task
//   audience: string (optional) — who reads it
//   format: string (optional, default "markdown") — output format
//
// Returns:
//   { task, analysis, review, final, draft_excerpt }

export const meta = {
  name: "chain_draft",
  description:
    "Prompt chaining for artifact production: analyze the request, draft, review against explicit criteria, finalize. Stages are fixed; each feeds the next.",
  phases: [
    { title: "Analyze" },
    { title: "Draft" },
    { title: "Review" },
    { title: "Finalize" },
  ],
};

const ANALYSIS = {
  type: "object",
  properties: {
    goal: { type: "string" },
    audience: { type: "string" },
    key_points: { type: "array", items: { type: "string" } },
    structure: { type: "array", items: { type: "string" } },
    representation: { type: "string" },
    constraints: { type: "array", items: { type: "string" } },
  },
  required: ["goal", "key_points"],
};

const DRAFT = {
  type: "object",
  properties: { artifact: { type: "string" } },
  required: ["artifact"],
};

const REVIEW = {
  type: "object",
  properties: {
    issues: {
      type: "array",
      items: {
        type: "object",
        properties: {
          severity: { type: "string", enum: ["material", "minor"] },
          issue: { type: "string" },
          suggestion: { type: "string" },
        },
        required: ["severity", "issue"],
      },
    },
    verdict: { type: "string", enum: ["publish", "revise"] },
  },
  required: ["issues", "verdict"],
};

phase("Analyze");
const task = args && typeof args.task === "string" ? args.task.trim() : "";
const audience = args && typeof args.audience === "string" ? args.audience : "unspecified";
const format = args && typeof args.format === "string" ? args.format : "markdown";
if (!task) return { error: "task argument required" };

const analysis = await agent(
  "Analyze this artifact request. Identify goal, audience, key points, section " +
  "structure, the best representation (prose / table / diagram / code, per the " +
  "choose-the-best-representation rule), and constraints.\n\n" +
  "Task: " + task + "\nAudience: " + audience + "\nFormat: " + format + "\n\n" +
  "Return JSON: { goal, audience, key_points, structure, representation, constraints }.",
  { label: "chain:analyze", schema: ANALYSIS }
);

phase("Draft");
const draft = await agent(
  "Draft the artifact described by this analysis. Follow the structure and " +
  "representation it chose. Match the requested format (" + format + ").\n\n" +
  "Analysis:\n" + JSON.stringify(analysis, null, 2) + "\n\n" +
  "Return JSON: { artifact } — the full artifact as one string.",
  { label: "chain:draft", schema: DRAFT }
);
if (!draft || typeof draft.artifact !== "string") {
  return { error: "draft stage failed", analysis };
}

phase("Review");
const review = await agent(
  "Review this draft against explicit criteria: accuracy, clarity, completeness, " +
  "format suitability. Judge against the analysis, not abstract ideals.\n\n" +
  "Analysis:\n" + JSON.stringify(analysis, null, 2) + "\n\nDraft:\n" + draft.artifact + "\n\n" +
  'Return JSON: { issues: [{ severity: "material"|"minor", issue, suggestion }], verdict: "publish"|"revise" }. ' +
  "Only material issues justify a revise verdict.",
  { label: "chain:review", schema: REVIEW }
);

phase("Finalize");
const finalize = await agent(
  "Produce the final artifact. Fix every material issue from the review; take " +
  "minor issues only when cheap. If the verdict was publish, pass the draft " +
  "through unchanged and say so.\n\n" +
  "Draft:\n" + draft.artifact + "\n\nReview:\n" + JSON.stringify(review, null, 2) + "\n\n" +
  "Return JSON: { artifact, changes_made: [string] }.",
  { label: "chain:finalize", schema: {
    type: "object",
    properties: {
      artifact: { type: "string" },
      changes_made: { type: "array", items: { type: "string" } },
    },
    required: ["artifact"],
  } }
);

return {
  task,
  analysis,
  review,
  final: finalize && finalize.artifact ? finalize.artifact : draft.artifact,
  changes_made: finalize && finalize.changes_made ? finalize.changes_made : [],
  draft_excerpt: draft.artifact.slice(0, 400),
};
