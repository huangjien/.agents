# Skills 层去重候选 — 2026-10-16

> skills-first 重构（同日 notes/2026-10-16-skills-first-redesign.md）的副产物。
> 并入 ~2026-11-10 的 skill cull（见 notes/2026-10-13-skill-cull-candidates.md）。
> 本清单只记录，不执行。

## 强重复（合并候选）

| 组 | 成员 | 重叠点 | 建议 |
|---|---|---|---|
| 1 | `to-prd` / `to-spec` | 同一流程骨架，只差产物名（PRD vs spec） | 合并为一个 skill，产物类型做参数 |
| 2 | `to-issues` / `to-tickets` | tracer-bullet 垂直切片拆分，触发空间几乎相同 | 合并；`to-tickets` 的阻塞边保留为选项 |
| 3 | `deploy-to-vercel` / `vercel-cli-with-tokens` | 都触发 "deploy to vercel"，后者只窄化认证方式 | 按 token 可用性自动分流，或合并 |
| 4 | `ui-ux-pro-max` / `frontend-design` / `design-taste-frontend` | 第一个横跨全部 UI 触发词，与后两者三重叠加 | 收窄 `ui-ux-pro-max` 的 description，让三个各管一段 |

## 中度重叠（触发词收窄即可）

| 组 | 成员 | 说明 |
|---|---|---|
| 5 | `doc-coauthoring` / `clear-technical-communication` / `show-me` | CTC 的触发词伸进两者地盘；CTC 同时与 `writing-guidelines` 重叠 |
| 6 | `algorithmic-art` / `canvas-design` | 同一触发家族 + 相同的原创性条款，仅媒介不同（p5.js vs 静态图） |
| 7 | `brainstorming` / `grill-with-docs` | 真差异化（预设计 vs 压力测试），但竞争 "challenge my plan" 触发 |
| 8 | `skill-creator` / `skill-wiki` | "改现有 skill" vs "沉淀 pattern 成 skill 编辑"，边界模糊 |

## 触发词冲突（内容不重叠，路由有风险）

| 组 | 成员 | 说明 |
|---|---|---|
| 9 | `triage` / `laya-triage` | 完全不相关的两个领域共享 "triage" 一词 |

## 其他发现

- `ui-ux-pro-max/SKILL.md` 是 CRLF 行尾。`name:` 带隐形 `\r`，会导致
  name≠dir 的加载丢弃（PAT-20260906-skill-name-dir-mismatch 的隐形变体）。
  cull 时顺手转 LF 或直接退役。
