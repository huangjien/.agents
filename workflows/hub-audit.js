// ~/.agents/workflows/hub-audit.js
// 5-axis audit of the agents system, run in parallel.
// Each axis is a separate agent call; the workflow cross-validates
// and returns a structured report.
//
// Args:
//   scope: string (default "~/.agents/") — root of the install
//   checks: string[] (default = all 5) — which axes to run
//
// Returns:
//   { scope, axes, total_issues, by_severity, ledger }

export const meta = {
  name: "hub_audit",
  description:
    "Run the 5-axis hub audit on ~/.agents/ in parallel: tool registry consistency, post-retirement paths, role consistency, skill loader, MCP shared-docs.",
  phases: [{ title: "Setup" }, { title: "Audit (parallel)" }, { title: "Cross-validate" }],
};

const ALL_CHECKS = [
  {
    id: "tool-registry-consistency",
    label: "audit:tool-registry",
    prompt:
      "Verify tool names are consistent across these 5 files in ~/.agents/:\n" +
      "  - install.sh\n" +
      "  - AGENTS.md Part 4 (Tool Integration table)\n" +
      "  - README.md (Tool-specific behavior table)\n" +
      "  - adapters/README.md (Adapter policy)\n" +
      "  - route.yaml (header comment)\n\n" +
      "Expected tools: OpenCode, Codex, pi, VSCode+Copilot, Gemini.\n" +
      "Forbidden: Claude (retired 2026-10).\n\n" +
      "Read each file with grep and report any inconsistency. Return JSON array of issues: " +
      '[{id, severity: "high"|"med"|"low", file, line, finding}]. ' +
      "Empty array if clean.",
    schema: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          severity: { type: "string" },
          file: { type: "string" },
          line: { type: "integer" },
          finding: { type: "string" },
        },
        required: ["id", "severity", "file", "finding"],
      },
    },
  },
  {
    id: "post-retirement-paths",
    label: "audit:post-retirement",
    prompt:
      "Scan ~/.agents/ for active references to retired tools. The retired tools are Trae (deleted 2026-09) and Claude (deleted 2026-10). " +
      "Look for paths like ~/.trae/ or ~/.claude/ and for the literal strings 'Trae' or 'Claude' that are NOT in intentional historical record.\n\n" +
      "Exclude (these are intentional historical record, do NOT flag):\n" +
      "  - ~/.agents/wiki/notes/*\n" +
      "  - ~/.agents/wiki/index.md\n" +
      "  - ~/.agents/wiki/logs.md\n" +
      "  - ~/.agents/.archive/*\n" +
      "  - __pycache__/ directories\n" +
      "  - ~/.agents/skills/claude-api/ (the Claude API SDK skill, not Claude Desktop)\n\n" +
      "Return JSON array: [{file, line, context}] of active refs that should be flagged.",
    schema: {
      type: "array",
      items: {
        type: "object",
        properties: {
          file: { type: "string" },
          line: { type: "integer" },
          context: { type: "string" },
        },
        required: ["file", "context"],
      },
    },
  },
  {
    id: "role-consistency",
    label: "audit:role-consistency",
    prompt:
      "Verify all 9 roles mentioned in ~/.agents/AGENTS.md Part 3 (The nine subagents) have corresponding files on disk:\n" +
      "  - Standard 7: architect, coder, debugger, reviewer, researcher, tester, doc-writer\n" +
      "  - Portable 2: laptop-admin, software-maintainer\n\n" +
      "Files should live in ~/.agents/opencode/subagent/ (for the 7 standard) or ~/.agents/agents/ (for the 2 portable). " +
      "Also verify ~/.agents/route.yaml lists all 9 under subagents:.\n\n" +
      "Return JSON array of issues: [{role, severity, file, finding}]. " +
      "Empty if all 9 are present everywhere they should be.",
    schema: {
      type: "array",
      items: {
        type: "object",
        properties: {
          role: { type: "string" },
          severity: { type: "string" },
          file: { type: "string" },
          finding: { type: "string" },
        },
        required: ["role", "finding"],
      },
    },
  },
  {
    id: "skill-loader-readiness",
    label: "audit:skill-loader",
    prompt:
      "Walk ~/.agents/skills/*/. For each directory containing SKILL.md:\n" +
      "  1. Parse the YAML frontmatter.\n" +
      "  2. Extract the 'name:' field value (strip quotes/whitespace).\n" +
      "  3. Compare byte-for-byte to the parent directory basename.\n" +
      "  4. If they differ, that's a rename-drift (the dir was renamed but frontmatter wasn't updated). " +
      "Per PAT-20261010-skill-renamer-broke-frontmatter, VS Code Agent Skills loader drops mismatches silently.\n\n" +
      "Also check that 'description:' is non-empty and has trigger phrases.\n\n" +
      "Return JSON: [{skill, dir, frontmatter_name, mismatch, finding}]. " +
      "Empty array if all skills pass.",
    schema: {
      type: "array",
      items: {
        type: "object",
        properties: {
          skill: { type: "string" },
          dir: { type: "string" },
          frontmatter_name: { type: "string" },
          mismatch: { type: "boolean" },
          finding: { type: "string" },
        },
        required: ["skill", "dir", "frontmatter_name", "mismatch"],
      },
    },
  },
  {
    id: "mcp-shared-docs-integrity",
    label: "audit:mcp-shared-docs",
    prompt:
      "Verify the project-level MCP shared docs in ~/.agents/mcp/:\n" +
      "  - Each *.md file has well-formed YAML frontmatter (with applyTo: and description:).\n" +
      "  - Tool-native docs reference it where appropriate: ~/.codex/AGENTS.md, ~/.gemini/GEMINI.md, ~/.copilot/copilot-instructions.md should mention ~/.agents/mcp/ when there's content there.\n\n" +
      "Return JSON: [{file, finding}] of any unresolved path, missing frontmatter, or stale reference. Empty if clean.",
    schema: {
      type: "array",
      items: {
        type: "object",
        properties: {
          file: { type: "string" },
          finding: { type: "string" },
        },
        required: ["file", "finding"],
      },
    },
  },
];

phase("Setup");
const scope = args && typeof args.scope === "string" ? args.scope : "~/.agents/";
const requested = args && Array.isArray(args.checks) ? args.checks : null;
const checks = requested
  ? ALL_CHECKS.filter((c) => requested.includes(c.id))
  : ALL_CHECKS;
if (checks.length === 0) {
  return { error: "no checks to run", requested, available: ALL_CHECKS.map((c) => c.id) };
}

phase("Audit (parallel)");
const results = await parallel(
  checks.map((check) => () =>
    agent(
      `[scope=${scope}] ${check.prompt}`,
      { label: check.label, schema: check.schema },
    ),
  ),
);

// Preserve every result identity before parsing — failed runs show up as null
const ledger = checks.map((check, i) => ({
  id: check.id,
  status: results[i] === null ? "failed" : "complete",
  result: results[i],
}));

phase("Cross-validate");
const by_severity = { high: 0, med: 0, low: 0 };
let total_issues = 0;
for (const entry of ledger) {
  if (entry.status !== "complete") continue;
  const issues = Array.isArray(entry.result) ? entry.result : [];
  for (const issue of issues) {
    const sev = (issue && issue.severity) || "low";
    by_severity[sev] = (by_severity[sev] || 0) + 1;
    total_issues += 1;
  }
}

return {
  scope,
  axes: ledger,
  total_issues,
  by_severity,
  verdict: total_issues === 0 ? "CLEAN" : `${total_issues} issues across ${ledger.filter((l) => l.status === "complete").length} axes`,
};
