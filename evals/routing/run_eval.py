#!/usr/bin/env python3
"""Routing eval: route.yaml keyword matcher vs laya vs hybrid.

Usage: python3 evals/routing/run_eval.py [--laya] [--sweep]
Labels come from prompts.jsonl (human-labeled ground truth).
Writes report.md next to this script.
"""
import json, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).parent
HUB = HERE.parent.parent
sys.path.insert(0, str(HUB / "skills" / "_tools"))

INTENTS = ["laptop_administration", "software_maintenance", "debugging",
           "implementation", "review", "architecture", "testing",
           "documentation", "investigation"]

# --- keyword matcher: mirrors route.yaml rules -----------------------------
import re
import yaml
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

def kw_matched(prompt: str) -> bool:
    """True when a route trigger or the deterministic greeting check hit."""
    p = prompt.lower()
    for r in ROUTES:
        for ph in r["triggers"].get("phrases", []):
            if _hit(ph, p):
                return True
    for r in ROUTES:
        for kw in r["triggers"].get("keywords", []):
            if _hit(kw, p):
                return True
    return _is_greeting(prompt)

# --- laya ------------------------------------------------------------------
LAYA_URL = "http://127.0.0.1:8019/v1/systemone"
GATE_T = 0.5   # smalltalk noul threshold (eval-tuned; non-ST max 0.13)
CRITERIA = {
    "laptop_administration": "manage or configure this laptop, its tools, or agent clients",
    "software_maintenance": "maintain packages, CLIs, runtimes, toolchains",
    "debugging": "something is broken, failing, or erroring",
    "implementation": "build, write, create, or modify code",
    "review": "audit or check code for quality or security",
    "architecture": "system design, planning, tech decisions",
    "testing": "write tests or improve coverage",
    "documentation": "write docs, READMEs, technical prose",
    "investigation": "research, explain, understand, look into",
}
def laya_route(prompt: str):
    body = json.dumps({"state": {"message": prompt}, "questions": {
        "intent": {"type": "choice", "instructions": "What does the user want in `message`?",
                   "criteria": CRITERIA},
        "smalltalk": {"type": "noul",
                      "instructions": "Is `message` a greeting, identity question, or simple factoid?"}
    }}).encode()
    req = urllib.request.Request(LAYA_URL, body, {"Content-Type": "application/json"})
    a = json.loads(urllib.request.urlopen(req, timeout=30).read())["answers"]
    conf = a["intent"]["answer_confidence"]
    if a["smalltalk"]["noul"] >= GATE_T:
        return "smalltalk", conf
    return a["intent"]["choice"], conf

# --- metrics ---------------------------------------------------------------
def accuracy(preds, labels):
    ok = sum(p == l for p, l in zip(preds, labels))
    return ok, len(labels)

def main():
    data = [json.loads(l) for l in (HERE / "prompts.jsonl").read_text().splitlines() if l.strip()]
    labels = [d["label"] for d in data]

    kw = [keyword_route(d["prompt"]) for d in data]
    kw_ok, n = accuracy(kw, labels)

    laya_preds, confs = [], []
    for d in data:
        c, conf = laya_route(d["prompt"]); laya_preds.append(c); confs.append(conf)
    laya_ok, _ = accuracy(laya_preds, labels)

    lines = ["# Routing eval report", "",
             f"n={n} prompts ({sum(1 for d in data if d['source']=='real')} real / "
             f"{sum(1 for d in data if d['source']=='synthetic')} synthetic). "
             f"Labels: human judgment.", "",
             f"| Router | Accuracy |", "|---|---|",
             f"| route.yaml keywords | {kw_ok}/{n} ({100*kw_ok/n:.0f}%) |",
             f"| laya (no threshold) | {laya_ok}/{n} ({100*laya_ok/n:.0f}%) |"]

    lines += ["", "## Laya-first hybrid (rejected: worse than keywords alone)", "",
              "laya intent when confidence >= T, else keywords:", "",
              "| T | Accuracy |", "|---|---|"]
    best = (0, 0)
    for T in [0.4, 0.5, 0.6, 0.7, 0.8]:
        preds = ["smalltalk" if _is_greeting(d["prompt"]) or p == "smalltalk"
                 else (p if conf >= T else k)
                 for d, p, k, conf in zip(data, laya_preds, kw, confs)]
        ok, _ = accuracy(preds, labels)
        lines.append(f"| {T} | {ok}/{n} ({100*ok/n:.0f}%) |")
        if ok > best[1]: best = (T, ok)

    lines += ["", "## Keyword-first hybrid (production rule)", "",
              "Keyword router when a trigger or greeting matches; otherwise",
              "laya (smalltalk gate, then intent at `answer_confidence >= 0.5`);",
              "otherwise the keyword result stands (question-shortcut or", "general fallback).", ""]
    prod = [(p if (not kw_matched(d["prompt"]) and k != "smalltalk" and conf >= 0.5) else k)
            for d, p, k, conf in zip(data, laya_preds, kw, confs)]
    prod_ok, _ = accuracy(prod, labels)
    lines.append(f"Accuracy: {prod_ok}/{n} ({100*prod_ok/n:.0f}%)")

    lines += ["", "## Keyword-router errors", ""]
    for d, p, l in zip(data, kw, labels):
        if p != l: lines.append(f"- `{d['prompt'][:60]}` → kw={p}, truth={l}")
    lines += ["", "## Laya errors", ""]
    for d, p, l in zip(data, laya_preds, labels):
        if p != l: lines.append(f"- `{d['prompt'][:60]}` → laya={p}, truth={l}")

    lines += ["", f"Laya-first hybrid best: T={best[0]} ({best[1]}/{n}) — rejected.",
              f"Production rule: keyword-first with laya fallback ({prod_ok}/{n})."]
    (HERE / "report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:12])); print("...full report:", HERE / "report.md")

if __name__ == "__main__":
    main()
