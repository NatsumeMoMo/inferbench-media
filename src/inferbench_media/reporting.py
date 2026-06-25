from __future__ import annotations

import html
from pathlib import Path
from typing import Any


METRIC_LABELS = {
    "model_load_ms": "模型加载",
    "preprocess_ms": "前处理",
    "inference_ms": "推理",
    "postprocess_ms": "后处理/结构检查",
    "e2e_ms": "端到端",
    "latency_mean": "平均延迟",
    "latency_p50": "P50 延迟",
    "latency_p95": "P95 延迟",
    "throughput_items_s": "吞吐",
}


def write_markdown_report(summary: dict[str, Any], path: Path) -> None:
    metrics = summary["metrics"]
    lines = [
        "# 固定图片 ONNX Runtime CPU Benchmark 报告",
        "",
        "## 结论摘要",
        "",
        f"- 运行 ID：`{summary['run_id']}`",
        f"- 迭代次数：{summary['iteration_count']}",
        f"- 验证状态：`{summary['validation_status']}`",
        f"- 模型：`{summary['target']['model_path']}`",
        f"- 输入图片：`{summary['workload']['image_path']}`",
        "",
        "## 核心指标",
        "",
        "| 指标 | 数值 |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        label = METRIC_LABELS.get(key, key)
        unit = "items/s" if key == "throughput_items_s" else "ms"
        lines.append(f"| {label} (`{key}`) | {value:.4f} {unit} |")

    lines.extend(
        [
            "",
            "## 多轮统计",
            "",
            "| 指标 | 最小值 | 最大值 | 平均值 |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for key, stat in summary["metric_stats"].items():
        label = METRIC_LABELS.get(key, key)
        lines.append(f"| {label} | {stat['min']:.4f} | {stat['max']:.4f} | {stat['mean']:.4f} |")

    lines.extend(
        [
            "",
            "## 说明",
            "",
            "- 本报告只覆盖第一步固定图片、固定 ONNX 模型、ONNX Runtime CPU 的最小闭环。",
            "- 当前后处理为输出结构检查，不代表完整 YOLO bbox decode 或 NMS 已实现。",
            "- `validation_status=VALID` 表示输出结构、有限数值和基本运行状态通过检查。",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_html_report(summary: dict[str, Any], path: Path) -> None:
    metrics = summary["metrics"]
    stage_keys = ["model_load_ms", "preprocess_ms", "inference_ms", "postprocess_ms", "e2e_ms"]
    max_value = max(metrics[key] for key in stage_keys) or 1.0
    bars = []
    for index, key in enumerate(stage_keys):
        value = metrics[key]
        width = 420 * value / max_value
        y = 34 + index * 48
        label = html.escape(METRIC_LABELS[key])
        bars.append(
            f'<text x="0" y="{y + 17}" class="axis">{label}</text>'
            f'<rect x="138" y="{y}" width="{width:.2f}" height="26" rx="3"></rect>'
            f'<text x="{150 + width:.2f}" y="{y + 17}" class="value">{value:.3f} ms</text>'
        )

    rows = []
    for key, stat in summary["metric_stats"].items():
        label = html.escape(METRIC_LABELS.get(key, key))
        rows.append(
            "<tr>"
            f"<td>{label}</td>"
            f"<td>{stat['min']:.4f}</td>"
            f"<td>{stat['max']:.4f}</td>"
            f"<td>{stat['mean']:.4f}</td>"
            "</tr>"
        )

    document = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>InferBench-Media 固定图片 Benchmark 报告</title>
  <style>
    body {{ margin: 0; font-family: Arial, "Microsoft YaHei", sans-serif; color: #172033; background: #f6f8fb; }}
    header {{ padding: 28px 40px; background: #20324a; color: white; }}
    main {{ max-width: 1080px; margin: 0 auto; padding: 28px 24px 48px; }}
    section {{ margin: 0 0 28px; padding: 22px; background: white; border: 1px solid #dbe2ea; border-radius: 6px; }}
    h1, h2 {{ margin: 0 0 14px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }}
    .metric {{ padding: 14px; border: 1px solid #dbe2ea; border-radius: 6px; background: #fbfcfe; }}
    .metric span {{ display: block; color: #52606f; font-size: 13px; }}
    .metric strong {{ display: block; margin-top: 6px; font-size: 22px; }}
    svg {{ width: 100%; max-width: 760px; height: 280px; }}
    rect {{ fill: #2f80ed; }}
    .axis {{ fill: #344054; font-size: 13px; }}
    .value {{ fill: #172033; font-size: 12px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #e5eaf0; text-align: right; }}
    th:first-child, td:first-child {{ text-align: left; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 3px; }}
  </style>
</head>
<body>
  <header>
    <h1>固定图片 ONNX Runtime CPU Benchmark 报告</h1>
    <p>Run ID: <code>{html.escape(summary['run_id'])}</code> · 验证状态: <code>{html.escape(summary['validation_status'])}</code></p>
  </header>
  <main>
    <section>
      <h2>核心指标</h2>
      <div class="grid">
        {''.join(_metric_card(key, value) for key, value in metrics.items())}
      </div>
    </section>
    <section>
      <h2>阶段耗时</h2>
      <svg viewBox="0 0 640 280" role="img" aria-label="阶段耗时柱状图">
        {''.join(bars)}
      </svg>
    </section>
    <section>
      <h2>多轮统计</h2>
      <table>
        <thead><tr><th>指标</th><th>最小值</th><th>最大值</th><th>平均值</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""
    path.write_text(document, encoding="utf-8")


def _metric_card(key: str, value: float) -> str:
    label = html.escape(METRIC_LABELS.get(key, key))
    unit = "items/s" if key == "throughput_items_s" else "ms"
    return f'<div class="metric"><span>{label}</span><strong>{value:.3f} {unit}</strong></div>'

