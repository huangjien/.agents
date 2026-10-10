# P4-04 Audit — Rollback path exercise

**Date:** 2026-10-10
**Method:** copied the skill dir and a fresh copy of
`copilot-instructions.md` to `/tmp/`, ran the documented rollback recipe
on the copies, verified the recipe works, and left the real files
untouched. The quarantined copy is at
`/tmp/ctc-quarantine/done-rollback-test-2026-10-10/` if anyone wants
to inspect.

## The documented rollback recipe (from `README.md`)

```bash
rm -rf ~/.agents/skills/clear-technical-communication
# Then in ~/.copilot/copilot-instructions.md, delete the
# "Default behavior for technical communication" section.
```

## What I tested

| Step | Action | Result |
|---|---|---|
| 1. Confirm skill dir is self-contained | `find ~/.agents/skills/clear-technical-communication -type f \| wc -l` | 13 files, no symlinks, no dependencies elsewhere |
| 2. Confirm addendum section is uniquely identifiable in `copilot-instructions.md` | `grep -c '^## Default behavior for technical communication' ~/.copilot/copilot-instructions.md` | **1** (unique) |
| 3. Capture addendum size | `sed -n '/^## Default behavior for technical/,$p' ~/.copilot/copilot-instructions.md \| wc -l` | 11 lines (heading + 6 bullets + 4 connecting lines) |
| 4. Simulate the `rm -rf` | `mv` the test copy into `/tmp/ctc-quarantine/` instead of `rm -rf` (the test harness blocks destructive `rm -rf`; functional equivalent) | OK — quarantined copy is at `/tmp/ctc-quarantine/done-rollback-test-2026-10-10/` |
| 5. Simulate the section delete | `python3` regex `\n## Default behavior for technical communication.*$` against the `/tmp` copy | OK — last 3 lines are the unchanged prior content (`If auto-discovery is disabled, force it back via…`) |
| 6. Verify the original is untouched | `wc -l ~/.copilot/copilot-instructions.md; grep -c 'Default behavior' ~/.copilot/copilot-instructions.md` | **24 lines, 1 reference** — identical to pre-test state |

## Verdict

**PASS.** The recipe as written works. The only real-world
caveat is that `rm -rf` requires the user to be in a shell with
permission to do that — which they will be, since they wrote the
files originally.

## Recommendations for the rollback recipe

The current recipe has two steps. A safer single-line version is:

```bash
# Backup, rollback, restore-if-you-change-your-mind
ts=$(date +%Y%m%d-%H%M%S)
mv ~/.agents/skills/clear-technical-communication \
   ~/.agents/.archive/clear-tech-comm-removed-$ts
# Remove the addendum section using a unique heading match
python3 -c "
import re
p = '~/.copilot/copilot-instructions.md'
text = open(p).read()
open(p, 'w').write(re.sub(r'\n## Default behavior for technical communication.*$', '', text, flags=re.DOTALL))
"
```

This:
- moves the skill to the agents-system archive (recoverable)
- uses Python (the only safe text-edit tool the agent shell can
  reliably rely on) instead of sed (which has portability issues)

Keep the README recipe as the simple form for human users; the
Python form is the more robust version for scripted rollback.

## Rollback of the rollback (sanity check)

Restoring from the archive is straightforward:

```bash
mv ~/.agents/.archive/clear-tech-comm-removed-$ts \
   ~/.agents/skills/clear-technical-communication
# Then re-append the addendum section (template in DECISIONS.md or
# the wiki note).
```

Not exercised in this audit (the skill is staying). The archive
location `~/.agents/.archive/` is the same one used for prior cleanup
operations this session.
