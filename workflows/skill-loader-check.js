// ~/.agents/workflows/skill-loader-check.js
// Single-axis check: walk ~/.agents/skills/*/ and verify each SKILL.md has
// parseable YAML frontmatter with `name:` byte-identical to the parent dir.
// Implements the verification from PAT-20261010-skill-renamer-broke-frontmatter.
//
// Args:
//   skillsDir: string (default "~/.agents/skills/")
//
// Returns:
//   { skills_dir, total, mismatches, parse_errors, results: [...] }

export const meta = {
  name: "skill_loader_check",
  description:
    "Walk ~/.agents/skills/*/SKILL.md and verify frontmatter 'name:' is byte-identical to the parent dir name. Catches the rename-drift pattern from PAT-20261010-skill-renamer-broke-frontmatter before it silently breaks VS Code Agent Skills loading.",
  phases: [{ title: "Scan" }, { title: "Verify" }, { title: "Report" }],
};

phase("Setup");
const skillsDir = args && typeof args.skillsDir === "string" ? args.skillsDir : "~/.agents/skills/";

phase("Scan");
const scan = await agent(
  `Walk every directory under ${skillsDir} that contains a SKILL.md file. For each skill:\n` +
    `  1. Read the SKILL.md file.\n` +
    `  2. Parse the YAML frontmatter (between the first '---' markers).\n` +
    `  3. Extract the 'name:' field value (strip any surrounding quotes and whitespace).\n` +
    `  4. Compare byte-for-byte to the parent directory basename.\n` +
    `  5. If they differ, that's a mismatch (the dir was renamed but frontmatter wasn't updated). Per PAT-20261010-skill-renamer-broke-frontmatter, VS Code Agent Skills loader drops mismatches silently.\n` +
    `  6. Also check that 'description:' is non-empty (must have at least one sentence; not just whitespace).\n` +
    `  7. Catch any YAML parse errors separately.\n\n` +
    `Return JSON: {\n` +
    `  "total": <int>,\n` +
    `  "mismatches": [{skill, dir, frontmatter_name, finding}],\n` +
    `  "missing_description": [{skill, finding}],\n` +
    `  "parse_errors": [{skill, finding}]\n` +
    `}`,
  {
    label: "skill-loader:scan",
    schema: {
      type: "object",
      properties: {
        total: { type: "integer" },
        mismatches: {
          type: "array",
          items: {
            type: "object",
            properties: {
              skill: { type: "string" },
              dir: { type: "string" },
              frontmatter_name: { type: "string" },
              finding: { type: "string" },
            },
            required: ["skill", "dir", "frontmatter_name"],
          },
        },
        missing_description: {
          type: "array",
          items: {
            type: "object",
            properties: {
              skill: { type: "string" },
              finding: { type: "string" },
            },
            required: ["skill", "finding"],
          },
        },
        parse_errors: {
          type: "array",
          items: {
            type: "object",
            properties: {
              skill: { type: "string" },
              finding: { type: "string" },
            },
            required: ["skill", "finding"],
          },
        },
      },
      required: ["total", "mismatches", "missing_description", "parse_errors"],
    },
  },
);

phase("Verify");
const m = (scan && Array.isArray(scan.mismatches) ? scan.mismatches : []);
const md = (scan && Array.isArray(scan.missing_description) ? scan.missing_description : []);
const pe = (scan && Array.isArray(scan.parse_errors) ? scan.parse_errors : []);
const total_issues = m.length + md.length + pe.length;

phase("Report");
return {
  skills_dir: skillsDir,
  total: (scan && Number.isInteger(scan.total)) ? scan.total : 0,
  mismatches: m,
  missing_description: md,
  parse_errors: pe,
  total_issues,
  verdict: total_issues === 0 ? "CLEAN" : `${total_issues} issues found`,
};
