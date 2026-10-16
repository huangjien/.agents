---
name: system-design
description: Design systems and make technical decisions before implementation. Scoping gate, territory mapping, 2+ options with trade-offs, confidence-rated recommendation, step plan, vertical slice. Use when the user says "design", "how should I structure", asks for an architecture or approach, scope needs decomposition, a refactor touches multiple modules, or a tech-stack decision (library, pattern, schema) must be made.
metadata:
  author: local
  version: "1.0.0"
  last_reviewed: 2026-10-16
  source: ""
  local_only: true
---

# System Design

Produce plans and decisions, not implementation code. When you do write code, it's a sketch — a vertical slice to validate the design.

## Scoping gate

Before designing anything, ask these three questions. All three must get a yes. If any answer is no, stop. Fix the scope first: descope, split the project, or reject it. Only then produce a design.

1. **Can the product be described on one page?**
   If the pitch needs more than one page, the project is too complex.
   Do not build it as one project — split it.

2. **Can the core technology be separated from the product?**
   Products pivot constantly; core technology endures and keeps evolving.
   Separating the two forces you to think beyond the product itself.
   Example: a phone's core technology is mobile communication. A specific
   phone model can fail; mobile communication does not.

3. **Does the product have one signature feature?**
   One clear trait that gives the product a distinct personality.
   Examples: Minecraft — everything is made of blocks; IKEA — flat-packed,
   self-assembled furniture.

A failed question 1 means the brief needs decomposition before mapping. A failed question 2 or 3 shapes the options and recommendation.

## Workflow

### 1. Read the brief

Identify:
- **What** is being designed
- **Constraints** (existing code, perf budget, team skills, deadlines)
- **Stopping condition** (what deliverable ends the work)

### 2. Map the territory

Before proposing:
- Read the relevant existing code.
- Note current architecture, patterns, conventions.
- Identify dependencies and blast radius.

Never propose a design that ignores the existing system.

### 3. Generate 2+ options

For any non-trivial decision, present at least two options:
- Option A: usually the conservative / evolutionary choice
- Option B: usually the more ambitious / cleaner choice

For each option:
- **Trade-offs**: what you gain, what you lose
- **Cost**: rough effort estimate (S/M/L)
- **Risk**: what could go wrong

### 4. Recommend

Pick one and justify. State your confidence (high / medium / low).
If confidence is low, name what must be true for the recommendation to hold.

### 5. Produce the plan

If the user accepts, produce a step-by-step plan:
- Numbered steps, each with a clear deliverable
- Dependency order (what blocks what)
- Parallelization opportunities (what can run in parallel)
- Verification at each step

### 6. Identify a vertical slice

For any multi-step plan, identify the **thinnest end-to-end slice** that proves the design. Implement that first.

## Design heuristics

Standard requirement→solution heuristics. Apply them as starting points when mapping options — they are defaults, not mandates. Prefer generic terms over specific product names unless the stack dictates otherwise.

### Caching & content delivery

| Requirement | Consider |
|---|---|
| Data-intensive system | Caching |
| Low latency | Caching + CDN |
| Global data delivery | CDN |
| Cache eviction policy | LRU (least recently used) |

### Async processing & messaging

| Requirement | Consider |
|---|---|
| Write-heavy system | Message queue for async processing |
| Complex computation | Message queue + caching |
| Batch job processing | Batch processing + message queue |
| Fast user-to-user communication | WebSockets |

### Databases & storage

| Requirement | Consider |
|---|---|
| ACID guarantees (atomicity, consistency, isolation, durability) | RDBMS / SQL database |
| Unstructured data | NoSQL database |
| Large binaries (video, images, files) | Blob / object storage |
| Graph data (nodes, edges, relationships) | Graph database |
| Massive data search | Search index / search engine |
| Scaling a SQL database | Database sharding |
| High-performance database queries | Database indexes |
| Fault tolerance and durability | Data replication |
| Audit trails | Data lake |

### Scaling & availability

| Requirement | Consider |
|---|---|
| High availability, performance, throughput | Load balancer |
| Scaling any component | Horizontal scaling |
| Efficient server scaling | Consistent hashing |
| Single point of failure | Redundancy |
| Traffic spikes | Autoscaling |
| Availability-vs-consistency trade-off | Eventual consistency |

### Networking & communication

| Requirement | Consider |
|---|---|
| Server load management / DoS prevention | Rate limiter |
| Microservices architecture | API gateway |
| Failure detection in distributed systems | Heartbeats |
| Decentralized data transfer | Gossip protocol |
| IP resolution and domain lookup | DNS |
| Large data in network requests | Pagination |
| High-concurrency connections | Connection pooling; compact wire formats (e.g., Protobuf) |

### Data integrity & specialized patterns

| Requirement | Consider |
|---|---|
| Data integrity | Checksum algorithms |
| Location-based features | Quadtrees, geohash, etc. |

## Output template

```markdown
## Architecture: {title}

### Context
- {what's being designed}
- {key constraints}

### Options

#### Option A: {name}
- **Approach**: {one paragraph}
- **Trade-offs**: {gains} / {costs}
- **Cost**: {S/M/L}
- **Risk**: {what could break}

#### Option B: {name}
- **Approach**: {one paragraph}
- **Trade-offs**: {gains} / {costs}
- **Cost**: {S/M/L}
- **Risk**: {what could break}

### Recommendation: {A or B}
**Confidence**: {high/medium/low}
**Why**: {one paragraph}

### Plan
1. {step with deliverable}
2. {step with deliverable}

### Vertical slice (implement first)
{smallest end-to-end test of the design}
```
