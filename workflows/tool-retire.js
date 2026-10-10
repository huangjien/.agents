// ~/.agents/workflows/tool-retire.js
// Implements PAT-20261010-absorbslim-ordering (candidate).
// 5 phases: identify → absorb → slim → drop → verify.
//
// Args:
//   tool: string — name of the tool to retire (e.g. "Claude", "Trae")
//   scope: string (default "~/.agents/") — root of the install
//
// Returns:
//   { tool, scope, phases: { identify, absorb, slim, drop, verify } }

export const meta = {
  name: "tool_retire",
  description:
    "Retire a tool from the agent system following the 5-step absorb-slim-order: identify unique content, absorb to canonical hub, slim per-tool docs, drop references, verify.",
  phases: [
    { title: "1. Identify" },
    { title: "2. Absorb" },
    { title: "3. Slim" },
    { title: "4. Drop" },
    { title: "5. Verify" },
  ],
};

phase("Setup");
const tool = args && typeof args.tool === "string" ? args.tool.trim() : "";
const scope = args && typeof args.scope === "string" ? args.scope : "~/.agents/";
if (!tool) {
  return { error: "tool argument required (e.g. tool='Claude')" };
}

// Phase 1: identify content unique to the tool before any slims
phase("1. Identify");
const identify = await agent(
  `Find content in the to-be-retired tool's native doc(s) and the canonical hub that is unique to ${tool} ` +
    `and would be lost if the per-tool docs are slimmed first. Examples of what to look for:\n` +
    `  - Communication & output style content (the kind of section in Claude's CLAUDE.md or Copilot's instructions)\n` +
    `  - Tool-specific MCP instructions (e.g. codebase-memory-mcp priority order)\n` +
    `  - Tool-specific skill invocation triggers (e.g. /graphify)\n` +
    `  - Anything in the tool's native doc that doesn't exist yet in ${scope}AGENTS.md, ${scope}mcp/, or ${scope}copilot/\n\n` +
    `For each block found, output: location (file:line), content summary, and proposed canonical home ` +
    `(either "absorb into AGENTS.md Part 1 (universal)" or "absorb into ~/.agents/<topic>/<doc>.md (shared)" or "drop entirely (tool-specific, won't survive retirement)").\n\n` +
    `Output as a JSON array: [{block, location, content_summary, proposed_home, reason}]. ` +
    `Empty array if nothing needs absorbing.`,
  {
    label: "retire:identify",
    schema: {
      type: "array",
      items: {
        type: "object",
        properties: {
          block: { type: "string" },
          location: { type: "string" },
          content_summary: { type: "string" },
          proposed_home: { type: "string" },
          reason: { type: "string" },
        },
        required: ["block", "location", "proposed_home"],
      },
    },
  },
);

// Phase 2: absorb — propose concrete diffs to move each block
phase("2. Absorb");
const absorb = await agent(
  `Based on the identify phase output, generate concrete edit instructions that move each content block into its proposed canonical home. ` +
    `For each block, show: target_file, target_section, before (current text to delete), after (new text to insert, with absolute path references).\n\n` +
    `Output as a JSON array: [{block, target_file, target_section, before, after, validation}] where validation is how to confirm the absorption worked (e.g. "grep -c 'topic' ~/.agents/AGENTS.md").`,
  {
    label: "retire:absorb",
    schema: {
      type: "array",
      items: {
        type: "object",
        properties: {
          block: { type: "string" },
          target_file: { type: "string" },
          target_section: { type: "string" },
          before: { type: "string" },
          after: { type: "string" },
          validation: { type: "string" },
        },
        required: ["block", "target_file", "target_section", "before", "after"],
      },
    },
  },
);

// Phase 3: slim — turn each surviving per-tool doc into a thin pointer
phase("3. Slim");
const slim = await agent(
  `For each surviving per-tool doc that still has redundant content, generate a slimmed version. The slim pattern: ` +
    `first line is a one-liner saying "Rules live in ${scope}AGENTS.md" with absolute path; remaining lines are tool-specific extras only (e.g. references to ${scope}mcp/codebase-memory.md for Codex/Gemini).\n\n` +
    `Generate slims for these files (if they exist and still carry redundant content):\n` +
    `  - ${scope}copilot/copilot-instructions.md\n` +
    `  - ${scope.replace(/~$|\/$/, "")}/.codex/AGENTS.md (i.e. ~/.codex/AGENTS.md)\n` +
    `  - ${scope.replace(/~$|\/$/, "")}/.gemini/GEMINI.md (i.e. ~/.gemini/GEMINI.md)\n\n` +
    `Output as a JSON array: [{file, current_lines, slimmed_content, line_count_after}].`,
  {
    label: "retire:slim",
    schema: {
      type: "array",
      items: {
        type: "object",
        properties: {
          file: { type: "string" },
          current_lines: { type: "integer" },
          slimmed_content: { type: "string" },
          line_count_after: { type: "integer" },
        },
        required: ["file", "slimmed_content"],
      },
    },
  },
);

// Phase 4: drop references from install.sh, route.yaml, README, adapters/README
phase("4. Drop");
const drop = await agent(
  `Identify every place that still references the retired tool "${tool}". The active code locations are:\n` +
    `  - ${scope}install.sh (sections, variable definitions, comments — keep migration comments as historical meta-notes)\n` +
    `  - ${scope}route.yaml (header comments)\n` +
    `  - ${scope}AGENTS.md (Part 4 tool table, Part 5 file tree, "OpenCode is the only tool" sentence, Read-by line)\n` +
    `  - ${scope}README.md (Tools section, tool tables)\n` +
    `  - ${scope}adapters/README.md (adapter policy)\n` +
    `  - ${scope}bin/verify-global-agents (any check_link/check_file references)\n\n` +
    `For each location, propose: action (remove | rewrite | keep-as-historical-meta-note), before, after, rationale.\n\n` +
    `Output as a JSON array: [{location, action, before, after, rationale}].`,
  {
    label: "retire:drop",
    schema: {
      type: "array",
      items: {
        type: "object",
        properties: {
          location: { type: "string" },
          action: { type: "string" },
          before: { type: "string" },
          after: { type: "string" },
          rationale: { type: "string" },
        },
        required: ["location", "action", "rationale"],
      },
    },
  },
);

// Phase 5: verify — re-run install + verify-global-agents + final grep
phase("5. Verify");
const verify = await agent(
  `Run the verification checklist for the ${tool} retirement. Output a JSON object with each step's pass/fail and the actual command output (first 20 lines):\n\n` +
    `  1. shell: \`bash -n ${scope}install.sh && echo OK\` — must print OK.\n` +
    `  2. shell: \`${scope}bin/verify-global-agents\` — last line should show "0 warnings" (10 OK / 0 warnings).\n` +
    `  3. shell: \`bash ~/.agents/install.sh\` — must complete without error.\n` +
    `  4. grep: \`grep -r "${tool}" ~/.agents/\` — should return only intentional historical refs (wiki/notes/, wiki/index.md, wiki/logs.md, .archive/, or install.sh migration comments that explain the absence).\n` +
    `  5. grep: \`grep -r "active code ref to ~/${tool.toLowerCase()}/" ~/.agents/\` — should be empty in active code.\n\n` +
    `Output: { steps: [{name, command, passed, output_excerpt}], overall: "PASS" | "FAIL" }.`,
  {
    label: "retire:verify",
    schema: {
      type: "object",
      properties: {
        steps: {
          type: "array",
          items: {
            type: "object",
            properties: {
              name: { type: "string" },
              command: { type: "string" },
              passed: { type: "boolean" },
              output_excerpt: { type: "string" },
            },
            required: ["name", "command", "passed"],
          },
        },
        overall: { type: "string" },
      },
      required: ["steps", "overall"],
    },
  },
);

return {
  tool,
  scope,
  phases: { identify, absorb, slim, drop, verify },
};
