# 贡献指引

欢迎参与 agent-acceptance 的维护。本仓库是一个 Agent Skills 技能包：全部内容为 Markdown 判据正文 + 少量 Python 维护脚本。贡献前请先通读本文与 [docs/00-写作与引用规范.md](docs/00-写作与引用规范.md)。

## 仓库结构与角色

- `SKILL.md`：唯一入口（元数据 + 章级路由索引），不承载判据正文
- `references/`：判据正文（章 01-10 + 附录 A 元规则 + 附录 B 脚手架型通用接入模板）与全局地图（00），技能包核心资产
- `docs/`：作者维护区（写作规范、结构、依赖、速查），自身含规则反例示范，不参与机械扫描
- `project_overview/`：仓库全景展示页，不进发布包；其判点统计、元数据、生成资产与基础访问性由 verify 交叉检查
- `scripts/verify.py`：机械自检（发布门禁）
- `scripts/release.py`：一键发布（校验 -> 打包 -> 安装本机，覆盖安装前保留备份）
- `tests/`：维护脚本单元测试（pytest），覆盖 verify / release / 两个 SVG 生成脚本
- `.github/workflows/verify.yml`：GitHub Actions 校验工作流（推送 main、PR、手动触发），跑 `verify.py` 与 `pytest`

## 改动类型与对应流程

### 1. 修错字 / 措辞 / 引用

- 直接修改对应章正文即可，不动章号与判点号。
- 改 `references/` 链接或新增/删除文件时，注意维护联动：`verify.py` 的 `KNOWN_REF_FILES` 登记、`docs/` 维护文档、各章头部回链需三方同步。
- 机械自检：`python scripts/verify.py`，须 FAIL 0。

### 2. 修改判据（不新增判点）

- 判点号是稳定主键，正文互引用它，改判据不得改动编号。
- 若改的是达标线、证据要求等语义，需同步检查：涉及判据的引用处、对应输出物描述、以及 `docs/03-维护联动速查.md` 列出的联动面。

### 3. 新增检查面（扩容）

先过扩容三关，再落正文：

1. **通用**：对任意形态 / 技术栈 / 场景的 Agent 都成立，非单项目专属；
2. **公用**：其他章查同一条可直接回链，不造语义重复的面；
3. **可判**：能落成「查什么 / 判据 / 证据」而非感想。

过三关后：

- 在 `references/00-全局地图.md` 对应小节登记（图只增不删）；
- 落章正文小节；
- 同步 `verify.py` 登记表与 `docs/` 维护文档。

### 4. 新增 / 删除一章

- 三处登记必须同步，否则 verify 会 FAIL：`SKILL.md` 路由表、`00-全局地图.md`、`verify.py` 的 `KNOWN_REF_FILES`。
- 章正文超过 100 行需具备「正文小节导航」。

### 5. 修改全景展示页 / 可视化资产

- `project_overview/` 的判点统计、版本与日期必须和 `references/`、`skill.json` 同步；`python scripts/verify.py` 会检查关键展示值。
- SVG 是受管生成物：修改 `skill.json`、`references/` 数量或图示口径后，运行 `python docs/scripts/generate_badges.py` 与 `python docs/scripts/generate_overview.py`。脚本会同时更新 `docs/assets/` 和展示页镜像，禁止只手改其中一份。
- 展示页新增第三方脚本时必须固定版本、配置 SRI；动态效果须尊重 `prefers-reduced-motion`，新 Tab / 折叠交互须提供键盘可达性。

## 内容纪律

- 判据自含：不依赖本仓库之外的任何文件；对外引用须标注出处与版本，外链仅允许官方一手来源（verify 对非一手来源给 WARN）。
- 写作遵循 `docs/00`：链接只指向技能包内部文件（入口 + references/），字符纪律（含全角标点、禁用清单）以规范为准。
- 中文为源语言：正文以中文定稿，英文翻译仅在有明确发布需求时另行推进，不做双语常驻维护。

### 6. 修改维护脚本

- `scripts/` 下脚本改动后，同步更新 `tests/` 中对应单元测试，并跑 `python -m pytest tests/`。
- 判据正文或文件行数变化会导致展示页数值漂移，由 `python scripts/verify.py` 兜底；展示页数值类 FAIL 按 `docs/03-维护联动速查.md` 第 7 节逐项修正。

## 提交与合并约定

- 提交信息用 `type: 简述` 前缀（`feat` / `fix` / `docs` / `refactor` / `chore`），中文描述。
- 涉及判据正文的改动，提交信息须能反查改动点。
- 合入主干前必跑 `python scripts/verify.py`（FAIL 0）与 `python -m pytest tests/`（仅允许保留 WARN 级官方外链提示项）。

## 发布流程

版本号与节奏由维护者决定（当前 1.2.0）。发版时：

1. 更新 `CHANGELOG.md`（把 [Unreleased] 内容归入新版本号）；
2. 更新 `skill.json` 与 `SKILL.md` frontmatter 的 `version`（两者须一致，verify 会查）；
3. `python scripts/release.py all`（校验 + 打包 + 安装本机；已有安装会保留为带时间戳的同级备份）。
