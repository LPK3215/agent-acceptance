/* ============================================================
   agent-acceptance · project_overview 图表（Chart.js）
   数据全部取自 references/ 正文真实数值
   ============================================================ */
window.AACharts = (function () {
  'use strict';

  var built = {};        // 已构建的图表实例
  var instances = {};    // 按 canvas id 保存

  function css(name, fallback) {
    var v = getComputedStyle(document.documentElement).getPropertyValue(name);
    return (v && v.trim()) ? v.trim() : fallback;
  }

  function palette() {
    return {
      text: css('--text', '#e6edf7'),
      dim: css('--text-dim', '#7d8ba4'),
      border: css('--border', 'rgba(148,163,184,.16)'),
      surface: css('--surface-solid', '#111a2e'),
      accent: css('--accent', '#f0b429'),
      blue: css('--accent-2', '#38bdf8'),
      green: css('--accent-3', '#34d399'),
      red: css('--danger', '#f43f5e'),
      violet: css('--violet', '#a78bfa'),
      warn: css('--warn', '#fb923c')
    };
  }

  function baseOptions(opts) {
    var p = palette();
    var o = {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 900, easing: 'easeOutQuart' },
      plugins: {
        legend: {
          display: opts.legend !== false,
          labels: { color: p.dim, font: { family: getComputedStyle(document.body).fontFamily, size: 11.5 }, boxWidth: 12, boxHeight: 12, usePointStyle: true, pointStyle: 'roundedRect', padding: 14 }
        },
        tooltip: {
          backgroundColor: p.surface,
          titleColor: p.text,
          bodyColor: p.dim,
          borderColor: p.border,
          borderWidth: 1,
          padding: 10,
          cornerRadius: 8,
          displayColors: true,
          titleFont: { size: 12, weight: '700' },
          bodyFont: { size: 12 }
        }
      },
      scales: {}
    };
    if (opts.x) o.scales.x = opts.x;
    if (opts.y) o.scales.y = opts.y;
    return o;
  }

  function axis(p, opts) {
    return {
      grid: { color: p.border, drawTicks: false, borderColor: 'transparent' },
      ticks: { color: p.dim, font: { size: 11 }, padding: 6 },
      title: opts && opts.title ? { display: true, text: opts.title, color: p.dim, font: { size: 11 }, padding: { top: 4 } } : undefined
    };
  }

  /* ---------- 图 1：各章判点分布 ---------- */
  function buildPoints() {
    var p = palette();
    var labels = ['01 范围形态', '02 系统组成', '03 考卷', '04 判分', '05 指标', '06 可观测', '07 安全', '08 上线', '09 交付', '10 收口'];
    var data = [23, 68, 41, 39, 30, 29, 38, 39, 34, 16];
    var colors = [p.red, p.blue, p.violet, p.violet, p.violet, p.green, p.red, p.green, p.green, p.accent];

    instances.chartPoints = new Chart(document.getElementById('chartPoints'), {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: '判点数',
          data: data,
          backgroundColor: colors.map(function (c) { return c + '33'; }),
          borderColor: colors,
          borderWidth: 1.6,
          borderRadius: 6,
          borderSkipped: false,
          maxBarThickness: 58
        }]
      },
      options: baseOptions({
        legend: false,
        x: axis(p),
        y: Object.assign(axis(p, { title: '判点数量' }), { beginAtZero: true, suggestedMax: 74 })
      })
    });
    built.m1 = true;
  }

  /* ---------- 图 2：五层 SLO 阈值 ---------- */
  function buildSLO() {
    var p = palette();
    var labels = ['任务成功\nGold 场景', '智能质量\n关键字段覆盖', '工具可靠性\n关键工具成功率', '安全合规\n审计完整率', '可观测\ntrace 完整率'];
    var data = [99, 98, 99.5, 100, 99];
    var colors = [p.accent, p.violet, p.blue, p.red, p.green];

    instances.chartSLO = new Chart(document.getElementById('chartSLO'), {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'SLO 阈值（%）',
          data: data,
          backgroundColor: colors.map(function (c) { return c + '33'; }),
          borderColor: colors,
          borderWidth: 1.6,
          borderRadius: 6,
          borderSkipped: false,
          maxBarThickness: 64
        }]
      },
      options: Object.assign(baseOptions({
        legend: false,
        x: axis(p),
        y: Object.assign(axis(p, { title: '百分比（%）· 纵轴自 90 起' }), { min: 90, max: 100.5, ticks: { color: p.dim, font: { size: 11 }, stepSize: 2 } })
      }), {
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: p.surface, titleColor: p.text, bodyColor: p.dim,
            borderColor: p.border, borderWidth: 1, padding: 10, cornerRadius: 8,
            callbacks: {
              afterBody: function (items) {
                var extra = [
                  '关键回归场景要求 100%',
                  '关键字段覆盖率 ≥98%',
                  '关键工具成功率 ≥99.5%',
                  '绕过须为 0（0 容忍层，独立判）',
                  '失败归因覆盖率 ≥95%'
                ];
                return extra[items[0].dataIndex] ? ['补充：' + extra[items[0].dataIndex]] : [];
              }
            }
          }
        }
      })
    });
    built.m2 = true;
  }

  /* ---------- 图 3：完成率四件套 A/B 对照 ---------- */
  function buildAB() {
    var p = palette();
    instances.chartAB = new Chart(document.getElementById('chartAB'), {
      type: 'bar',
      data: {
        labels: ['完成率（%）', '平均步数（步）', '工具失败率（%）'],
        datasets: [
          {
            label: '系统 A',
            data: [95, 12, 8],
            backgroundColor: p.red + '38',
            borderColor: p.red,
            borderWidth: 1.6, borderRadius: 6, borderSkipped: false, maxBarThickness: 52
          },
          {
            label: '系统 B',
            data: [92, 3, 2],
            backgroundColor: p.green + '38',
            borderColor: p.green,
            borderWidth: 1.6, borderRadius: 6, borderSkipped: false, maxBarThickness: 52
          }
        ]
      },
      options: Object.assign(baseOptions({
        x: axis(p),
        y: Object.assign(axis(p, { title: '数值（三项量纲不同，分并列示）' }), { beginAtZero: true })
      }), {
        plugins: {
          legend: { display: true, labels: { color: p.dim, font: { size: 11.5 }, usePointStyle: true, pointStyle: 'roundedRect', boxWidth: 12, padding: 14 } },
          tooltip: {
            backgroundColor: p.surface, titleColor: p.text, bodyColor: p.dim,
            borderColor: p.border, borderWidth: 1, padding: 10, cornerRadius: 8,
            callbacks: {
              afterBody: function (items) {
                return ['', '结论：B 完成率略低，但步数与失败率大幅优于 A —— 综合落地价值 B 远胜 A。'];
              }
            }
          }
        }
      })
    });
    built.m3 = true;
  }

  /* ---------- 图 4：两段式阈值 ---------- */
  function buildTwoPhase() {
    var p = palette();
    instances.chartTwoPhase = new Chart(document.getElementById('chartTwoPhase'), {
      type: 'bar',
      data: {
        labels: ['AI 自动解决率', '准确率', '满意度（换算百分制）', '人工节省率'],
        datasets: [
          {
            label: '首月合格线',
            data: [55, 80, 76, 30],
            backgroundColor: p.warn + '38',
            borderColor: p.warn,
            borderWidth: 1.6, borderRadius: 6, borderSkipped: false, maxBarThickness: 46
          },
          {
            label: '3 个月目标线',
            data: [62, 90, 84, 40],
            backgroundColor: p.green + '38',
            borderColor: p.green,
            borderWidth: 1.6, borderRadius: 6, borderSkipped: false, maxBarThickness: 46
          }
        ]
      },
      options: Object.assign(baseOptions({
        x: axis(p),
        y: Object.assign(axis(p, { title: '百分比（%）' }), { beginAtZero: true, suggestedMax: 96 })
      }), {
        plugins: {
          legend: { display: true, labels: { color: p.dim, font: { size: 11.5 }, usePointStyle: true, pointStyle: 'roundedRect', boxWidth: 12, padding: 14 } },
          tooltip: {
            backgroundColor: p.surface, titleColor: p.text, bodyColor: p.dim,
            borderColor: p.border, borderWidth: 1, padding: 10, cornerRadius: 8,
            callbacks: {
              afterBody: function (items) {
                var raw = ['首月 ≥55% → 3 月 ≥62%', '首月 ≥80% → 3 月 ≥90%', '首月 ≥3.8/5 → 3 月 ≥4.2/5', '首月 ≥30% → 3 月 ≥40%'];
                var i = items[0].dataIndex;
                return ['原始口径：' + raw[i]].concat(i === 3 ? ['3 月另含复购提升 ≥5%'] : []);
              }
            }
          }
        }
      })
    });
    built.m4 = true;
  }

  /* ---------- 图 5：分层评估成本占比 ---------- */
  function buildCost() {
    var p = palette();
    instances.chartCost = new Chart(document.getElementById('chartCost'), {
      type: 'doughnut',
      data: {
        labels: ['L1 规则检查（$0 / 例）', 'L2 小模型 judge（~$0.001 / 例）', 'L3 大模型 judge + 人工（~$0.05 / 例）'],
        datasets: [{
          data: [80, 15, 5],
          backgroundColor: [p.green + '55', p.blue + '55', p.accent + '55'],
          borderColor: [p.green, p.blue, p.accent],
          borderWidth: 1.6,
          hoverOffset: 8
        }]
      },
      options: Object.assign(baseOptions({ legend: true }), {
        cutout: '58%',
        plugins: {
          legend: {
            display: true,
            position: 'bottom',
            labels: { color: p.dim, font: { size: 11.5 }, usePointStyle: true, pointStyle: 'circle', boxWidth: 9, padding: 12 }
          },
          tooltip: {
            backgroundColor: p.surface, titleColor: p.text, bodyColor: p.dim,
            borderColor: p.border, borderWidth: 1, padding: 10, cornerRadius: 8,
            callbacks: {
              label: function (ctx) { return ctx.label + '：占比 ' + ctx.parsed + '%'; },
              afterBody: function () {
                return ['', '对照：$0.02/例 → 90%　纯大模型 $0.05/例 → 85%　纯人工 $5/例 → 95%', '省钱路径与牺牲量须一并写明。'];
              }
            }
          }
        }
      })
    });
    built.m5 = true;
  }

  var BUILDERS = { m1: buildPoints, m2: buildSLO, m3: buildAB, m4: buildTwoPhase, m5: buildCost };

  function ensure(panel) {
    if (!BUILDERS[panel] || built[panel]) return;
    if (typeof Chart === 'undefined') return;
    var map = { m1: 'chartPoints', m2: 'chartSLO', m3: 'chartAB', m4: 'chartTwoPhase', m5: 'chartCost' };
    if (!document.getElementById(map[panel])) return;
    try { BUILDERS[panel](); } catch (e) { console.warn('chart build failed:', panel, e); }
  }

  function init() {
    if (typeof Chart === 'undefined') {
      console.warn('Chart.js 未加载（CDN 不可达），图表已跳过，页面其余功能不受影响。');
      return;
    }
    Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
    Chart.defaults.font.size = 11.5;
    // 首屏可见的 Tab 立即构建
    ensure('m1');
  }

  function refresh() {
    if (typeof Chart === 'undefined') return;
    Object.keys(instances).forEach(function (k) {
      var inst = instances[k];
      if (!inst) return;
      var p = palette();
      // 刷新配色相关配置
      inst.options.plugins.legend.labels.color = p.dim;
      inst.options.plugins.tooltip.backgroundColor = p.surface;
      inst.options.plugins.tooltip.titleColor = p.text;
      inst.options.plugins.tooltip.bodyColor = p.dim;
      inst.options.plugins.tooltip.borderColor = p.border;
      if (inst.options.scales && inst.options.scales.x) {
        inst.options.scales.x.ticks.color = p.dim;
        inst.options.scales.x.grid.color = p.border;
      }
      if (inst.options.scales && inst.options.scales.y) {
        inst.options.scales.y.ticks.color = p.dim;
        inst.options.scales.y.grid.color = p.border;
      }
      inst.update('none');
    });
  }

  return { init: init, ensure: ensure, refresh: refresh };
})();
