# pstack 24 条工程原则 — 2026-10-18

> 学习笔记。来源：`cursor/plugins` @ `0b8e952`（2026-10-18），`pstack/plugin.json`
> version `0.15.26`。本地副本 `/tmp/pstack-src/pstack`（sparse clone）。
> 目的：**只学规则，不装他们的 skills**。
>
> 权威文件：`pstack/skills/principle-*/SKILL.md`（24 个）、
> `pstack/skills/poteto-mode/SKILL.md`、`pstack/docs/guide/08-principles.md`。

## 为什么要看它

poteto（React core team，Cursor）针对"AI 写太多 slop code"的答案。核心主张：
**少写代码、提高正确性、用显式原则 + 验证让并行 agent 变得可靠**。
对 hub 的价值不在任何单条原则，而在三件事的组合：

1. **决策前置于编码**（foundational thinking / attack the premise / subtract）
2. **agent 工作可审计**（playbook + 显式验证 + decision trail）
3. **重复错误变成强制手段**（encode lessons in structure / build the lever）

## 核心机制（不在任何二手总结里）

`/poteto-mode` 每次多步任务先读 24 条原则的索引，按任务触发应用，并强制：

1. **不用"调用"原则，用原则名"steer"。** 一个短语比一段指令更精确地改变方向。
2. **回复必须点名原则 + 它改变的那个决定。**
   > "A principle citation with no decision behind it means the agent named the
   > rule without applying it."

这条是反装饰检查 —— 防止 agent 撒原则名装严谨。

## 24 条原则

### Core —— 造多少、何时重想设计

| 原则 | 规则要点 | 硬性检查 |
|---|---|---|
| **Laziness Protocol** | 偏向删除与最小改动。两个牙齿：consolidate decisions（同一决定别在多处重复；收敛到单一 source of truth，传一个 flag）、minimize the diff | fewer lines beat "elegant" boilerplate |
| **Foundational Thinking** | 结构决策保护 option value，代码级决策保护简洁。数据结构先于逻辑。DRY the structure, not every line —— 三句相似语句胜过过早抽象 | 并发推论：共享状态前问"另一个 actor 并发改它会怎样"，答案不是"无事"就隔离。Scaffold first（CI/lint/test infra/共享类型）。**减法先于搭脚手架** |
| **Redesign from First Principles** | 新需求不要 bolt 到既有设计上。问"如果从零写且包含这个需求，会建什么？"然后传播到每个引用：types/docs/examples/rationale | 想完整重构，增量交付 |
| **Attack the Premise** | 两个以上修复共享同一前提且都倒在同一个 gate 上 → 怀疑前提，不是修复。把前提写成一句话，找一个"前提为假时结果会不同"的观察并去做。**看失败如何分布，不只是失败多大** | **stop rule**：前提没写下并验证前，不准开始下一个修复。推论 —— **移除条件而不是补偿它**；善后机制把原因留在原地，每次运行都多付代价 |
| **Subtract Before You Add** | 先删死代码/冗余 validator/stub 引用，再在更简单的底座上建。Sequence removal before construction。Cut before you polish | 按 observed usage 设计，不为假想 edge case 加 speculative validator。引用无新内容就删，别留 stub |
| **Minimize Reader Load** | 可维护性 = 读者要做的理解工作。两条独立轴：layers to trace + state to hold。LOC / cyclomatic / "clean architecture" 都是代理指标 | 收缩作用域顺序：纯函数 → locals → fields → module state → globals。**测试**：新读者能否在 30 秒内答出 "X 从哪来" 和 "什么能改 X"？ |
| **Outcome-Oriented Execution** | 有显式 phase 边界的重写/迁移，向目标架构收敛。保持每步稳定会造出变成长期债的临时兼容层 | Guardrail：声明哪里允许临时破损；迁移中在被触及区域保留高信号检查；计划完成时要求完整静态+运行时验证 |
| **Experience First** | 实现便利与用户愉悦冲突时选愉悦。Ship less, ship better。Prototype before committing（设计决策在 disposable HTML 里比在生产代码里便宜）。细节：transitions/alignment/spacing/feedback/error states | **"用户"是消费这份工作的人** —— UI 是终端用户；library 是导入它的同事；下一个维护代码的工程师也是用户。三者同等权衡，并从他们的视角陈述影响。基础决定 *sequence*，本原则决定 *target* |
| **Exhaust the Design Space** | 无先例的新交互/架构决策，先建 2–3 个竞争原型再比较 | 注意：线上 `principle-exhaust-the-design-space/SKILL.md` 只有两行 stub，实体内容在 guide 与 `arena` skill 里 |
| **Build the Lever** | 非 trivial 工作就构建"做它或证明它"的工具（codemod/script/generator/delegate skill），不要手工做 | "Hand-done changes can only be re-verified by redoing them." 确定性 lever 优于扇出：脚本能一遍处理完就自己跑，不要派 delegate 手工做。流程：手工做第一个 unit 学配方 → 建工具 → 重跑该 unit 与手工版 diff 自证 → 让工具可安全重跑。**引用了它而 diff 里没有 codemod/script/generator/delegate skill，就是没应用。** 门槛是 triviality 而非重复度 |

### Architecture —— 状态、校验、兼容放哪

| 原则 | 规则要点 | 硬性检查 |
|---|---|---|
| **Model the Domain** | 把领域编码进结构，让非法状态不可表示、branch 消失。首选：state machine 取代散落的 boolean/phase；typed model 取代散参数；map/registry/discriminated union 取代跨文件分支；reducer/command/event model 取代临时状态变更；**围绕一份领域知识组织模块，而不是 load→validate→transform→save 这种序列（"execution order is not ownership"）** | 别强行抽象：形状已经清晰、本地、不太会长，就用 boring code。**跳过它的迹象**：新功能让既有 if/else 又多一个分支；或出现第二个必须与第一个同步的 boolean |
| **Boundary Discipline** | 校验、类型收窄、错误处理放系统边界（CLI args/config/external API/network）。内部无条件信任，业务逻辑放纯函数，shell 薄且机械 | 分散的校验 = 噪音 + 冗余 + **虚假的安全感**。边界已校验则深层调用链不做冗余 nil check。跨边界暴露领域概念，不暴露边界的私有表示 |
| **Type System Discipline** | 让编译器拒绝不可能状态。Brand 语义原始类型（`UserId` / `OrderId` 底层都是 string 但不可互换；创建时校验一次，下游信任类型）。**外部数据在 parse 之前都是无类型的**：RPC payload / JSON / IPC / CLI args / config / env var / DB row 各有边界 parse 函数。从权威 schema 派生类型（protobuf / OpenAPI / GraphQL / migration / design token），不要手搓平行类型 | — |
| **Make Operations Idempotent** | 每步从**已存在的状态**派生，不从"上次运行想做什么"派生。读当前状态、比目标、只应用差量。任何运行遗留物（lock/temp file/半写记录/claimed job）必须能被下次运行识别为 stale，且判据要在**上次可能停下的任何位置**都为真 | **三个测试**：连跑两次会怎样；上次在每个可能点崩了会怎样；重跑是否收敛到同一终态。任何答案是"取决于留下了什么状态"就需要 reconciliation step。做法：写临时路径再 rename 就位；按内容而非创建顺序比较产物 |
| **Migrate Callers Then Delete Legacy APIs** | 迁移调用方与删除旧 API 在同一波完成，不留兼容层。测试改为断言新契约，删掉只保护重构前实现细节的测试 | **适用条件**：无外部用户依赖向后兼容；项目能吸收协同 breaking change；新 API 属于简化/重构计划。有外部消费者时这条是错的 |
| **Separate Before Serializing Shared State** | 并发 actor 可能写同一文件/branch/key/object 时，先问是否真的需要同一个可变对象。不需要就消除共享 | **"我们需要一把锁"是设计坏味道，不是默认答案** —— 指令和约定不是并发控制。例子：两个 worker 各写自己的 `lastX` 字段进同一个 `state.json` **仍然是共享可变**；`indexer-state.json` + `metrics-state.json` 不是。仅当单写目标是真不变量时才结构性串行化：lockfile / 顺序 phase / single-writer / atomic CAS |

### Verification —— 什么算证明

| 原则 | 规则要点 | 硬性检查 |
|---|---|---|
| **Prove It Works** | 对真实 artifact 验证，不用 proxy、自述或"it compiles"。直接查进程存活，不通过派生状态查；读真实值，不读缓存表示。**验证失败时先怀疑观测方法，再怀疑被观测的系统。** 能写脚本就写 —— 最强的证明是可重跑同一比较的确定性脚本，输出留作 reviewer 可重跑的 artifact | 只在大规模/复杂工作（port、migration）需要可审计轨迹时 commit 该 artifact |
| **Fix Root Causes** | 修故障，不修症状浮现的地方。每步问 why 直到答案是**代码里的错误决定**而不是前一个答案的后果。卡住就 instrument，读真实 error 与真实 state | **判别问题：触发症状的状态本身合法吗？** 系统可能合法处于该状态 → 在那里处理它**就是**修复。该状态不该存在 → 在断点处加检查是在藏 bug，去找是什么产生了它。藏 bug 的常规手段：guard、retry、吞异常、clamp、丢弃状态。**只在重启后复现 → 先怀疑持久化状态**：config / cache / lock file / 序列化状态。查模式而非只查这一个实例。**workaround 需要一段话注释才能自圆其说 → 代码错了。** 决定性事实若要深挖才找到，就提出那个 always-on 的廉价信号 |
| **Sequence Work into Verifiable Units** | 每小 unit 结束在一个可检查的状态，当前 unit 不绿就不推进。先 rebase 到干净 trunk，让每次 check 对着真基线测。lever 做编辑时 unit check 近乎免费 —— **但照样跑** | 交付顺序：canonical 形状是 failing test 在前、fix 在后。其它有效序：subtraction 在 reshape 前、baseline capture 在 treatment 前、scaffold 在 feature 前。每个 commit 独立落地，序列本身读起来就是一个论证 |
| **Test Behavior, Not Implementation** | Behavior = 用户通过其使用的接口能观察到的东西（返回值、错误、可读回的状态、对系统外的影响：发出了请求、写了行、发了消息）。Implementation = 观察不到的（私有 helper、内部调用序、哪个协作者干的活） | **用两个想象中的编辑判断每个测试**：(a) *破坏行为* —— 返回错值、跳过效果、做两次；测试仍过 = 什么都没证明（常见原因：断言比契约松、期望值由被测代码算出、复述的常量或 prompt 字符串从未执行读它的代码）。(b) *改内部实现* —— 可观察结果不变只重构底层；测试此时失败 = 钉死在实现上。**留下能抓住第一个编辑、扛过第二个编辑的测试。** 细粒度判定：mock 外部服务收到的 payload **是** behavior；空列表在无匹配记录时是精确答案、在只需要某个结果时是空心检查；精确的 error message 钉死了没人读的措辞，而调用方分支依赖的 error **类型**才是契约 |
| **Explain the Number** | 在信任、报告或依据一个测得的数字（speedup / regression / throughput / latency / eval 结果）行动**之前**：问 **"why not double?"**，说出限制它的资源或代码路径（core、lock、磁盘、网络、压测器本身）。从 profile 或运行中的系统计数器拿到，再映射回源码 —— **读代码猜出来的不是 limiter**。然后列出这个数字还可能在测什么，逐个用证据排除：error、被跳过或缓存的工作、根本没跑的代码、一侧没调优、噪声、小到对端到端无影响的小块。**说不出为什么不是两倍好，就不知道你测的是什么** | 把 run count、离散度、limiter 跟数字放在一起（notes 或链接 artifact）。跳过它的信号：数字背后没有 run count、没有离散度、没有具名 limiter；或节省的时间大于被改部分自身耗时 |

### Delegation —— 让并行保持理智

| 原则 | 规则要点 |
|---|---|
| **Guard the Context Window** | 上下文溢出会降低推理质量、产生压缩伪影、卡住进度。大块阅读派给 subagent，主线程只留摘要。给 phase 定尺寸、封顶 scope：限制每 phase 文件数、设 turn 预算、计入机制开销 |
| **Never Block on the Human** | 人是异步监督的。做合理决策、推进、让人事后纠偏。代码改动可逆可 review，**做错的代价通常小于阻塞**。Proceed, then present。发现问题就记日志、下一轮修。不可逆动作（force-push、删生产数据、发外部消息）仍需确认。**产品方向来自人，执行不该阻塞** |

### Meta —— 唯一会复利的那条

**Encode Lessons in Structure** —— 发现自己第二次写同一条指令时，把它编码成 lint rule、metadata flag、runtime check 或脚本，而不是更多文字。

- **Corollary**：如果修复是结构性的，**只用**结构性修复；那条指令是症状。
- 若某条教训确实需要判断、无法编码，就把指令放得更显著，并附一个失败模式的例子。
- 落地：`/correct` 把这条应用到整个 repo。

## 非原则机制里值得抄的

**Autonomy。** 可逆动作（含外部动作：群消息、ticket 更新、启动 eval）"just do it"。**Always pause**：force-push 到共享 branch、deploy、删数据、发客户消息。Session override："don't stop" / "going to bed" / "run until done" / "be fully autonomous"。**"No" 是合法答案** —— 推荐是判断不是确认，同意不是默认，candor 优先于谄媚。

**别问那些"跑一下就能知道"的问题。** 遇到 "which approach / how should I / what should this do" 分叉先分类：如果答案是跑点什么就能观察到的（behaviour、timing、layout、output、perf，甚至某个 eval 是否能区分），那不是人该答的 —— 用 Prototype playbook 画个 sketch 让结果决定。只有**没有任何实验能定夺的产品/偏好决策**才问。在自治授权下，覆盖到的决策自己定、自己做、自己报告，不回一个字、不做 offer；只有 operator 能定的调用 default、完整解释地报告，并用平实语言说明 operator 可以改 telling you what 怎么做 —— **operator 用自己的话回答，绝不给 shorthand token 让用户敲回来**。

**Subagent 默认值。** `run_in_background: true`（readonly 会剥掉 MCP）。**默认给全新的 subagent + 合并过的 scope**：原始 brief、后续所有指令、前一个 agent 的报告与 branch。fix 轮、follow-up、retry、队列下一项都算。只有新工作严格需要活在那个 agent 里的状态（本地 checkout、未提交改动、仍在跑的进程如 dev server / simulator / babysit watcher）才 resume 它。**interrupt-chain 的 resume 会静默丢指令 —— 发一个全新 subagent 带合并 scope，而不是相信一份 "done" 总结。** role（如 PR owner）比它的 agent 活得久；那个 agent 返回后由新 agent 接手下一轮。且：**你拥有每个 subagent 的工作 —— review diff、自己写总结，不要转述它说的话。第二意见 = 同一 prompt 换模型，意见一致是高信号。**

**Prose 规则。** 短陈述句，一句一个意思，句号收尾。**全文不允许长破折号字符。** 句中连接用的冒号也不允许（unslop rule 14），列表前的冒号可以。terse 不是丢内容的借口。先为 consumer 讲 impact，再讲下一个接手工程师继承了什么 —— **说不出这两者各自会注意到什么，说明工作或说明本身有问题**。绝不编造 link / citation / transcript 引用。**每个 claim 在同一句里带上它的证据或它的 label**（measured / inferred / guess）；不要把一个你本可以自己跑的检查丢给人。

**Comment 规则。** 只保留代码无法自明的**非显然 why**。verify / test 脚本不加阶段叙述式注释（`// Phase 1: add cards`）—— assertion 或 log 字符串本身就记录了那一步。这条适用于产出的每个文件，**包括 delegate 的 diff**。

**Playbook 选择。** 23 个 playbook。开 todolist，第一批 item 就是匹配到的 playbook 的步骤**逐字复制**，排在任何任务特定 todo 之前。不做的步骤留在列表里并写一行 `skip: <reason>`。大范围/跨切面工作，或用户走开去稍后 review 的工作 → `figure-it-out`（为任务设计一份 bespoke playbook）；常驻多日、多 PR 栈、大批 subagent 的项目级计划 → `orchestrate`。

## 与本 hub 的对照

本 hub 已有的等价物：

| pstack 原则 | 本 hub 对应 | 判定 |
|---|---|---|
| Laziness Protocol | Rule 2 Simplicity First / Rule 3 Surgical Changes | 已覆盖。pstack 多出 *consolidate decisions* |
| Prove It Works | Rule 13 Run, Don't Assume | **本 hub 更强**（"没执行的命令是不能做的断言"）。pstack 多出"先怀疑观测方法"与脚本化 check |
| Guard the Context Window | Rule 6 / Router invariant 4 | 已覆盖 |
| Subtract Before You Add | Rule 3（部分） | 已覆盖 |
| Test Behavior | Rule 9（部分） | pstack 的"两个想象中的编辑"比"review 测试断言什么"锋利得多 |
| Never Block on the Human | Rule 15 / Rule 16 | **冲突，需裁决**。pstack 说可逆工作不要问；本 hub 说 commit/push 未经明确指示不做、破坏性操作先确认。两边都站得住但方向相反。本 hub 更安全、pstack 更快。建议保留本 hub，把 pstack 这条**收窄到"不要问 which approach"** —— 那才是真正赚回时间的部分 |

本 hub **没有**的：

| 原则 | 为什么值得先补 |
|---|---|
| **Attack the Premise** | 本 hub 没有任何规则处理"两个修复都失败 → 质疑共同假设"。这是 debug 死循环规则，**最该先加的一条** |
| **Encode Lessons in Structure** | 本 hub 有 `update-skills`，但没有"把重复指令转成 lint/type/script"的规则 |
| **Explain the Number** | Rule 12 讲的是 agent 自己的不确定性，不是"该不该相信一次测量" |
| Minimize Reader Load | Rule 8 管重复抽象，不管 reader cognitive load 作为一条被测量的轴 |
| Model the Domain / Boundary Discipline / Type System Discipline | 领域建模、边界校验、类型纪律三条整块缺失 |
| Make Operations Idempotent | 缺失 |
| Sequence Verifiable Units | Rule 4/10 只弱覆盖；pstack 的 delivered-commit 形状（failing test 先落）没有 |
| Separate Before Serializing | Rule 9 弱覆盖；"锁是坏味道不是答案"这条更锋利 |
| Migrate Callers Then Delete | Rule 3 只清理"自己造成的孤儿"；pstack 覆盖整个迁移波 |
| Build the Lever | 缺失 |

另一处直接冲突：**pstack prose 规则禁止长破折号与句中冒号**，本 hub 的 Output shape 都没禁。要采纳就是改变每一次回复的实际形态，属于独立决策，不应顺手带进来。

## 采纳建议（不要装他们的 skills）

1. **学名字，用名字 steer。** guide 自己说：别背清单，等你发现自己正在做某件"这里有个名字本可以避免"的事时再回来查。`attack the premise before the third fix` 比定义它的整段话更可执行。
2. **只采纳会产出 artifact 的三条** —— Encode Lessons in Structure、Build the Lever、Explain the Number。各自逼出一个文件（lint / 脚本 / 带具名 limiter 的 run count 与离散度），而不是一个意图。
3. **忽略不想要的机制。** 23 个 playbook、model tier 配置、babysit/autopilot stack、Cursor 专属 model slug 全是 harness 特定的。可移植的只有原则 + autonomy/prose 规则。

## 来源

- `pstack/skills/principle-*/SKILL.md`（24 个文件，24 个目录下各一个）
- `pstack/skills/poteto-mode/SKILL.md`（149 行，机制与 playbook 索引）
- `pstack/docs/guide/08-principles.md`（24 条的简表与 steering 用法）
- `pstack/README.md`（playbook 表、plugin 版本）

上游：`https://github.com/cursor/plugins/tree/main/pstack` @ `0b8e952052d482ee6de06deebf14d590d77b1b34`