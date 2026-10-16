# Skills-first 重构 — 2026-10-16

> 人工读的设计记录。动机、数据、映射表、阶段与回滚。

## 为什么

Anthropic 的 skills-first 方向（Agent Skills，2025-10-16 发布，progressive disclosure ~100 token）验证了一件事：**skills 是知识注入原语，agents 是上下文隔离原语**。本 hub 的 agents-first 架构把两类问题都交给了 spawn。

数据（2026-10-16 审计，7 个 subagent 文件）：

- 平均 ~70% 是领域知识（应该按需加载），~14% 与 AGENTS.md Part 1/2 重复（政策已有家），~21% 才是派生执行逻辑。
- tier hints（architect=expensive 等）从未生效 —— 全部 `model: inherit`。
- 流程知识已被 skills 覆盖（diagnose/code-review/tdd/doc-coauthoring），缺 15 项表格/清单类硬知识。
- Copilot Major 已有 "optionally attach a skill" 步骤 —— 一半已是 skills-first。

## 决策

1. spawn 角色只留 2 个：researcher（隔离噪音大的搜索）、reviewer（无锚定新上下文验证）。其余 7 个退役。
2. 派发规则：默认加载 skill 就地执行；仅当满足 spawn 条件才派生（新上下文验证 / 大范围扇出搜索 / 用户点名）。
3. STYLE.md "Agents first" 原则不动 —— 它讲的是工件服务 agent 读者，与派发机制无关。

## 迁移映射

| 原角色 | 知识去处 | 政策去处 |
|---|---|---|
| debugger | `diagnose`（+调查技术表、认知偏差表、症状问询、无结论模板） | AGENTS.md 既有 |
| reviewer | `code-review`（+严重度阶梯、verdict 协议、安全/正确性/类型/测试基线、评审原则）；spawn 壳保留 | 同上 |
| tester | `tdd`（+what-to-test 矩阵、约定、金字塔、no-slop） | 同上 |
| architect | 新 `system-design`（scoping gate、2+ 方案、设计启发式表、模板） | 同上 |
| doc-writer | 新 `doc-templates`（受众矩阵、README/API 顺序、模板） | 同上 |
| coder | 类型安全禁令 → STYLE.md Patterns；其余为政策重复 | 同上 |
| researcher | 新 `research-methods`（信源表、两源验证、引用纪律）；spawn 壳保留 | 同上 |
| laptop-admin | 新 `laptop-admin`（运维程序、破坏性操作流程） | 同上 |
| software-maintainer | 新 `software-maintenance`（升级纪律） | 同上 |

## 阶段

1. **P1 知识抽取**（纯增量）：3 扩 5 新 + STYLE.md 一条 + 两壳瘦身。
2. **P2 路由切换**：route.yaml v2（`dispatch.skill` + `spawn_when`）、两个 major.md、AGENTS.md Part 3/4/5、laya-decisions.md 措辞。eval 57/57 必须保持。
3. **P3 退役**：删 5 个 subagent 文件 + 2 个 portable 角色，install.sh 收缩，重跑验证 symlink。
4. **P4 清单**：skills 层重复对写入 notes，并入 ~2026-11-10 cull。

## 回滚

每阶段独立变更集，`git revert` 整体回退。P1 完全可独立回退（纯新增文件）。

## intent → skill 映射（P2 生效）

debugging→diagnose、testing→tdd、documentation→doc-templates、implementation→karpathy-engineer、architecture→system-design、review→code-review（新上下文验证时 spawn reviewer）、investigation→research-methods（大范围搜索时 spawn researcher）、laptop_administration→laptop-admin、software_maintenance→software-maintenance。
