# Template: Incident Report

> **Use when:** the user asks to "write a postmortem", "incident report",
> "what happened during the outage", or "write a runbook for a failed
> deployment". Adapt voice for audience (internal vs customer-facing).

---

## Summary

One paragraph. What broke, when, who was affected, what the user-visible
impact was, what the resolution was. Time and timezone. Audience
appropriate (a customer-facing update avoids internal jargon).

## Timeline

A list of timestamps (or table) for events that mattered. Relative
offsets ("+0:00", "+0:08", "+1:30") help readers who weren't there.

| Time (+offset) | Event | Owner / Actor |
|---|---|---|
| 2026-10-10 14:00 (+0:00) | <event> | <who> |
| | | |

## What broke

What was the failure mode, in plain language? Why was the user-visible
impact the shape it was?

## Why it broke — root cause

The mechanism, not the symptom. Distinguish what was directly broken
from what caused the direct failure (often upstream).

## Detection

- How was the issue first noticed? (alert, user report, monitoring)
- Time from first symptom to detection (TTD).
- Time from detection to mitigation start (TTM).

## Mitigation and resolution

- Short-term fix (what restored service).
- Long-term fix (the change that prevents recurrence).
- By whom, when.

## Customer or user impact

- Scope: who, how many, which systems.
- Duration: from first symptom to full restoration.
- Data integrity: any data lost, corrupted, or exposed (and to whom).

## What we learned

Three to five bullets. Concrete and actionable, not generic platitudes.
Mix of:
- what worked well (reinforced)
- what worked but slowly (could be faster)
- what didn't work (gap to close)

## Action items

| ID | Action | Owner | Severity | Due |
|---|---|---|---|---|
| | | | High / Med / Low | YYYY-MM-DD |

Each action item should be reviewable as done: specific person, scope of
work, verifiable completion criteria. Mark items that are blocked
(action: <blocker>; due: —) so they don't get lost.

## Followups

Anything that needs a separate document, ADR, or change to monitoring —
note it here so this report stays self-contained but the trail is clear.
