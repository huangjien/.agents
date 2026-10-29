#!/usr/bin/env python3
"""Routing eval: route.yaml keyword matcher accuracy.

Usage: python3 evals/routing/run_eval.py
Labels come from prompts.jsonl (human-labeled ground truth).
Writes report.md next to this script.
"""
import json
import re
from pathlib import Path

import yaml

HERE = Path(__file__).parent
HUB = HERE.parent.parent

INTENTS = ["laptop_administration", "software_maintenance", "debugging",
           "implementation", "review", "architecture", "testing",
           "documentation", "investigation"]

# --- keyword matcher: mirrors route.yaml rules -----------------------------
route = yaml.safe_load((HUB / "route.yaml").read_text())
ROUTES = sorted(route["routes"], key=lambda r: -r.get("priority", 0))

GREETINGS = {"hi", "hey", "hello", "yo", "sup", "thanks", "thank", "thx",
             "bye", "goodbye", "cheers"}
IDENTITY_PHRASES = ["who are you", "what can you do"]
QUESTION_STARTERS = ("what", "why", "how", "where", "which", "who", "when",
                     "is", "are", "do", "does", "can")

def _hit(trigger: str, prompt_lower: str) -> bool:
    return re.search(r"\b" + re.escape(trigger.lower()) + r"\b",
                     prompt_lower) is not None

def _first_word(prompt: str) -> str:
    return prompt.split()[0].lower().strip(",.!?'\"") if prompt.split() else ""

def _is_greeting(prompt: str) -> bool:
    return (_first_word(prompt) in GREETINGS
            or any(ph in prompt.lower() for ph in IDENTITY_PHRASES))

def keyword_route(prompt: str) -> str:
    p = prompt.lower()
    words = prompt.split()
    # phrase tier beats keyword tier; within a tier, priority wins (ROUTES
    # is pre-sorted by descending priority)
    for r in ROUTES:
        for ph in r["triggers"].get("phrases", []):
            if _hit(ph, p):
                return r["intent"]
    for r in ROUTES:
        for kw in r["triggers"].get("keywords", []):
            if _hit(kw, p):
                return r["intent"]
    if _is_greeting(prompt):
        return "smalltalk"
    if len(words) < 10:
        # simple_shortcut: question-shaped shorts are investigations
        question = "?" in prompt or _first_word(prompt) in QUESTION_STARTERS
        return "investigation" if question else "smalltalk"
    return route["fallback"]["intent"]  # "general" -> researcher

# --- metrics ---------------------------------------------------------------
def accuracy(preds, labels):
    ok = sum(p == lab for p, lab in zip(preds, labels))
    return ok, len(labels)

def main():
    raw = (HERE / "prompts.jsonl").read_text().splitlines()
    data = [json.loads(line) for line in raw if line.strip()]
    labels = [d["label"] for d in data]

    kw = [keyword_route(d["prompt"]) for d in data]
    kw_ok, n = accuracy(kw, labels)

    n_real = sum(1 for d in data if d["source"] == "real")
    n_syn = n - n_real
    lines = ["# Routing eval report", "",
             f"n={n} prompts ({n_real} real / {n_syn} synthetic). "
             "Labels: human judgment.", "",
             "| Router | Accuracy |", "|---|---|",
             f"| route.yaml keywords | {kw_ok}/{n} ({100 * kw_ok / n:.0f}%) |"]

    lines += ["", "## Keyword-router errors", ""]
    for d, p, lab in zip(data, kw, labels):
        if p != lab:
            lines.append(f"- `{d['prompt'][:60]}` → kw={p}, truth={lab}")

    lines += ["", f"Keyword-router accuracy: {kw_ok}/{n} ({100 * kw_ok / n:.0f}%)."]
    (HERE / "report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:12]))
    print("...full report:", HERE / "report.md")

if __name__ == "__main__":
    main()
