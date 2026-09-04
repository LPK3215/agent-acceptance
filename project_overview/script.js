/* ============================================================
   agent-acceptance · project_overview 交互逻辑
   数据全部取自仓库真实文件扫描结果
   ============================================================ */
(function () {
  'use strict';

  /* ---------- 数据：references/ 十二篇（行数 / 判点数取自实际扫描） ---------- */
  var CHAPTERS = [
    {
      no: '00', file: '00-全局地图.md', name: '全局地图', color: '#a78bfa',
      pts: 0, lines: 195, role: '全貌图 · 非执行必经',
      desc: '章树全貌（对象全景，穷尽该检查的全部面）。供全貌扫描、核对覆盖盲区与扩容登记用，与章正文平级。',
      secs: ['分层速览索引表（P0-P3 + L1/L2/L3）', '1 范围、形态与档位', '2 系统组成与真实接线', '3 考卷与评测集', '4 判分规则', '5 指标与目标值', '6 运行可观测', '7 安全与权限底线', '8 生产就绪与上线', '9 交付物与证据链', '10 验收结论与档位']
    },
    {
      no: '01', file: '01-范围、形态与档位.md', name: '范围、形态与档位', color: '#f43f5e',
      pts: 23, lines: 160, role: 'P0 定档问卷 · 必经入口',
      desc: '选层问卷：证是否真需要 Agent，锁形态 / 技术栈 / 边界 / 成功标准 / 自主度档，输出定档记录。',
      secs: ['1.1 是否真需要 Agent（过度设计四问）', '1.2 载体形态（六分法）', '1.3 技术栈', '1.4 目标与任务边界', '1.5 成功标准与验收口径（可测试）', '1.6 自主度 / 角色分级与适用档位 G1-G4']
    },
    {
      no: '02', file: '02-系统组成与真实接线.md', name: '系统组成与真实接线', color: '#38bdf8',
      pts: 68, lines: 289, role: 'P1 组成可查 · 判点最多',
      desc: '按组成拆开逐块查齐不齐、接没接线，只判实现真实可用。判点最多的一章——本体齐不齐是所有判据的地基。',
      secs: ['2.1 模型与认知核心层', '2.2 上下文管理', '2.3 自主执行循环', '2.4 规划与推理落地', '2.5 工具与技能接入层', '2.6 记忆机制实现', '2.7 反思与自我改进回路', '2.8 知识库与 RAG', '2.9 文档与内容解析', '2.10 数据与文件管理', '2.11 状态与编排', '2.12 Harness 运行时（8 元件）', '2.13 多 Agent 协作']
    },
    {
      no: '03', file: '03-考卷与评测集.md', name: '考卷与评测集', color: '#a78bfa',
      pts: 41, lines: 191, role: 'P2 评测资产 · 尺子',
      desc: '尺子可不可信：自评基建、测试集构成、风险样本六类、基线三件套、污染检测、分层节奏、难度递进、资产治理。',
      secs: ['3.1 自评基建', '3.2 测试集构成（五字段 / 四必备 / 配比规模）', '3.3 风险样本六类与历史失败沉淀', '3.4 基准与基线三件套（do-nothing / cheat / oracle）', '3.5 污染检测与可复现性', '3.6 评测分层与节奏（smoke / regression / safety / benchmark）', '3.7 难度递进与能力衰减评估', '3.8 评估资产治理与闭环']
    },
    {
      no: '04', file: '04-判分规则.md', name: '判分规则', color: '#a78bfa',
      pts: 39, lines: 161, role: 'P2 评测资产 · 裁判',
      desc: '怎么判才对：rubric 锚点、评分器三类型分工、匹配与判定算法、judge 选型与偏差控制、校准与漂移、分组件评估。',
      secs: ['4.1 rubric 结构与评分锚点', '4.2 评分器三类型与分工（确定性 / LLM-judge / 人工）', '4.3 匹配与判定算法（AST / 准精确 / 轨迹四档 / 幻觉分型 / Fact+mean²）', '4.4 judge 选型与偏差控制', '4.5 judge 校准与漂移监控', '4.6 分组件评估（路由器 / 技能 / 记忆 / 轨迹）']
    },
    {
      no: '05', file: '05-指标与目标值.md', name: '指标与目标值', color: '#a78bfa',
      pts: 30, lines: 135, role: 'P2 评测资产 · 分数线',
      desc: '多少算好：度量口径、完成率四件套同报、分域质量门、五层 SLI-SLO、成本预算与两段式阈值。',
      secs: ['5.1 指标口径（task_success_rate 为基，禁用 http_success_rate）', '5.2 完成率约束（与步数 / 失败率 / 成本同报、双 k 同测）', '5.3 分域目标与质量门（幻觉 / 时延 / 错误率 / 可用性）', '5.4 SLI-SLO 五层目标', '5.5 成本预算与两段式阈值']
    },
    {
      no: '06', file: '06-运行可观测.md', name: '运行可观测', color: '#34d399',
      pts: 29, lines: 132, role: 'P3 运行证据',
      desc: '过程能不能看见：trace/span 骨架、十字段必埋、step 级归因、审计日志与链路回放、版本绑定与奖励黑客插桩。',
      secs: ['6.1 trace/span 骨架（一次任务 = 一条 trace）', '6.2 必埋字段与十字段', '6.3 归因粒度与失败定位（step 级）', '6.4 审计日志与链路回放', '6.5 版本绑定与奖励黑客插桩']
    },
    {
      no: '07', file: '07-安全与权限底线.md', name: '安全与权限底线', color: '#f43f5e',
      pts: 38, lines: 181, role: 'P3 · 必查不可跳',
      desc: '不越权、不上当、关键交人、数据可管。红线触顶清单是章 8 Gate 前置与章 10 一票否决的唯一来源。',
      secs: ['7.1 最小权限与授权模型', '7.2 工具治理', '7.3 注入与内容隔离', '7.4 人工确认设计', '7.5 安全测试与红线', '7.6 数据治理与数据生命周期']
    },
    {
      no: '08', file: '08-生产就绪与上线.md', name: '生产就绪与上线', color: '#34d399',
      pts: 39, lines: 171, role: 'P3 运行证据',
      desc: '能不能放出去：四可、12 Gate 主干、失败隔离与恢复、灰度与回滚治理、复认证、事件响应、漂移监控。',
      secs: ['8.1 生产就绪四可', '8.2 上线前检查（12 Gate 主干 G0-G11）', '8.3 失败隔离与恢复（沙箱 / checkpoint / 幂等 / 回滚 / 急停）', '8.4 灰度与回滚治理', '8.5 复认证触发与 go/no-go 决策', '8.6 事件响应与负责人制度', '8.7 生产持续评估与漂移监控']
    },
    {
      no: '09', file: '09-交付物与证据链.md', name: '交付物与证据链', color: '#34d399',
      pts: 34, lines: 157, role: 'P3 交付证据',
      desc: '交得出什么、哪条证据能进结论：生命周期 10 项工件、证据等级 E1-E4、Agent Card fail-closed、例外审批。',
      secs: ['9.1 最小交付物清单（生命周期 10 项）', '9.2 证据等级与证据形态', '9.3 验收单 / Agent Card（fail-closed 分档）', '9.4 文档属性与例外审批', '9.5 合规报告骨架（GB/T 25000.51）', '9.6 业务交付验收六维（仅委托方场景启用）']
    },
    {
      no: '10', file: '10-验收结论与档位.md', name: '验收结论与档位', color: '#f0b429',
      pts: 16, lines: 89, role: '收口层 · 不新增检查面',
      desc: '合成定论：否决项先挡门、加权定档、未证实项不混入通过、改进回归闭环。判点最少——只聚合不重判。',
      secs: ['10.1 分档规则（加权汇总 / 否决项优先）', '10.2 未证实项清单（缺背书不混入通过）', '10.3 改进建议与回归闭环']
    },
    {
      no: 'A', file: '附录A-元规则.md', name: '附录 A 元规则', color: '#94a3b8',
      pts: 0, lines: 58, role: '全程 · 检查者纪律',
      desc: '不评什么（Out of Scope 五条）+ 验收者反模式自查六条。读完才够格当检查者，自查动作本身要留痕。',
      secs: ['A.1 Out of Scope（不评什么）', 'A.2 验收者反模式自查（不犯什么）', '附录收口：检查者出师自检']
    }
  ];

  /* ---------- 数据：真实目录结构 ---------- */
  var TREE = {
    name: 'agent-acceptance/', type: 'dir', desc: 'Agent Skills 技能包根目录', open: true, badge: 'v1.0.0',
    children: [
      { name: 'SKILL.md', type: 'file', desc: '唯一入口：frontmatter 元数据 + 章级路由索引（每行直达一章正文）', badge: '发布物' },
      { name: 'skill.json', type: 'file', desc: '机器可读元数据，与 frontmatter 双写同步，含 15 个关键词', badge: '发布物' },
      {
        name: 'references/', type: 'dir', desc: '判据正文 · 技能核心资产（12 个文件，357 判点）', open: true, badge: '发布物',
        children: [
          { name: '00-全局地图.md', type: 'file', desc: '章树全貌（平级成员，供全貌扫描与扩容登记，非执行必经）', badge: '195 行' },
          { name: '01-范围、形态与档位.md', type: 'file', desc: 'P0 定档问卷：过度设计四问 · 形态 · 技术栈 · 边界 · 成功标准 · G1-G4', badge: '23 判点' },
          { name: '02-系统组成与真实接线.md', type: 'file', desc: 'P1：13 大模块逐块查齐不齐、接没接线（判点最多）', badge: '68 判点' },
          { name: '03-考卷与评测集.md', type: 'file', desc: 'P2：自评基建 · 测试集构成 · 风险样本六类 · 基线三件套 · 污染检测', badge: '41 判点' },
          { name: '04-判分规则.md', type: 'file', desc: 'P2：rubric · 评分器三类型 · 判定算法 · judge 选型与校准', badge: '39 判点' },
          { name: '05-指标与目标值.md', type: 'file', desc: 'P2：度量口径 · 完成率四件套 · 分域质量门 · 五层 SLO · 两段式阈值', badge: '30 判点' },
          { name: '06-运行可观测.md', type: 'file', desc: 'P3：trace 骨架 · 十字段 · step 级归因 · 审计回放 · 奖励黑客插桩', badge: '29 判点' },
          { name: '07-安全与权限底线.md', type: 'file', desc: 'P3 · 必查：最小权限 · 工具治理 · 注入隔离 · 人工确认 · 红线 · 数据生命周期', badge: '38 判点' },
          { name: '08-生产就绪与上线.md', type: 'file', desc: 'P3：四可 · 12 Gate · 失败隔离 · 灰度回滚 · 事件响应 · 漂移监控', badge: '39 判点' },
          { name: '09-交付物与证据链.md', type: 'file', desc: 'P3：生命周期 10 项工件 · E1-E4 · Agent Card · 例外审批 · GB/T 25000.51', badge: '34 判点' },
          { name: '10-验收结论与档位.md', type: 'file', desc: '收口层：否决先行 · 加权定档 · 未证实项清单 · 改进回归闭环', badge: '16 判点' },
          { name: '附录A-元规则.md', type: 'file', desc: '检查者纪律：Out of Scope 五条 + 反模式自查六条', badge: '11 条目' }
        ]
      },
      {
        name: 'docs/', type: 'dir', desc: '作者与维护者专用（写作规范 / 结构图 / 依赖 / 速查），自身含规则反例示范，不参与机械扫描',
        children: [
          { name: '00-写作与引用规范.md', type: 'file', desc: '链接白名单 · 字符纪律 · 引用溯源 · T 级素材可信度分级', badge: '100 行' },
          { name: '01-项目结构与流程图.md', type: 'file', desc: '6 张 Mermaid 图：包结构 · 章 1 分流 · 完整流程 · 四个检查级别 · 发布流水线 · 元数据同步', badge: '218 行' },
          { name: '02-章间依赖与数据流.md', type: 'file', desc: '全局数据流 · 每章输入输出 · 强依赖 · 跨章引用热点 · 改动影响面速查', badge: '116 行' },
          { name: '03-维护联动速查.md', type: 'file', desc: '改判据时的联动面清单', badge: '135 行' },
          {
            name: 'assets/', type: 'dir', desc: '可视化资产（脚本生成，勿手改）',
            children: [
              { name: 'badges.svg', type: 'file', desc: 'README 顶部徽章条' },
              { name: 'overview.svg', type: 'file', desc: '体系总览图，口径变更后重跑 generate_overview.py 刷新' }
            ]
          },
          {
            name: 'scripts/', type: 'dir', desc: '图生成脚本，零外部依赖',
            children: [
              { name: 'generate_badges.py', type: 'file', desc: '生成 badges.svg' },
              { name: 'generate_overview.py', type: 'file', desc: '生成 overview.svg' }
            ]
          }
        ]
      },
      {
        name: 'scripts/', type: 'dir', desc: '维护工具（发布门禁）',
        children: [
          { name: 'verify.py', type: 'file', desc: '机械自检：结构与语义双重复核，FAIL 0 为硬性放行条件', badge: '454 行' },
          { name: 'release.py', type: 'file', desc: '一键发布：check → package → install', badge: '141 行' },
          { name: 'verify.cmd', type: 'file', desc: 'Windows 双击入口，包装 verify.py' },
          { name: 'release.cmd', type: 'file', desc: 'Windows 双击入口，包装 release.py' }
        ]
      },
      { name: 'dist/', type: 'dir', desc: '发布产物', children: [
        { name: 'agent-acceptance-1.0.0.zip', type: 'file', desc: 'v1.0.0 打包产物，zip 顶层带技能目录名，解压即可加载', badge: '122 KB' }
      ]},
      { name: 'project_overview.html', type: 'file', desc: '全景观览页根入口（meta refresh 跳转）', badge: '本页' },
      { name: 'project_overview/', type: 'dir', desc: '全景观览页资源目录', open: true, children: [
        { name: 'index.html', type: 'file', desc: '页面骨架（含内联 SVG 架构图）' },
        { name: 'style.css', type: 'file', desc: '全部样式（主题变量 / 卡片 / 动画 / 响应式）' },
        { name: 'script.js', type: 'file', desc: '交互逻辑（导航 / 目录树 / Tab / 计数 / 主题）' },
        { name: 'charts.js', type: 'file', desc: 'Chart.js 图表（判点分布 / SLO / 完成率 / 两段式 / 成本）' },
        { name: 'assets/', type: 'dir', desc: '位图与 SVG 资源', children: [
          { name: 'overview.svg', type: 'file', desc: '仓库原体系总览图（副本）' },
          { name: 'badges.svg', type: 'file', desc: '徽章条（副本）' }
        ]}
      ]},
      { name: 'README.md', type: 'file', desc: '使用者视角：结论档体系 · 四个检查级别 · 各级别开场白与产出 · 使用边界 · 质量标准' },
      { name: 'FAQ.md', type: 'file', desc: '九个高频问题' },
      { name: 'CONTRIBUTING.md', type: 'file', desc: '贡献指引：四类改动流程 · 扩容三关 · 内容纪律 · 发布流程' },
      { name: 'CHANGELOG.md', type: 'file', desc: 'Keep a Changelog 格式，语义化版本' },
      { name: 'LICENSE', type: 'file', desc: 'MIT License' },
      { name: 'AUTHORS', type: 'file', desc: '作者与主要贡献者：LPK' }
    ]
  };

  /* ---------- 数据：references 文档索引（注入到 Tab d1） ---------- */
  var REF_DOCS = [
    { f: '00-全局地图.md', s: '章树全貌：分层速览索引表（P0-P3 / L1-L3）+ 十章对象全景，供全貌扫描与扩容登记。', m: '195 行 · 平级成员' },
    { f: '01-范围、形态与档位.md', s: '必经入口：过度设计四问 + 形态六分法 + 技术栈 + 边界 + 成功标准 + 自主度 G1-G4，输出定档记录。', m: '160 行 · 23 判点' },
    { f: '02-系统组成与真实接线.md', s: '13 大模块逐块查齐不齐、接没接线，含 Harness 运行时八元件与多 Agent 协作。', m: '289 行 · 68 判点' },
    { f: '03-考卷与评测集.md', s: '自评基建到资产治理八节；risk 样本六类、基线三件套、污染检测与可复现性。', m: '191 行 · 41 判点' },
    { f: '04-判分规则.md', s: 'rubric 锚点、评分器三类型、判定算法五件套、judge 选型与偏差、校准与漂移、分组件评估。', m: '161 行 · 39 判点' },
    { f: '05-指标与目标值.md', s: '度量口径、完成率四件套、分域质量门、五层 SLI-SLO、成本预算与两段式阈值。', m: '135 行 · 30 判点' },
    { f: '06-运行可观测.md', s: 'trace/span 骨架、十字段必埋、step 级归因、审计日志与链路回放、版本绑定与奖励黑客插桩。', m: '132 行 · 29 判点' },
    { f: '07-安全与权限底线.md', s: '最小权限、工具治理、注入隔离、人工确认、红线与攻击库入 CI、数据生命周期；含 OWASP ASI 对照表。', m: '181 行 · 38 判点' },
    { f: '08-生产就绪与上线.md', s: '四可、12 Gate 主干、失败隔离五件、灰度与回滚治理、复认证 go/no-go、事件响应、漂移监控。', m: '171 行 · 39 判点' },
    { f: '09-交付物与证据链.md', s: '生命周期 10 项工件、证据等级 E1-E4、Agent Card fail-closed 分档、例外审批、GB/T 25000.51 骨架。', m: '157 行 · 34 判点' },
    { f: '10-验收结论与档位.md', s: '否决先行、加权定档、未证实项清单、改进回归闭环；含落盘与归档规定。', m: '89 行 · 16 判点' },
    { f: '附录A-元规则.md', s: 'Out of Scope 五条 + 验收者反模式自查六条 + 检查者出师自检。', m: '58 行 · 11 条目' }
  ];

  /* ---------- 工具 ---------- */
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  /* ---------- 1. 主题 ---------- */
  function initTheme() {
    var saved = null;
    try { saved = localStorage.getItem('aa-theme'); } catch (e) {}
    var theme = saved || (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    document.documentElement.setAttribute('data-theme', theme);

    $('#themeToggle').addEventListener('click', function () {
      var cur = document.documentElement.getAttribute('data-theme');
      var next = cur === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      try { localStorage.setItem('aa-theme', next); } catch (e) {}
      if (window.AACharts && typeof window.AACharts.refresh === 'function') {
        setTimeout(window.AACharts.refresh, 40);
      }
    });
  }

  /* ---------- 2. 渲染章节卡 ---------- */
  function renderChapters() {
    var host = $('#chapterGrid');
    if (!host) return;
    var html = '';
    CHAPTERS.forEach(function (c, i) {
      html += '<article class="chapter reveal" style="--ch-color:' + c.color + '" data-i="' + i + '">' +
        '<div class="ch-top">' +
          '<span class="ch-no">' + esc(c.no) + '</span>' +
          '<span class="ch-name">' + esc(c.name) + '</span>' +
          '<span class="ch-pts">' + (c.pts ? c.pts + ' 判点' : c.lines + ' 行') + '</span>' +
        '</div>' +
        '<div class="ch-desc">' + esc(c.desc) + '</div>' +
        '<div style="font-size:11.5px;color:var(--ch-color);font-weight:600;margin-bottom:2px">' + esc(c.role) + '</div>' +
        '<div class="ch-secs" id="chsecs-' + i + '"><ul>' +
          c.secs.map(function (s) { return '<li>' + esc(s) + '</li>'; }).join('') +
        '</ul></div>' +
        '<button class="ch-toggle" data-target="chsecs-' + i + '">展开 ' + c.secs.length + ' 个小节 ▾</button>' +
      '</article>';
    });
    host.innerHTML = html;

    $$('.ch-toggle', host).forEach(function (btn) {
      btn.addEventListener('click', function () {
        var box = document.getElementById(btn.getAttribute('data-target'));
        var open = box.classList.toggle('open');
        var total = box.querySelectorAll('li').length;
        btn.textContent = (open ? '收起 ' : '展开 ') + total + ' 个小节 ' + (open ? '▴' : '▾');
      });
    });
  }

  /* ---------- 3. 渲染文档索引 ---------- */
  function renderDocs() {
    var host = $('#docListRefs');
    if (!host) return;
    host.innerHTML = REF_DOCS.map(function (d) {
      return '<a class="doc-item" href="../references/' + encodeURIComponent(d.f) + '">' +
        '<span class="doc-name">references/' + esc(d.f) + '</span>' +
        '<span class="doc-sum">' + esc(d.s) + '</span>' +
        '<span class="doc-meta">' + esc(d.m) + '</span></a>';
    }).join('');
  }

  /* ---------- 4. 渲染目录树 ---------- */
  function buildNode(node, depth) {
    var isDir = node.type === 'dir' && node.children && node.children.length;
    var cls = 'tree-row';
    var nameCls = 'tree-name' + (isDir ? ' dir' : '') + (node.dim ? ' dim' : '');
    var caret = isDir
      ? '<span class="tree-caret' + (node.open ? ' open' : '') + '" aria-hidden="true">' +
        '<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"></path></svg></span>'
      : '<span class="tree-caret leaf" aria-hidden="true">·</span>';

    var html = '<div class="' + cls + '">' + caret +
      '<span class="' + nameCls + '">' + esc(node.name) + '</span>' +
      (node.desc ? '<span class="tree-desc">— ' + esc(node.desc) + '</span>' : '') +
      (node.badge ? '<span class="tree-badge' + (node.badge === '不发布' ? ' out' : '') + '">' + esc(node.badge) + '</span>' : '') +
      '</div>';

    if (isDir) {
      var childHtml = node.children.map(function (c) { return buildNode(c, depth + 1); }).join('');
      html += '<div class="tree-children' + (node.open ? ' open' : '') + '">' +
              '<div class="tree-node">' + childHtml + '</div></div>';
    }
    // 叶子包一层，保持缩进一致
    return '<div class="tree-item">' + html + '</div>';
  }

  function renderTree() {
    var host = $('#fileTree');
    if (!host) return;
    host.innerHTML = buildNode(TREE, 0);

    $$('.tree-caret:not(.leaf)', host).forEach(function (caret) {
      caret.addEventListener('click', function () {
        var item = caret.closest('.tree-item');
        var kids = item ? item.querySelector(':scope > .tree-children') : null;
        if (!kids) return;
        var open = kids.classList.toggle('open');
        caret.classList.toggle('open', open);
      });
    });
    // 让整行可点击折叠
    $$('.tree-row', host).forEach(function (row) {
      row.addEventListener('click', function (e) {
        if (e.target.closest('.tree-caret')) return;
        var caret = row.querySelector('.tree-caret:not(.leaf)');
        if (caret) caret.click();
      });
    });
  }

  function bindTreeToolbar() {
    var exp = $('#treeExpand'), col = $('#treeCollapse');
    if (exp) exp.addEventListener('click', function () {
      $$('#fileTree .tree-children').forEach(function (n) { n.classList.add('open'); });
      $$('#fileTree .tree-caret:not(.leaf)').forEach(function (n) { n.classList.add('open'); });
    });
    if (col) col.addEventListener('click', function () {
      $$('#fileTree .tree-children').forEach(function (n) { n.classList.remove('open'); });
      $$('#fileTree .tree-caret:not(.leaf)').forEach(function (n) { n.classList.remove('open'); });
    });
  }

  /* ---------- 5. Tab 切换 ---------- */
  function initTabs() {
    $$('[data-tabs]').forEach(function (group) {
      var tabs = $$('.tab', group);
      var scope = group.parentElement;
      var groupName = group.getAttribute('data-tabs');
      group.setAttribute('role', 'tablist');
      tabs.forEach(function (tab) {
        var name = tab.getAttribute('data-tab');
        var panel = $('.tab-panel[data-panel="' + name + '"]', scope);
        var tabId = groupName + '-tab-' + name;
        var panelId = groupName + '-panel-' + name;
        tab.id = tabId;
        tab.setAttribute('role', 'tab');
        tab.setAttribute('aria-controls', panelId);
        if (panel) {
          panel.id = panelId;
          panel.setAttribute('role', 'tabpanel');
          panel.setAttribute('aria-labelledby', tabId);
          panel.setAttribute('tabindex', '0');
        }

        function activate(moveFocus) {
          tabs.forEach(function (t) { t.classList.remove('active'); });
          tab.classList.add('active');
          $$('.tab-panel', scope).forEach(function (p) {
            var selected = p.getAttribute('data-panel') === name;
            p.classList.toggle('active', selected);
            p.setAttribute('aria-hidden', selected ? 'false' : 'true');
          });
          tabs.forEach(function (t) {
            var selected = t === tab;
            t.setAttribute('aria-selected', selected ? 'true' : 'false');
            t.tabIndex = selected ? 0 : -1;
          });
          if (moveFocus) tab.focus();
          if (window.AACharts && typeof window.AACharts.ensure === 'function') {
            setTimeout(function () { window.AACharts.ensure(name); }, 30);
          }
        }

        tab.addEventListener('click', function () { activate(false); });
        tab.addEventListener('keydown', function (event) {
          var index = tabs.indexOf(tab);
          var next = null;
          if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (index + 1) % tabs.length;
          if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (index - 1 + tabs.length) % tabs.length;
          if (event.key === 'Home') next = 0;
          if (event.key === 'End') next = tabs.length - 1;
          if (next !== null) {
            event.preventDefault();
            tabs[next].click();
            tabs[next].focus();
          }
        });
        if (tab.classList.contains('active')) activate(false);
      });
    });
  }

  /* ---------- 6. 导航：滚动高亮 + 平滑 + 进度条 + 汉堡 ---------- */
  function initNav() {
    var nav = $('#navbar');
    var bar = $('#progressBar');
    var links = $$('.nav-link');
    var sideLinks = $$('#sidebarList a');
    var sections = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); }).filter(Boolean);
    var sidebar = $('#sidebar');
    var toTop = $('#toTop');

    function onScroll() {
      var y = window.scrollY || document.documentElement.scrollTop;
      var h = document.documentElement.scrollHeight - window.innerHeight;
      if (bar) bar.style.width = (h > 0 ? (y / h) * 100 : 0) + '%';
      nav.classList.toggle('scrolled', y > 12);
      toTop.classList.toggle('show', y > window.innerHeight * 0.7);
      if (sidebar) sidebar.classList.toggle('show', y > window.innerHeight * 0.45);

      var idx = -1;
      for (var i = 0; i < sections.length; i++) {
        var top = sections[i].getBoundingClientRect().top;
        if (top - 140 <= 0) idx = i; else break;
      }
      sweepReveal();
      links.forEach(function (a, i) { a.classList.toggle('active', i === idx); });
      if (idx >= 0) {
        var id = links[idx].getAttribute('href').slice(1);
        sideLinks.forEach(function (a) { a.classList.toggle('active', a.getAttribute('href') === '#' + id); });
      } else {
        sideLinks.forEach(function (a) { a.classList.toggle('active', a.getAttribute('href') === '#top'); });
      }
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    // 平滑滚动（补齐 scroll-padding 不支持的场景）
    $$('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var id = a.getAttribute('href');
        if (id === '#' || id.length < 2) return;
        var target = document.querySelector(id);
        if (!target) return;
        e.preventDefault();
        var offset = 78;
        var y = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top: y, behavior: 'smooth' });
        if ($('#navLinks').classList.contains('open')) $('#navLinks').classList.remove('open');
      });
    });

    toTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    var burger = $('#burger');
    burger.addEventListener('click', function () {
      $('#navLinks').classList.toggle('open');
    });
  }

  /* ---------- 7. 数字计数动画 ---------- */
  function initCounters() {
    var els = $$('[data-count]');
    if (!els.length) return;
    function run(el) {
      if (el.dataset.counted === '1') return;
      el.dataset.counted = '1';
      var target = parseInt(el.getAttribute('data-count'), 10) || 0;
      var dur = 1100;
      var t0 = performance.now();
      function step(t) {
        var p = Math.min((t - t0) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(target * eased).toLocaleString('en-US');
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
      // 兜底：rAF 被节流或不可用时，保证终值正确
      setTimeout(function () { el.textContent = target.toLocaleString('en-US'); }, dur + 260);
    }
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { run(en.target); io.unobserve(en.target); }
        });
      }, { threshold: 0.1 });
      els.forEach(function (el, i) {
        var r = el.getBoundingClientRect();
        // 首屏可见的直接跑，避免观察器未触发时数字停在 0
        if (r.top < window.innerHeight && r.bottom > 0) run(el);
        else io.observe(el);
        // 兜底：2.5s 后仍未计数的一律运行
        setTimeout(function () { run(el); }, 2500 + i * 120);
      });
    } else {
      els.forEach(run);
    }
  }

  /* ---------- 8. 入场动画 ---------- */
  var revealTargets = [];
  function sweepReveal() {
    if (!revealTargets.length) return;
    var h = window.innerHeight;
    revealTargets = revealTargets.filter(function (el) {
      if (el.classList.contains('in')) return false;
      var r = el.getBoundingClientRect();
      if (r.top < h * 1.05 && r.bottom > -150) { el.classList.add('in'); return false; }
      return true;
    });
  }
  function initReveal() {
    var targets = $$('.card, .chapter, .section-head, .stat-strip');
    targets.forEach(function (el) { el.classList.add('reveal'); });
    if (!('IntersectionObserver' in window)) {
      targets.forEach(function (el) { el.classList.add('in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.04, rootMargin: '0px 0px -30px 0px' });
    targets.forEach(function (el) { io.observe(el); });

    // 兜底：观察器因环境原因未触发时，按视口位置补显示，避免内容永久不可见
    revealTargets = targets.slice();
    setTimeout(sweepReveal, 700);
    setTimeout(sweepReveal, 2200);
  }

  /* ---------- 9. 代码复制 ---------- */
  function initCopy() {
    $$('.copy-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var box = btn.closest('.code');
        var pre = box ? box.querySelector('pre') : null;
        if (!pre) return;
        var text = pre.innerText;
        function done() {
          btn.textContent = '已复制';
          btn.classList.add('done');
          setTimeout(function () { btn.textContent = '复制'; btn.classList.remove('done'); }, 1600);
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done, function () { fallback(text, done); });
        } else {
          fallback(text, done);
        }
      });
    });
    function fallback(text, cb) {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); cb(); } catch (e) {}
      document.body.removeChild(ta);
    }
  }

  /* ---------- 10. SVG 架构图 tooltip ---------- */
  function initSvgTips() {
    // 逐 wrap 绑定
    $$('.svg-wrap').forEach(function (wrap) {
      var tip = wrap.querySelector('.svg-tooltip');
      if (!tip) return;
      $$('[data-tip]', wrap).forEach(function (node) {
        node.addEventListener('mouseenter', function () { show(tip, node.getAttribute('data-tip')); });
        node.addEventListener('mousemove', function (e) { move(wrap, tip, e); });
        node.addEventListener('mouseleave', function () { tip.classList.remove('show'); });
      });
    });
    // 模块格复用同一套提示
    $$('.module[data-tip]').forEach(function (m) {
      var host = m.closest('.card') || m;
      if (host.querySelector('.svg-tooltip')) return;
      var tip = document.createElement('div');
      tip.className = 'svg-tooltip';
      host.style.position = 'relative';
      host.appendChild(tip);
      m.addEventListener('mouseenter', function () { show(tip, m.getAttribute('data-tip')); });
      m.addEventListener('mousemove', function (e) { move(host, tip, e); });
      m.addEventListener('mouseleave', function () { tip.classList.remove('show'); });
    });

    function show(tip, text) { tip.textContent = text; tip.classList.add('show'); }
    function move(host, tip, e) {
      var r = host.getBoundingClientRect();
      var x = e.clientX - r.left + 14;
      var y = e.clientY - r.top + 14;
      var maxX = r.width - tip.offsetWidth - 10;
      if (x > maxX) x = Math.max(6, maxX);
      tip.style.left = x + 'px';
      tip.style.top = y + 'px';
    }
  }

  /* ---------- 启动 ---------- */
  function boot() {
    initTheme();
    renderChapters();
    renderDocs();
    renderTree();
    bindTreeToolbar();
    initTabs();
    initNav();
    initCounters();
    initReveal();
    initCopy();
    initSvgTips();
    if (window.AACharts && typeof window.AACharts.init === 'function') window.AACharts.init();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
