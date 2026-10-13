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
import yaml
route = yaml.safe_load((HUB / "route.yaml").read_text())
ROUTES = sorted(route["routes"], key=lambda r: -r.get("priority", 0))
SUBAGENT_IDS = {a["id"] for a in route["subagents"]}

def keyword_route(prompt: str) -> str:
    words = prompt.split()
    for r in ROUTES:
        for kw in r["triggers"].get("keywords", []):
            if kw.lower() in prompt.lower():
                return r["intent"]
        for ph in r["triggers"].get("phrases", []):
            if ph.lower() in prompt.lower():
                return r["intent"]
    if len(words) < 10:
        return "smalltalk"          # simple_shortcut rule
    return route["fallback"]["intent"]  # "general" -> researcher

# --- laya ------------------------------------------------------------------
LAYA_URL = "http://127.0.0.1:8019/v1/systemone"
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
    if a["smalltalk"]["noul"] >= 0.8:
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

    lines += ["", "## Hybrid sweep (laya when confidence >= T, else keywords)", "",
              "| T | Accuracy |", "|---|---|"]
    best = (0, 0)
    for T in [0.4, 0.5, 0.6, 0.7, 0.8]:
        preds = ["smalltalk" if p == "smalltalk" else (p if conf >= T else k)
                 for p, k, conf in zip(laya_preds, kw, confs)]
        ok, _ = accuracy(preds, labels)
        lines.append(f"| {T} | {ok}/{n} ({100*ok/n:.0f}%) |")
        if ok > best[1]: best = (T, ok)

    lines += ["", "## Keyword-router errors", ""]
    for d, p, l in zip(data, kw, labels):
        if p != l: lines.append(f"- `{d['prompt'][:60]}` → kw={p}, truth={l}")
    lines += ["", "## Laya errors", ""]
    for d, p, l in zip(data, laya_preds, labels):
        if p != l: lines.append(f"- `{d['prompt'][:60]}` → laya={p}, truth={l}")

    lines += ["", f"Best hybrid threshold: T={best[0]} ({best[1]}/{n})"]
    (HERE / "report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:12])); print("...full report:", HERE / "report.md")

if __name__ == "__main__":
    main()
