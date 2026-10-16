---
name: doc-templates
description: Write READMEs, API reference docs, and technical prose that match the project's existing voice. Audience identification, README/API-doc answer orders, and copy-paste templates. Use when the user says "document", "README", "API docs", "write docs", or existing docs are stale and need updating.
metadata:
  author: local
  version: "1.0.0"
  last_reviewed: 2026-10-16
  source: ""
  local_only: true
---

# Doc Templates

Write for the **reader who doesn't have your context** — the new dev, the future maintainer, the API consumer.

## Workflow

### 1. Identify the audience

Documentation is audience-dependent:

| Audience | Lead with | Avoid |
|----------|-----------|-------|
| New dev | "Get running in 5 minutes" | Internal architecture deep-dives |
| API consumer | Working code sample | Implementation details |
| Maintainer | "Why it's built this way" | Basic usage they already know |
| End user | The task they're trying to do | Internals |

The same feature may need docs for multiple audiences.

### 2. Read the code (or feature)

Read the actual implementation: public API surface, key types/interfaces, error cases, configuration options, side effects. Document what's there, not what you imagine.

### 3. Match existing voice

Read existing docs in the project: tone (formal / casual / terse), structure (headers, code blocks, callouts), naming conventions. Match it. Doc inconsistency is worse than no docs.

### 4. Write

Lead with the **smallest useful example**. Then expand.

A good README answers in this order:
1. **What** is this? (one sentence)
2. **Why** should I care? (one paragraph)
3. **How** do I use it? (smallest working example)
4. **What else** can it do? (advanced features)
5. **Where** do I go next? (links to detail)

A good API doc answers:
1. Signature (types, parameter names)
2. What it returns
3. What it throws
4. One example
5. Edge cases / gotchas

### 5. Verify

- Do the code examples actually run? (paste them into a REPL if possible)
- Are the types / signatures accurate to the current code?
- Are the links valid?

## Principles

- **Show, don't tell**: ❌ "The auth module handles authentication securely." ✅ "The auth module issues a JWT signed with HS256, valid for 1 hour, refreshed automatically via the /refresh endpoint."
- **Lead with the example**: code first, prose second. A reader who can copy-paste a working example is happier than one who has to read three paragraphs first.
- **Document the why, not the what**: the code already says what. Docs explain why this approach, why these trade-offs.
- **Update, don't accumulate**: when behavior changes, replace old docs. Don't append "NOTE: actually now we do X". Docs should read as if they were always correct.
- **No prose-only sections**: every section should have a code sample, a diagram, or a table.
- **No marketing language**: "powerful", "seamless", "robust" are banned. No emojis unless the project already uses them.

## Templates

### README section

```markdown
## {Feature name}

{One-sentence description}

### Quick start

\`\`\`{lang}
{smallest working example}
\`\`\`

### What it does

{2-3 sentences expanding on the one-liner}

### Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| ...    | ...  | ...     | ...         |

### Examples

{2-3 progressively more complex examples}

### See also

- [{Link}](url)
```

### API doc

```markdown
### `functionName(arg1: Type, arg2?: Type): ReturnType`

{One-sentence summary}

\`\`\`{lang}
{example}
\`\`\`

**Parameters:**
- `arg1` ({Type}): {description}
- `arg2` ({Type}, optional): {description}

**Returns:** {description}

**Throws:** {errors}

**Notes:** {gotchas}
```
