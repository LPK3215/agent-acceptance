# Changelog

本仓库所有显著变更均记录于此，格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循语义化版本。提交历史见 git log，版本节奏说明见 CONTRIBUTING.md。

## [Unreleased]

### Fixed

- 10.1.2 / 第 7 章收口把「无 7.5.1 书面红线表」误写进行为红线 block 清单：缺表改为 7.5.1 不达标并封顶原型；「红线被平均掩盖」改挂 7.5.5（有表却用总分稀释）。判据对所有项目通用，不针对单一仓库。
- 脚手架/SDK wrapper 定档漏双行 G：1.6 要求框架自身档与默发画像档分行记录，加码按框架档。
- 执行硬协议未声明被检根目录与验收快照：SKILL.md + 定档第 8 项写明忽略技能仓库夹带副本，并声明工作区或指定 commit。
- 附录 B 伪码接口名被当成必改 API：增补「同构机制 + 真实名称示例即二级」。

- 入口 `SKILL.md`、README、FAQ 与第 10 章的 1.1 快速出口口径与第 1 章对齐：改为建议性条款；框架/脚手架型与 SDK wrapper 型转为可选出口，须询问用户后决定是否按脚手架口径继续。`verify.py` 增加对应锚定，防止再次被写成强制终止。
- 第 1 章脚手架接入位置三级定义错字「刭达标」改为「判达标」。
- Windows 控制台运行 `verify.py` 时中文文件名乱码：启动时把 stdout/stderr 设为 UTF-8。
- 第 10 章页脚把附录 B/C 写成「不在包内、不要寻找」：附录 B 已在 `references/` 随包发布，页脚改为必须回链 B.1–B.5；附录 C 标明当前不存在、不要新建。
- 第 2 章 2.7 脚手架口径与 1.2 接入位置三级冲突：文档化示例改按二级「达标（接入位置级）」；G1/G2 完全无接口改警示（不再一律不达标把薄壳打成原型-B）；G3/G4 无接口仍不达标。
- 第 1 章「四条全过才进入 1.2+」与可选出口冲突：应用型四问不过可停在定档；脚手架/SDK wrapper 选择继续时四问不过仍须跑完 1.2+ 并进 10。
- 三项目复测中改进清单不会被强制指向附录 B：`SKILL.md` 执行硬协议新增「脚手架补件必指向附录 B」，`verify.py` 锚定该句与「附录 B **在包内**」；第 10 章 10.3.1 要求 P0/P1 写 B.1–B.5 编号。

### Changed

- 7.5.1 增补易混点：系统提示 / 开发纪律 / gitignore **不等于** 书面 fail-closed 红线清单；脚手架无此表即不达标，补件指向附录 B.1。
- 2.3.3 增补 SDK wrapper 口径：上游 `max_turns` 未在本仓接线时记未证实，不一票否决；未读 `node_modules` 不得臆测。
- 2.12.5 / 2.12.7 脚手架口径与 2.7 同表；2 章收口明确 wrapper 可将循环/协议/流式标「不适用」，不把上游缺件算成本仓不达标。
- 10.1.1 写明四个检查级别与 L 轴对照，结论里二者并存。

### Changed

- 发布包纳入 `LICENSE`；`release.py install` 对本机已存在的 CodeBuddy（`~/.codebuddy/skills/`）与 Claude Code（`~/.claude/skills/`）技能目录同时安装。
- GitHub Actions 在机械检查之外加跑 `pytest`；`.gitignore` 忽略 `.pytest_cache/`。

## [1.2.0] - 2026-09-04

### Changed

- 质量保障三层把关正式成形：机械自检 `verify.py` + 单元测试 `pytest`（tests/ 套件）+ GitHub Actions CI（`.github/workflows/verify.yml`）；全景展示页质量保障段由"无单测无 CI"更正为如实描述三层把关，README / CONTRIBUTING 补齐 tests/ 与 CI 流程。

### Fixed

- 全景展示页展示数字与最新代码对齐：references 篇数（13，含附录 B）/ 总行数（2282）、判点总数（357）、章 2 行数（290）、scripts 行数（verify.py 528 / release.py 168）、tests/ 各文件行数、dist 包大小（131 KB）等写死数值全部同步为真实扫描值；目录树补齐 tests/ 与 .github/。
- `verify.py` 新增展示页行数 / 文件数漂移检查（references 总行数与各章行数登记），落实 README 声称的"展示页同步：章节行数"；`main()` 开头清空 `results` 修复测试间结果残留导致的误报，单元测试 `pytest` 全绿（71 passed）。

## [1.1.0] - 2026-09-04

### Added

- 补齐 GitHub 开源标准基础文件：LICENSE（MIT）、AUTHORS、CONTRIBUTING.md、CHANGELOG.md、FAQ.md、.gitattributes；.gitignore 增补虚拟环境与编辑器规则；README 增补许可证与贡献指引段。
- 新增可视化资产：README 顶部徽章条与体系总览图（`docs/assets/badges.svg`、`docs/assets/overview.svg`），由 `docs/scripts/generate_badges.py`、`docs/scripts/generate_overview.py` 生成，零外部依赖、便于复用。
- 新增 GitHub Actions 校验工作流：向 main 推送、提交 PR 或手动触发时运行 `python scripts/verify.py`。
- L4 自动检查级别补充 AI 选级别决策树：按项目子类（应用型/脚手架型/SDK wrapper 型）逐层决策，支持按面交叉建议，用户确认后开跑。
- 1.2 形态子类新增"脚手架型接入位置三级定义"：一级（接入位置存在）判警示、二级（接入位置+文档化示例）判达标（接入位置级）、三级（接入位置+默认实现）判达标（机制级），适用于 2.7 反思回路、2.12 护栏/HITL 等检查点。
- 新增附录 B 脚手架型项目通用接入模板（`references/附录B-脚手架型通用接入模板.md`，335 行）：5 个语言无关通用模板——B.1 安全红线清单模板（7.5.1）、B.2 护栏/HITL 接入位置文档化示例（2.12.5）、B.3 评估挂钩接入位置文档化示例（2.12.7）、B.4 反思回路接入位置文档化示例（2.7）、B.5 安全测试框架扩展位置文档模板（7.5.2-7.5.6）。脚手架型项目套用模板即可从"警示"升级到"达标（接入位置级）"，不针对特定项目或编程语言。

### Changed

- 徽章生成脚本改为从 `skill.json` 和 `references/` 动态取数；两份 SVG 生成脚本同时更新 README 资产与全景展示页镜像。
- `verify.py` 增加全景展示页的判点统计、版本日期、资产镜像、依赖安全和基础无障碍同步检查。
- 验收入口从"三种跑法"改为"四个检查级别"（轻/中/重/自动），包含制，选高自动包含低；自动级别 = AI 全扫项目后从前三个级别中选/交叉。SKILL.md、README.md、FAQ.md、references/01 定档记录模板、project_overview、docs/01 流程图同步更新。术语统一：原"跑法"一律改为"检查级别"，避免与结论档（Demo/原型/Beta/生产候选）和自主度档（G1-G4）混淆。
- README 使用方式从"按角色（甲方/交付团队/外包/学习者）分类"重构为"按四个检查级别组织"：每个级别直接写明适用场景、开场白与会拿到什么，不再按角色分节。FAQ、project_overview 全景页（tab 从三角色改为四级别）、script.js 同步更新。
- 1.1 快速出口条款从强制性改为建议性：脚手架型/SDK wrapper 型项目快速出口自动转为可选出口，由检查者或用户决定是否继续走脚手架型口径完成全流程。
- 7.5 安全测试门槛按 G 档和子类分层：G1 脚手架型仅要求 7.5.1 达标，G3 应用型要求 7.5.1-7.5.3，G4 应用型要求全 7.5.1-7.5.6；门槛分层不降低安全底线，7.5.1 红线清单对所有档位均为达标门槛。
- 2.7 反思回路增加脚手架型项目特殊口径：按"接入位置"三级定义判定，不应一律判"不适用"。
- 10.1.4 档位合成协议区分"未评估"和"不达标"的封顶效果：两者封顶效果一致但改进方向不同，结论表述须区分原因。

### Fixed

- 全景展示页移除远程字体依赖，为 Chart.js CDN 增加 SRI / anonymous CORS / 无 referrer，并补齐减少动态效果偏好和 Tab 键盘 / ARIA 语义。
- `release.py install` 不再先删除已有安装目录，改为临时目录安装、完成后切换，并保留已有内容的时间戳备份。

## [1.0.0] - 2026-09-03

首个可发布版本。技能包骨架与判据体系全部落地，机械校验零失败放行。

### Added

- **技能包结构**：`SKILL.md`（frontmatter + 章级路由索引，唯一入口）、`skill.json`（机器可读元数据，与 frontmatter 双写同步）、`references/`（判据正文，按需加载）。
- **判据体系**：`references/` 下全局地图 1 图 + 章正文 01-10 + 附录 A（元规则）。面向 AI Agent / 多 Agent 项目的工程验收与定档，档位为 Demo / 原型 / 有限 Beta / 生产候选 / block；判据自含，可第三方复核。
- **执行协议**：`SKILL.md` 定义分层路由（P0-P3）、四个检查级别（轻/中/重/自动，包含制）、执行硬协议与验收产物落盘收口。
- **维护工具**：`scripts/verify.py`（结构与语义双重复核：链接、字符纪律、章节命名一致性、判点引用完整性、硬协议锚定、references 登记比对）、`scripts/release.py all`（校验 + 打包 zip + 安装到本机技能目录），并附 `verify.cmd` / `release.cmd` 一键入口。
- **维护文档**：`docs/00`（写作与引用规范）、`docs/01`（项目结构与流程图）、`docs/02`（章间依赖与数据流）、`docs/03`（维护联动速查）。

### Changed

- 仓库结构多次收敛：verify 脚本迁移至 `scripts/`，发布物统一由 `release.py` 管理；README 改为使用者视角，元数据补可发现性描述与关键词。
- 章命名统一直白可读；文档口径与 verify 脚本判定偏差多次修正对齐。
- `references/00-global-map.md` 更名 `references/00-全局地图.md`（git rename 保留历史），全库索引、verify 判名豁免与维护文档同步；标题去除英文括注，全库英文残留清零。

### Fixed

- 消融审计两处 bug；`docs/00` 失效引用修复。

[1.1.0]: https://github.com/LPK3215/agent-acceptance
[1.0.0]: https://github.com/LPK3215/agent-acceptance
