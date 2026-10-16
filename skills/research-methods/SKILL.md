---
name: research-methods
description: Investigate, explain concepts, and look up current documentation with source discipline. Source-selection table, broad-then-narrow search, two-source verification, citation rules, and answer templates. Use when the user says "how does X work", "investigate", "look into", "find examples", wants to understand a library/framework/concept, or research is needed before acting.
metadata:
  author: local
  version: "1.0.0"
  last_reviewed: 2026-10-16
  source: ""
  local_only: true
---

# Research Methods

Find and synthesize. Don't dump everything you know — answer the specific question.

## Workflow

### 1. Understand the question

Rephrase the user's question in your own words. Identify:
- **What they want to know** (not what they literally asked — what they need)
- **Depth required** (quick answer vs deep dive)
- **Format wanted** (prose, code sample, comparison table, decision)

If the question is ambiguous, ask one clarifying question.

### 2. Pick your sources

| Need | Source |
|------|--------|
| Library / framework docs | Context7 MCP, or the tool's doc-lookup equivalent (always preferred over training data) |
| Current library versions / changelogs | Context7 or official docs |
| Code examples in real repos | GitHub code search (grep.app / `grep_app_searchGitHub`) |
| General concept / news / facts | Web search (`web_search_exa` or the tool's search equivalent) |
| Reading a specific URL | Web fetch (`web_fetch_exa` or the tool's fetch equivalent) |
| Code in THIS repo | Read / Glob / Grep |

**Always prefer current doc lookup over your training data for library APIs.** Your training data is stale; docs are current. Tool names above are the pi/OpenCode MCP names — use the equivalents available in the current tool.

### 3. Search broadly first, then narrow

- Start with one broad query
- Read 2-3 results to map the landscape
- Then run targeted queries for specifics

Do NOT fire 10 parallel searches when 2 sequential ones will do.

### 4. Verify

- If a source claims X, can you find a second source confirming X?
- For library APIs: does the doc match the version the user is on?
- For code patterns: is this from a recent, maintained repo?

If sources conflict, say so. Don't pick one to look authoritative.

### 5. Synthesize

Combine findings into a single coherent answer:
- Lead with the answer to the user's actual question
- Then context / caveats
- Then sources (cite every claim)

## Principles

- **Current > stale**: always check current docs for library APIs. Training data may be 6-12 months out of date. APIs change.
- **Cite everything**: every non-trivial claim links to a source. If you can't cite it, say "based on general knowledge" and tell the user to verify before relying on it.
- **Answer the question asked**: don't dump everything you know about a topic.
- **Distinguish fact from opinion**: "React 19 was released" — fact, cite it. "React 19 is better than Vue 3" — opinion, mark it as such.
- **Admit uncertainty**: "I don't know" is a valid answer. "I think X but haven't verified" is honest. Pretending certainty is the worst option.

## Answer templates

### Short answer (most cases)

```markdown
{direct answer to the question}

{2-3 sentences of context}

**Sources:**
- [{source title}]({url})
```

### Deep dive (when warranted)

```markdown
## {Topic}

### TL;DR
{one-paragraph answer}

### Detail
{explanation with code samples where useful}

### Trade-offs / caveats
{what to watch out for}

### Sources
- [{title}]({url}) — {what it contributed}
```

### Comparison

```markdown
## {A} vs {B}

| Dimension | {A} | {B} |
|-----------|-----|-----|
| {dim 1}   | ... | ... |
| {dim 2}   | ... | ... |

**Recommendation:** {for which use case}
```
