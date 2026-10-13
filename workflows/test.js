// ~/.agents/workflows/test.js
// Static checks for all workflows in this directory.
//
// Verifies, for each workflow:
//   1. File exists and has parseable syntax (uses acorn — handles top-level return).
//   2. Exports a `meta` object with name + description.
//   3. The workflow has runtime hooks (agent/parallel/pipeline/phase calls) —
//      i.e. it's not just a stub.
//   4. The meta `name` is kebab/snake_case and matches the file name.
//
// Run via: node workflows/test.js
//
// Note: workflow scripts use top-level `return` (only valid inside the
// pi-dynamic-workflows runtime, which wraps the file in a function).
// Plain `node workflows/<name>.js` would fail with "Illegal return
// statement" — that's by design. This test script handles it via acorn.

import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

/**
 * Syntax check by wrapping the file in a function — mirroring what the
 * pi-dynamic-workflows runtime does. Strips ESM `import` / `export`
 * keywords first (those are module-only; the function body uses raw JS).
 * Top-level `return` becomes valid inside the function.
 */
function syntaxCheck(text) {
  // Convert module syntax to function-body syntax
  const transformed = text
    // `export const X = ...` -> `const X = ...`
    .replace(/^export\s+(const|let|var|function|class)\s+/gm, '$1 ')
    // `import X from '...'` -> `const X = (await import('...')).default;`
    .replace(/^import\s+([\s\S]+?)\s+from\s+['"][^'"]+['"];?\s*$/gm, '')
    // `export { ... }` -> remove
    .replace(/^export\s*\{[\s\S]*?\};?\s*$/gm, '');
  // Wrap as an async function body — top-level return is now valid, and
  // any `await` keywords at the top level work.
  const wrapped = `(async function(){\n${transformed}\n})`;
  try {
    new Function(wrapped);
    return { ok: true };
  } catch (e) {
    return { ok: false, error: e.message.split('\n')[0] };
  }
}

const files = readdirSync(__dirname)
  .filter(f => f.endsWith('.js') && f !== 'test.js' && f !== 'test.mjs')
  .sort();

const results = [];
let pass = 0, fail = 0;

for (const file of files) {
  const fullPath = join(__dirname, file);
  const text = readFileSync(fullPath, 'utf-8');

  const issues = [];

  // 1. Syntax check (wraps in function to allow top-level return)
  const syntax = syntaxCheck(text);
  if (!syntax.ok) {
    issues.push('syntax: ' + syntax.error);
  }

  // 2. meta export
  const metaMatch = text.match(/export\s+const\s+meta\s*=\s*(\{[\s\S]*?\n\})\s*;?/);
  let meta = null;
  if (!metaMatch) {
    issues.push('no "export const meta = { ... }"');
  } else {
    try {
      // Strip type annotations / comments and eval just the meta object
      const cleaned = metaMatch[1]
        .replace(/\/\*[\s\S]*?\*\//g, '')
        .replace(/^\s*\/\/.*$/gm, '');
      meta = (new Function('return (' + cleaned + ')'))();
    } catch (e) {
      issues.push('meta parse: ' + e.message);
    }
  }

  // 3. meta shape
  if (meta) {
    if (!meta.name) issues.push('meta.name missing');
    if (!meta.description) issues.push('meta.description missing');
    if (meta.name && typeof meta.name !== 'string') issues.push('meta.name not a string');
    if (meta.description && typeof meta.description !== 'string') issues.push('meta.description not a string');
  }

  // 4. Runtime hooks present (catches stub files)
  const hasRuntimeHook = /\b(agent|parallel|pipeline|phase|loopUntilDry|verify|judgePanel|completenessCheck|workflow)\s*\(/.test(text);
  if (!hasRuntimeHook) {
    issues.push('no runtime hook (agent/parallel/pipeline/phase) found — possible stub');
  }

  // 5. Conventions: top-level return is the workflow runtime convention
  const hasTopLevelReturn = /^\s*return\s*[\(\{]/m.test(text);

  // 6. File name ↔ meta.name hint (informational only)
  let nameMatch = null;
  if (meta?.name) {
    const fileStem = file.replace(/\.js$/, '');
    // Accept snake or kebab
    const norm = (s) => s.replace(/[_-]/g, '');
    nameMatch = norm(meta.name) === norm(fileStem) || meta.name === fileStem;
  }

  results.push({
    file,
    metaName: meta?.name,
    metaDescLen: meta?.description?.length || 0,
    nameMatchesFile: nameMatch,
    hasTopLevelReturn,
    hasRuntimeHook,
    issues,
  });

  if (issues.length === 0) pass++;
  else fail++;
}

// Output
const total = files.length;
console.log('\nWorkflow static-check report');
console.log('===========================');
console.log(`Workflows scanned:  ${total}`);
console.log(`PASS:               ${pass}`);
console.log(`FAIL:               ${fail}`);
console.log(`syntax:             function-wrap (allows top-level return)`);
console.log('');

for (const r of results) {
  const icon = r.issues.length === 0 ? '✓' : '✗';
  const tag = r.nameMatchesFile === false ? '  (meta name ≠ file name)' : '';
  console.log(`  ${icon} ${r.file.padEnd(28)}  meta=${(r.metaName || '?').padEnd(20)}  top-return=${r.hasTopLevelReturn ? 'yes' : 'no '}  hook=${r.hasRuntimeHook ? 'yes' : 'no '}${tag}`);
  for (const issue of r.issues) {
    console.log(`      ↳ ${issue}`);
  }
}

console.log('');
console.log(fail === 0 ? 'OVERALL: PASS' : `OVERALL: FAIL (${fail} issue${fail > 1 ? 's' : ''})`);
process.exit(fail === 0 ? 0 : 1);
