# Eval results — 2026-10-10

Actual Copilot CLI runs of the 10 §11 test prompts. Outputs captured from
`copilot -p "<prompt>" --silent` against the skill at
`~/.agents/skills/clear-technical-communication/`.

## How the run was done

- **Tool:** `copilot` (GitHub Copilot CLI) — non-interactive (`-p`).
- **Skill discovery:** `copilot skill list` shows the
  `clear-technical-communication` skill under "Inherited skills" (Personal
  scope, `~/.copilot/skills/`). The CLI is therefore a valid test bed for
  the skill's behavior.
- **Skill engagement evidence:** indirect. The CLI does not surface which
  skills were invoked; engagement is inferred from the output style
  (lead-with-the-answer, structured prose, table for comparison, Mermaid
  for diagrams, etc.) being consistent with the skill's process.
- **Self-assessment disclaimer:** the scorer is the same agent that ran
  the prompts. Scoring is honest per the rubric, but treat it as
  self-graded. An independent second pair of eyes is recommended before
  marking the skill fully "ready for normal use" (Phase 4 P4-05).
- **Captured raw outputs:** see `/tmp/ctc-eval/*.txt` (10 files) and
  excerpts below.

## Rubric reference

Score each dimension 1 (poor) to 5 (strong). **Release threshold:** average
≥ 4.0/5, with no score below 3 on correctness, completeness, or honesty.

| Dimension | Notes |
|---|---|
| Correctness | Did simplification change meaning? Are claims supported? |
| Clarity | Are actors, actions, conditions, outcomes clear? |
| Structure | Hierarchy that matches the user's task? |
| Terminology | Standard, consistent, audience-appropriate? |
| Representation fit | Simplest format that serves the goal? |
| Completeness | Constraints, risks, caveats preserved? |
| Proportionality | Length matches complexity? |
| Honesty | Facts, assumptions, verification status clear? |

## Per-prompt results

### P1 — Simple explanation: "What is a Kubernetes Service?"

**Output (truncated):** A Kubernetes Service gives a stable network
address for a set of Pods. Because Pods can be replaced and their IP
addresses can change, other applications connect to the Service instead
of tracking individual Pods. A Service selects matching Pods and routes
network traffic to them. Common types include ClusterIP, NodePort, and
LoadBalancer.

| Dimension | Score | Comment |
|---|---|---|
| Correctness | 5 | Accurate; stable-IP concept correctly explained |
| Clarity | 5 | Direct, two short paragraphs |
| Structure | 4 | No headings (fine for a short response) |
| Terminology | 5 | ClusterIP/NodePort/LoadBalancer named correctly |
| Representation fit | 5 | Short prose, no diagram or table needed |
| Completeness | 4 | Covers what, why, types; no usage example |
| Proportionality | 5 | Concise, appropriate |
| Honesty | 5 | No unsupported claims |

**Average: 4.75 / 5. PASS.**

### P2 — Complex architecture: ingress / Service / Pods

**Output excerpt:** A typical request flows like this: … (ASCII diagram
showing Client → DNS → Cloud LB → Ingress controller → Service → Pod).
The Ingress resource defines routing rules. The Ingress controller
watches those rules. The Service provides a stable address and selects
Pods. Ingress adds external HTTP/HTTPS routing; it does not replace the
Service or run the application.

| Dimension | Score | Comment |
|---|---|---|
| Correctness | 5 | Mentions EndpointSlices, kube-proxy, TLS termination — accurate |
| Clarity | 4 | ASCII diagram plus prose; clear but could be tighter |
| Structure | 5 | Diagram then prose; clean |
| Terminology | 4 | EndpointSlices and kube-proxy mentioned without expansion; OK for the audience |
| Representation fit | 5 | ASCII diagram is the right call for a CLI env |
| Completeness | 5 | Walks the full flow, distinguishes Ingress resource vs controller, mentions internal-only paths |
| Proportionality | 4 | A bit longer than minimum |
| Honesty | 5 | No fabrication |

**Average: 4.625 / 5. PASS.**

### P3 — Comparison: pgvector vs Qdrant

**Output excerpt:** Choose pgvector if PostgreSQL is already your
system of record. Choose Qdrant if vector retrieval is the main service
… (7-row comparison table covering what/best fit/filtering/search/ops/
scaling/trade-off). Practical starting point. **Do not decide on a
record-count cutoff alone.** References at the end.

| Dimension | Score | Comment |
|---|---|---|
| Correctness | 5 | Mentions HNSW/IVFFlat, payload filtering caveats, hybrid search |
| Clarity | 5 | TL;DR at the top, table, conclusion, references |
| Structure | 5 | Lead with the decision rule, then table, then recommendation |
| Terminology | 5 | HNSW, IVFFlat, dense/sparse, payload — standard terms |
| Representation fit | 5 | Table is the right call |
| Completeness | 5 | 7 dimensions + recommendation + reference links |
| Proportionality | 5 | Dense but not bloated |
| Honesty | 5 | "Do not decide on a record-count cutoff alone. Benchmark both." |

**Average: 5.0 / 5. PASS.**

### P4 — Operational runbook: failed Kubernetes deployment

**Output excerpt:** 6 sections: Assess impact, Capture deployment
state, Diagnose, Restore service, Verify recovery, Escalate and record.
Includes a signal → likely cause → next-checks table and rollback
commands. Note about not rolling back blindly when DB schema or
external deps changed.

| Dimension | Score | Comment |
|---|---|---|
| Correctness | 5 | Valid kubectl commands; signals and causes correct |
| Clarity | 5 | Numbered steps, table of common signals |
| Structure | 5 | 6 numbered sections with subsections; signal table |
| Terminology | 5 | CrashLoopBackOff, ImagePullBackOff, OOMKilled — all correct |
| Representation fit | 5 | Numbered checklist + table + code blocks |
| Completeness | 5 | Pre-checks, diagnosis, restore, verify, escalate — all present |
| Proportionality | 5 | Long but appropriate for a runbook |
| Honesty | 5 | "Do not roll back blindly when a release changed a database schema" |

**Average: 5.0 / 5. PASS.**

### P5 — Rewrite: simplify a technical paragraph

**Input (paraphrased):** "K8s autoscaler is configured to scale node
groups in response to pending pods, but in some cases it can be slow
to react when you have bursty workloads — meaning the HPA might not be
set up correctly — which can cause some pods to sit in Pending state
for a while, and as a result, requests might fail, although in most
cases the scheduler eventually catches up and everything stabilizes."

**Output:** "For a new engineer, the key point is this: Kubernetes
usually scales node groups automatically when pods are waiting to run,
but that scaling can be delayed when workloads spike suddenly or when
the HPA is not configured correctly. In those cases, some pods may
stay in a Pending state longer than expected. If a request depends on
one of those pods starting, it can fail or time out before the cluster
catches up. The autoscaler and scheduler often recover on their own,
and the cluster usually stabilizes after a short delay, but this lag
is a real operational caveat and can affect bursty or time-sensitive
workloads."

| Dimension | Score | Comment |
|---|---|---|
| Correctness | 5 | All original caveats preserved: pending pods, HPA misconfig, requests failing, eventual recovery, bursty caveat |
| Clarity | 4 | Much clearer than input; "may stay in a Pending state longer than expected" is a good turn |
| Structure | 4 | Single paragraph, but the paragraph has clear sentence-by-sentence logic |
| Terminology | 5 | "K8s" → "Kubernetes" on first use |
| Representation fit | 5 | Prose is right |
| Completeness | 5 | All caveats preserved |
| Proportionality | 4 | Original 1 sentence → 4 sentences; longer than ±20% but the input was unparseable; net win |
| Honesty | 5 | "may", "often" preserved |

**Average: 4.625 / 5. PASS.**

### P6 — Uncertainty: explain why a pipeline failed (no logs)

**Output excerpt:** "There isn't enough evidence to identify the
cause. A passing previous stage only shows that the pipeline reached
integration tests; it doesn't reveal whether the failure came from a
test assertion, service setup, dependency, or timeout. … The next
useful evidence is the integration-test job's exit code and logs …
Without those, naming a root cause would be guesswork."

| Dimension | Score | Comment |
|---|---|---|
| Correctness | 5 | Does not invent a cause |
| Clarity | 5 | Direct |
| Structure | 4 | Two paragraphs |
| Terminology | 5 | Standard |
| Representation fit | 5 | Prose only — appropriate |
| Completeness | 5 | Names what's missing (test logs, config, artifacts) |
| Proportionality | 5 | Tight |
| Honesty | 5 | "naming a root cause would be guesswork" |

**Average: 4.875 / 5. PASS.**

### P7 — Format override: "exactly three bullet points, no table"

**Output:**
- Forward a local port to a pod with `kubectl port-forward pod/<pod-name> <local-port>:<pod-port>`; example given.
- You can target other resources like `deployment/<name>` or `service/<name>`; add `-n <namespace>` if needed.
- Keep the command running; press **Ctrl+C** to stop forwarding.

| Dimension | Score | Comment |
|---|---|---|
| Correctness | 5 | Accurate kubectl port-forward usage |
| Clarity | 5 | Direct |
| Structure | 5 | Exactly three bullets, no table |
| Terminology | 5 | Correct |
| Representation fit | 5 | Bullets, no table |
| Completeness | 5 | Three concrete bullets with example |
| Proportionality | 5 | Tight |
| Honesty | 5 | Factual |

**Average: 5.0 / 5. PASS.**

### P8 — Visual artifact: "create an architecture diagram"

**Output:** Mermaid `flowchart LR` showing Client → API Gateway → Auth
Service → User DB / Cache / Message Queue → Background Workers, with
12 numbered steps. One-line explanation of cache-miss behavior.

| Dimension | Score | Comment |
|---|---|---|
| Correctness | 5 | Mermaid syntax is valid; flow is reasonable |
| Clarity | 5 | Diagram + one explanatory line |
| Structure | 4 | Code block + line of prose |
| Terminology | 5 | Standard |
| Representation fit | 5 | Mermaid is the right call for CLI env |
| Completeness | 5 | All 6 components + data flow + cache-miss path |
| Proportionality | 5 | Tight |
| Honesty | 5 | No overstatement |

**Average: 4.875 / 5. PASS.**

### P9 — Interactive artifact: "create an interactive HTML page"

**Output:** Did not produce the page. Asked a clarifying question
instead: "Which comparison layout do you prefer? 1. Filterable cards,
2. Side-by-side table, 3. Score plot." Said it would build the page
after the user chose.

| Dimension | Score | Comment |
|---|---|---|
| Correctness | 4 | The clarifying question is per the skill's process step 1 ("ask ONE focused question"); but it did not also offer a "usable alternative" (table, recommendation) per §11 expected behavior |
| Clarity | 4 | Clear that three layouts are being offered |
| Structure | 4 | Numbered list |
| Terminology | 4 | "low / medium / high" labels proposed |
| Representation fit | 4 | Asked for clarification, did not fabricate HTML |
| Completeness | 3 | Did not deliver a usable alternative (e.g., a static table with sortable columns or a written recommendation) as §11 expected |
| Proportionality | 5 | Short |
| Honesty | 5 | Did not pretend to create HTML |

**Average: 4.125 / 5. BORDERLINE — completeness score 3 is at threshold.**

**Note:** the response is consistent with the skill's process (clarify
before producing a large artifact), but the §11 test prompt's expected
behavior includes "offer a usable alternative". Future improvement:
when asking a clarifying question for a large artifact, also produce a
small usable alternative inline (a 3-row table, a one-paragraph
recommendation). Easy to add to the skill's process step 5 or to
references/representation-selection.md.

### P10 — Formal customer-facing incident update

**Output:** "Incident update — October 10, 2026. Our API was
unavailable for 18 minutes, from 14:00 to 14:18 UTC. A deployment at
13:55 UTC caused the database connection pool to become exhausted. We
rolled back the deployment at 14:12 UTC, and service recovered by
14:18 UTC. No data was lost. We are adding a database connection-pool
pre-flight check to our deployment pipeline to help prevent this issue
from recurring."

| Dimension | Score | Comment |
|---|---|---|
| Correctness | 5 | All facts from the prompt are in the output, in order |
| Clarity | 5 | Calm, direct |
| Structure | 4 | Single paragraph with bold heading; works for an email blast |
| Terminology | 5 | Customer-appropriate; no internal jargon |
| Representation fit | 5 | Short prose with bold heading |
| Completeness | 5 | What / when / cause / fix / prevention |
| Proportionality | 5 | Concise |
| Honesty | 5 | Factual, no speculation |

**Average: 4.875 / 5. PASS.**

## Aggregate across all 10 prompts

| Dimension | Average across 10 |
|---|---|
| Correctness | 4.9 |
| Clarity | 4.7 |
| Structure | 4.5 |
| Terminology | 4.7 |
| Representation fit | 4.8 |
| Completeness | 4.7 |
| Proportionality | 4.8 |
| Honesty | 5.0 |
| **Grand average** | **4.76 / 5** |

## Release-threshold check

- **Average ≥ 4.0/5:** ✅ 4.76
- **No score < 3 on correctness, completeness, or honesty:** ✅
  - Correctness min: 4 (P9)
  - Completeness min: 3 (P9 — at threshold, not below)
  - Honesty min: 5 (all)
- **P0 issues remaining:** one borderline (P9 completeness, score 3) — the
  skill asked for clarification rather than producing a usable
  alternative. **Not a P0 blocker;** release may proceed. Improvement
  noted above.

## Verdict

**PASS.** The skill behaves per the design plan across the 10 §11 test
prompts. Release gate (P4-05) is met at the self-assessment level. An
independent second-scorer is recommended before promoting to "ready for
normal use" in the wiki index.
