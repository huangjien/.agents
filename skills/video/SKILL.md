---
name: video
description: Operate the AI Video Factory monorepo — a pnpm TypeScript pipeline that turns a topic into a 1080p Chinese MP4 via `video draft` and `video make`. Use when the user works in this repo, asks about `video` subcommands, needs to set up the environment, or wants to generate/research/script/storyboard/render/audit/publish a video.
metadata:
  author: local
  source: internal://~/workspace/ai-video-factory
  version: "1.1.0"
  last_reviewed: 2026-10-03
  local_only: true
---

# AI Video Factory

A pnpm TypeScript monorepo. Two human-edit files (`article.md`, `audio-config.yaml`) drive the pipeline; everything else is derived. Final output is a 1920×1080@30fps MP4 with narration + BGM + SFX.

**Trigger**: load this skill when the user is inside `~/workspace/ai-video-factory` (or any descendant), or mentions `video`, VDSL, storyboard, draft, make, shorts, or YouTube packaging.

## 1. Setup (run first if anything fails)

The repo provides a checker. Run it and act on each line:

```bash
bash ~/.agents/skills/video/scripts/check_setup.sh
```

It checks: Node ≥22, pnpm 12.5+, FFmpeg + ffprobe on PATH, the `video` binary resolvable, and `MINIMAX_API_KEY` set if not using `--fake`. Offer to install what's missing:

| Missing | Fix |
|---|---|
| Node | `brew install node` (mac) or `nvm install 22` |
| pnpm | `corepack enable && corepack prepare pnpm@12.5.1 --activate` |
| FFmpeg | `brew install ffmpeg` (mac) / `apt-get install ffmpeg` (linux) |
| `video` binary | Symlink `bin/video` into a PATH dir: `ln -sf ~/workspace/ai-video-factory/bin/video ~/.local/bin/video`. `bin/video` resolves the symlink via `realpath $0` so it works from any PATH location. |
| API key | export `MINIMAX_API_KEY=…` (or `GLM_API_KEY=…` for the LLM) |

### How `video` resolves

```
video                 ← from PATH (e.g. ~/.local/bin/video)
  └→ symlink to    ~/workspace/ai-video-factory/bin/video
      └→ exec      node ~/workspace/ai-video-factory/packages/cli/dist/index.js "$@"
```

The CLI source lives at `packages/cli/src/index.ts`. After `pnpm build`, the entrypoint is `node packages/cli/dist/index.js`. `bin/video` is a thin bash wrapper that resolves the real script path with `realpath $0` before computing the project root — **without that, calling `video` via a symlink breaks** (the wrapper used to use `dirname $0`, which is the symlink path, not the target).

## 2. Major commands

Minimal API (v0.3.9+ recommended) — two commands do the whole pipeline:

```bash
video draft "<topic>"   # LLM writes article.md + audio-config.yaml + derived storyboard.yaml
                        # quality gate: judge rates attractive/interesting/useful (0-10 each);
                        # below 25/30 the draft is regenerated with the judge's feedback
                        # (max 3 drafts, best wins) → article-review.yaml sidecar.
                        # Flags: --no-review, --min-score <n>, --max-attempts <n>
video make <project>    # TTS → audio assets → render scenes → mix → final-mixed.mp4
```

Full command set:

| Command | Purpose |
|---|---|
| `video new <id>` | Scaffold `projects/<id>/` |
| `video draft <topic>` | Generate `article.md` + `audio-config.yaml` + derived `storyboard.yaml` (LLM) |
| `video script <topic>` | Narration script only |
| `video storyboard <topic>` | VDSL storyboard only |
| `video audio-plan <project>` | Voice / BGM / SFX plan |
| `video audio <project>` | TTS narration |
| `video audio-asset <project>` | BGM + SFX |
| `video make <project>` | Full render: TTS → assets → scenes → mix → `final-mixed.mp4` |
| `video preview <project>` | Fast preview render |
| `video review <project>` | LLM review (content / visual / technical) |
| `video approve [stage] <project>` | Approve a stage |
| `video reject <project> <reason>` | Reject current stage |
| `video final <project>` | Final mixed MP4 with narration + BGM + SFX |
| `video validate <storyboard.yaml>` | VDSL schema check |
| `video status [project]` | Pipeline state |
| `video thumbnail <project>` | YouTube thumbnail (MiniMax image) |
| `video shorts <project>` | 60s Shorts clip (MiniMax video) |
| `video youtube <project>` | Title / description / chapters / shorts hook |

Every command accepts `--cwd <dir>` (default `projects/`). Every step writes `runs/<id>.yaml` and updates `state.yaml`.

### Visual components (v0.4.2 registry — 25 components)

`video make` re-derives `storyboard.yaml` from article.md on every run: each scene's `visual:` field is keyword-matched by a deterministic classifier (`packages/draft/src/visual-classifier.ts`), which picks a component and a prop builder fills structured props from caption/narration/prose. First scene is always Title. When editing article.md, steer visuals by putting trigger keywords in `visual:`:

| Trigger keywords in `visual:` (en / zh) | Component | Look |
|---|---|---|
| quote, 引用/名言/金句 | `QuoteBlock` | quote card + `——author` attribution |
| %, percent, 增长/百分比/统计 | `StatGrid` | big numbers with count-up |
| chart, distribution, 柱状图/分布 | `BarChart` | animated horizontal bars from `label: 40%` pairs |
| ranking, top-N, 排名/榜单/冠军 | `Leaderboard` | ranked rows, #1 lands last |
| checklist, 注意事项/避坑 | `Checklist` | check marks stroke on per item |
| key insight, takeaway, 核心观点/一句话 | `BigIdea` | full-screen statement, token reveal |
| pyramid, hierarchy, 金字塔/层级 | `PyramidDiagram` | layers drawn bottom-up |
| venn, overlap, 交集/重叠 | `VennDiagram` | 2-3 translucent circles |
| cycle, loop, 循环/闭环/飞轮 | `CycleDiagram` | stages on rotating ring |
| network, pipeline, 流程/步骤 | `SvgScene` | draw-on diagram |
| compare, vs, 对比/差异 | `Comparison` | left/right cards |
| code, terminal, 代码/命令行 | `Terminal` | typewriter listing |
| timeline, history, 历史/年表 | `Timeline` | events on a line |
| formula, 公式 / database, 数据库 | `Callout` | info/warning/success card |
| list, bullet, 列表/要点 | `Checklist` | item rows with stroke-on check marks (DoodleScene never auto-selected) |
| (no match) | `AnimatedIllustration` | generic shapes |

Renderers: `remotion` covers all classic components; `svg` → SvgScene; `canvas` → DoodleScene. New scenes need no YAML hand-editing — the storyboard regenerates, but hand edits to `storyboard.yaml` are overwritten by the next `video make` (article.md is the source of truth). One-off visual check of all components: `node scripts/render-visual-smoke.mjs` → stills in `.omo/tmp/visual-smoke/`. Branding smoke: `node scripts/render-brand-smoke.mjs` → `.omo/tmp/brand-smoke/`.

## 2.5 Branding & marketing (root `brand.yaml`)

Branding lives at the WORKSPACE root — `<repo>/brand.yaml` + `<repo>/assets/brand/*` — and EVERY project inherits it automatically at render time (preview / final / make). Override per project by dropping `projects/<id>/brand.yaml` (per top-level key; a project `intro:` replaces the root `intro:` wholesale). Paths resolve relative to the brand.yaml that declared them.

```yaml
# <repo>/brand.yaml  (shipped default: name "AI 视频工厂" + placeholder icon)
brand:
  name: "我的频道"              # shown in the intro band
  icon: assets/brand/icon.png   # corner watermark on EVERY scene (png/jpg/svg)
  corner: bottom-right          # top-left|top-right|bottom-left|bottom-right
  size_px: 72                   # at 1080p; scales with composition width
  opacity: 0.85
  intro:                        # fixed branded opening (omit = no intro chrome)
    duration_sec: 15            # 10-20s is the marketing norm
    background: aurora          # aurora|sunset|ocean|citrus
    show_name: true
```

Multi-BGM — different music for the opening vs the body, in `audio-config.yaml` (overrides `bgm`; `track` = named tag generated like `bgm`, or a file path resolved project-first then workspace-root — shared brand audio lives in `<repo>/assets/brand/`; `until_sec` = absolute window end, last entry runs to the end):

**BGM generation backends** (`video make <p> --music-provider auto|minimax|mock`, default `auto`): `auto` uses MiniMax music-01 generation when `MINIMAX_API_KEY` is set (original, license-clean beds; ~60s each, looped by the timeline), else silent mock; a failed generation degrades to mock with a warning. Named tags map to curated zh prompts in `MUSIC_PROMPTS` (`packages/audio-assets/src/minimax-music.ts`) — shipped: `calm`, `epic`, `guofeng`, `liubang-xiaodiao` (古风小调，琵琶竹笛，汉代气象)， `fanzhuan-march` (反转进行曲，由压抑到爆发). Unknown tags are passed to the API as free-text prompts verbatim (Chinese works). bgmDir library always wins over generation.

```yaml
bgm_tracks:
  - { track: calm, until_sec: 18 }   # branded opening mood
  - { track: epic }                  # rest of the video
```

Windows crossfade (1s) into one timeline wav (`assets/audio-assets/bgm/_timeline.wav`), then mix through the normal ducker/fades.

## 3. Canonical end-to-end

```bash
# 1. Scaffold
video new "transformer architectures"

# 2. Two human-edit checkpoints via LLM
video draft "transformer architectures"
#   → edit projects/.../article.md and projects/.../audio-config.yaml
#   article.md narrations drive scene visuals; audio-config.yaml drives voice/BGM/SFX

# 3. Render
video make transformer-architectures
#   writes output/final-mixed.mp4

# 4. (Optional) Publish
video youtube transformer-architectures
video thumbnail transformer-architectures
video shorts transformer-architectures
```

Idempotent: `video make` skips a step when its output is newer than its inputs. Use `--fake` to render without network / API calls (silent placeholder WAVs, no AI images).

## 4. Provider flags

- LLM: `--model minimax|glm` (default `glm` for draft, `minimax` for storyboard / youtube)
- Image / video: `--image-provider minimax|mock|none`, `--fake`
- TTS: `--fake` (offline placeholder)
- Web search in research: `--no-web` (LLM knowledge only)

Provider fallback (minimax → glm) is automatic on quota / rate-limit errors.

## 5. Package layout (monorepo)

```
packages/
├── cli               # the `video` command (entry: packages/cli/src/index.ts)
├── draft             # article.md + audio-config.yaml generation
├── script            # narration script generator
├── agent-storyboard  # VDSL storyboard agent
├── audio-plan        # voice/BGM/SFX planning
├── audio-assets      # BGM/SFX generator
├── audio-mix         # mix narration + BGM + SFX
├── tts               # TTS provider abstraction
├── vdsl              # VDSL schema (Zod)
├── video-components  # React/Remotion components
├── video-renderer    # Remotion render pipeline
├── media-generators  # image / video provider abstractions
├── llm               # minimax / glm provider clients
├── make              # make-command orchestrator
├── review            # review agent
├── research          # research agent + MiniMax web search
├── youtube           # YouTube package + thumbnail prompt + shorts hook
└── workflow          # pipeline state machine
```

`pnpm build` at the root compiles every package via `tsc -b`.

## 6. Common pitfalls

- **Keyless smoke run (no API keys needed)**: write `article.md` (frontmatter: project/language/duration_target_sec/voice + `## Scenes` fenced YAML) and an `audio-config.yaml` (`voice: zh-CN-XiaoxiaoNeural`, `bgm: "calm"`, `sfx: {scene_1: whoosh}` — flat keys, not nested objects), then `video approve storyboard <project>` (gate) and `video make <project> --fake`.
- **`no scene-N.wav files` in mix**: article scene ids must be `scene-1`, `scene-2`, … — TTS names narration WAVs after article ids and mix matches `/^scene[-_]\d+\.wav$/`. Ids like `s1` break the mix step.
- **`video` not found**: symlink `bin/video` into a PATH dir (see §1). Verify with `which video` and `realpath $(which video)`.
- **`Cannot find module '.../packages/cli/dist/index.js'`** — the `video` / `video` wrapper resolved the wrong project root. The bundled `bin/video` uses `realpath $0`, so this only happens with a custom wrapper that uses `dirname $0` or `$(pwd)`. Fix: either rebuild via `pnpm build`, or replace any custom wrapper with `bin/video`.
- **`MINIMAX_API_KEY` missing**: needed for real image / video generation; not needed for `--fake`.
- **`pnpm test` slow**: vitest runs across all packages with coverage. Use `pnpm vitest run packages/<name>` to scope.
- **Render stuck on port**: Remotion needs a free port; check `output/` for crash logs.
- **Storyboard schema mismatch**: `video validate projects/<id>/storyboard/storyboard.yaml --root projects/<id>`.
- **Edge TTS fails**: try `--fake` to confirm pipeline; fall back to a different voice via `audio-config.yaml`.
- **Disk usage**: `node_modules`, `output/`, and Remotion caches grow fast; `pnpm store prune` periodically.

## 7. More reading

- `README.md` — one-page overview
- `INSTALLATION_AND_USAGE.md` — full reference (commands, flags, troubleshooting)
- `ARCHITECTURE.md` — package boundaries and design decisions
- `RELEASES.md` — version history
- `AI_Video_Factory_Design_and_Plan_v1.1.md` — the design doc
