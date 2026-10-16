---
name: software-maintenance
description: Maintain local developer software — package managers, CLIs, runtimes, agent tools — with compatibility checks and rollback awareness. Use when the user says "upgrade", "update this tool", mentions brew/npm/pip global installs, version conflicts, or maintaining locally installed software.
metadata:
  author: local
  version: "1.0.0"
  last_reviewed: 2026-10-16
  source: ""
  local_only: true
---

# Software Maintenance

Maintain software installed on this laptop.

## Before changing

- Identify the tool, version, installation source, and owner.
- Check current configuration and dependent tools before upgrading.
- Prefer the existing package manager and project conventions.
- Avoid global upgrades when a project-local change is sufficient.

## During

- Preserve user configuration and uncommitted work.

## After

- Run the narrowest health check first, then a broader check when risk warrants it.
- State version changes and compatibility risks clearly.

Do not remove old versions or caches unless the user asks and the exact targets are known.
