---
name: devops-platform-integration
description: Run standalone Python scripts that detect DevOps platform credential availability from env/.env, skip missing integrations with reasons, and generate a combined GitHub/Jenkins/Azure/Artifactory report.
metadata:
  author: local
  version: "1.0.0"
  last_reviewed: 2026-09-26
  source: internal://.agents/skills/devops-platform-integration
  local_only: true
---

# DevOps Platform Integration

## Scripts

- `scripts/platform_capabilities.py`: Inspect env/.env and output which platform integrations are enabled.
- `scripts/devops_report.py`: Generate a combined JSON report, running only enabled platform snapshots.
- `scripts/github_snapshot.py`: Fetch minimal GitHub account and rate limit info.
- `scripts/jenkins_snapshot.py`: Fetch minimal Jenkins server and job info.
- `scripts/jenkins_recent_failures.py`: List failed builds within a recent time window (optionally include logs).
- `scripts/azure_snapshot.py`: Fetch minimal Azure subscription info.
- `scripts/artifactory_snapshot.py`: Fetch minimal Artifactory connectivity/auth info.

## Usage

Run from the repository root:

```bash
python .agents/skills/devops-platform-integration/scripts/platform_capabilities.py
python .agents/skills/devops-platform-integration/scripts/devops_report.py
```

### Jenkins Logs (Optional)

Include a build log tail + lightweight keyword summary:

```bash
python .agents/skills/devops-platform-integration/scripts/jenkins_snapshot.py --include-logs --job "folder1/folder2/job-name" --build lastBuild
```

### Jenkins Recent Failures (Last 8 Hours)

```bash
python .agents/skills/devops-platform-integration/scripts/jenkins_recent_failures.py --hours 8 --max-results 50
```

Include log tails for each failure:

```bash
python .agents/skills/devops-platform-integration/scripts/jenkins_recent_failures.py --hours 8 --max-results 20 --include-logs
```

## Output Contract

All scripts return JSON and never echo secret values. If required env vars are missing, scripts return a `skipped` or `enabled: false` result with a human-readable `reason`.
