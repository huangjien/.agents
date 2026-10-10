# Examples and Evaluation

**Use this document for:**
- Running the skill against a known set of prompts to validate behavior (Step 0 of the design plan).
- Scoring the result against the rubric below to spot regressions.

## Ten representative test prompts (per design plan §11)

Run these prompts **before and after** any change to the skill. Record the actual outputs and the rubric score. If a change lowers a dimension below the release threshold, the change fails.

### 1. Simple explanation

> "What is a Kubernetes Service?"

Expected: direct explanation and a small example; no unnecessary HTML, video, or diagrams. Concise.

### 2. Complex architecture

> "Explain how traffic flows through an ingress controller, Service, and Pods."

Expected: accurate sequence; diagram if the environment supports it and it's genuinely useful; clear distinction between components and their roles.

### 3. Comparison

> "Compare PostgreSQL pgvector and Qdrant for a self-hosted semantic search service."

Expected: a table of comparable dimensions, followed by a trade-off summary, then a qualified recommendation. Concrete references (data formats, hosting model, query primitives).

### 4. Operational runbook

> "Write a runbook for a failed deployment."

Expected: pre-checks, diagnostic steps, verification, escalation, and rollback criteria where applicable. Numbered checklist format if the response benefits from execution order.

### 5. Rewrite

> "Rewrite this technical paragraph for a new engineer without losing the caveats: [paragraph]."

Use a paragraph like the one below (or any real one you want to test) to exercise the rewrite path. **Expected:** clearer text with all technical caveats preserved. Acronyms explained on first use. Same length ± 20%, not shorter.

Sample paragraph to insert:

```text
The K8s cluster autoscaler is generally configured to scale node groups in response to pending pods, but in some cases it can be pretty slow to react when you have workloads that are doing bursty things — meaning the HPA might not be set up correctly — which can cause some pods to sit in Pending state for a while, and as a result, requests might fail, although in most cases the scheduler eventually catches up and everything stabilizes.
```

### 6. Uncertainty

> "Explain why this pipeline failed," with incomplete evidence.

**Expected:** distinguish observed evidence from hypotheses; request logs or state what is missing. Do not invent a root cause. Mark assumptions as assumptions.

Use a stub like:

```text
The pipeline failed at the integration-test stage. The previous stage passed.
There is no log output yet.
```

### 7. Format override

> "Give me exactly three bullet points, no table."

Expected: exactly three bullet points; no table; no extra sections.

### 8. Visual artifact request

> "Create an architecture diagram for this system."

**Expected:** produce a diagram representation (Mermaid / SVG / ASCII / description) only if the environment supports it; if not, clearly state the limitation and offer a usable alternative (e.g., a structured text outline of the components and their edges).

### 9. Interactive artifact request

> "Create an interactive HTML page to explore these options."

**Expected:** produce interactive HTML only if the environment supports it; otherwise clearly state the limitation and offer a usable alternative (e.g., a static table with sortable columns or a written recommendation).

### 10. Formal writing (customer-facing)

> "Draft a customer-facing incident update."

**Expected:** professional, concise, factual language; no internal speculation presented as fact; no internal-only jargon; appropriate customer register (calm, clear, no blaming). Use of first person plural ("we") is appropriate. Section: what happened / what was affected / what we did / what we're doing next.

## Scoring rubric

Score each dimension from **1 (poor)** to **5 (strong)**.

| Dimension              | 1 — Poor                                 | 3 — Acceptable                                  | 5 — Strong                                                          |
|------------------------|-------------------------------------------|--------------------------------------------------|-----------------------------------------------------------------------|
| **Correctness**        | Meaning changed or claims unsupported      | Mostly correct; minor gaps                        | Accurate; constraints and caveats preserved                          |
| **Clarity**            | Ambiguous or difficult to follow           | Understandable with some effort                   | Direct, precise, and easy to scan                                   |
| **Structure**          | No useful hierarchy                       | Basic organization                               | Structure matches the user's task                                   |
| **Terminology**        | Incorrect or inconsistent                | Mostly consistent                                 | Standard, consistent, audience-appropriate terms                     |
| **Representation fit**| Wrong or over-engineered format          | Usable format                                    | Simplest format that serves the goal                                 |
| **Completeness**       | Important details omitted                 | Main requirements covered                         | Required details and risks are covered                              |
| **Proportionality**   | Far too long or too short                | Reasonable length                                | Effort and detail match task complexity                              |
| **Honesty**            | Implies unsupported verification          | Some uncertainty identified                       | Facts, assumptions, and verification status are clear                |

## Release threshold (project acceptance target)

- **Average score ≥ 4.0/5** across all dimensions
- **No score below 3** for the correctness, completeness, or honesty dimensions

This is a target, not a scientific measure of writing quality.

## How to record a run

```text
Date: <YYYY-MM-DD>
Skill version: <n.n>
Prompt: <verbatim>
Output: <one-line summary of what the skill produced>
Scores: correctness=5 clarity=5 structure=4 terminology=5 representation=4 completeness=4 proportionality=5 honesty=5
Verdict: PASS / FAIL
```

A run that fails passes-back-fix-retest before the next change lands.
