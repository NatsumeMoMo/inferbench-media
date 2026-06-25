from __future__ import annotations

import json
import math
import platform
import statistics
import time
from pathlib import Path
from typing import Any

import numpy as np
import onnxruntime as ort

from .config import copy_config, get_iterations, load_config, resolve_config_path
from .image import load_image_tensor
from .reporting import write_html_report, write_markdown_report


NUMERIC_METRICS = [
    "model_load_ms",
    "preprocess_ms",
    "inference_ms",
    "postprocess_ms",
    "e2e_ms",
    "latency_mean",
    "latency_p50",
    "latency_p95",
    "throughput_items_s",
]


def run_benchmark(
    config_path: Path,
    output_root: Path,
    run_id: str,
    iterations_override: int | None = None,
) -> Path:
    config_path = config_path.resolve()
    output_root = output_root.resolve()
    config = load_config(config_path)
    iterations = get_iterations(config, iterations_override)

    result_dir = output_root / run_id
    result_dir.mkdir(parents=True, exist_ok=True)
    copy_config(config_path, result_dir)

    model_path = resolve_config_path(config_path, config["target"]["model_path"])
    image_path = resolve_config_path(config_path, config["workload"]["input"]["path"])
    if not model_path.exists():
        raise FileNotFoundError(f"model_path does not exist: {model_path}")
    if not image_path.exists():
        raise FileNotFoundError(f"image path does not exist: {image_path}")

    provider = config.get("target", {}).get("runtime", {}).get("provider", "CPUExecutionProvider")
    if provider != "CPUExecutionProvider":
        raise ValueError("first benchmark slice only supports CPUExecutionProvider")

    events: list[dict[str, Any]] = []
    model_start = time.perf_counter_ns()
    session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
    model_end = time.perf_counter_ns()
    if session.get_providers()[0] != "CPUExecutionProvider":
        raise RuntimeError(f"unexpected ONNX Runtime provider order: {session.get_providers()}")
    model_load_ms = ns_to_ms(model_end - model_start)
    events.append(stage_event("model_load", None, model_start, model_end, "ok"))

    input_meta = session.get_inputs()[0]
    input_name = input_meta.name
    input_shape = tuple(int(value) for value in config["preprocess"]["input_shape"])
    padding_value = int(config.get("preprocess", {}).get("padding_value", 114))

    iteration_metrics: list[dict[str, float]] = []
    validation_status = "VALID"
    validation_details: list[str] = []

    for iteration in range(1, iterations + 1):
        e2e_start = time.perf_counter_ns()

        pre_start = time.perf_counter_ns()
        tensor = load_image_tensor(image_path, input_shape, padding_value=padding_value)
        pre_end = time.perf_counter_ns()
        events.append(stage_event("preprocess", iteration, pre_start, pre_end, "ok"))

        infer_start = time.perf_counter_ns()
        outputs = session.run(None, {input_name: tensor})
        infer_end = time.perf_counter_ns()
        events.append(stage_event("inference", iteration, infer_start, infer_end, "ok"))

        post_start = time.perf_counter_ns()
        output_status, output_details = validate_outputs(outputs)
        post_end = time.perf_counter_ns()
        events.append(stage_event("postprocess", iteration, post_start, post_end, output_status.lower()))

        e2e_end = time.perf_counter_ns()
        events.append(stage_event("e2e", iteration, e2e_start, e2e_end, output_status.lower()))

        if output_status != "VALID":
            validation_status = "INVALID"
        validation_details.extend(output_details)

        e2e_ms = ns_to_ms(e2e_end - e2e_start)
        iteration_metrics.append(
            {
                "model_load_ms": model_load_ms,
                "preprocess_ms": ns_to_ms(pre_end - pre_start),
                "inference_ms": ns_to_ms(infer_end - infer_start),
                "postprocess_ms": ns_to_ms(post_end - post_start),
                "e2e_ms": e2e_ms,
                "latency_mean": e2e_ms,
                "latency_p50": e2e_ms,
                "latency_p95": e2e_ms,
                "throughput_items_s": 1000.0 / e2e_ms if e2e_ms > 0 else 0.0,
            }
        )

    e2e_values = [item["e2e_ms"] for item in iteration_metrics]
    metrics = {
        "model_load_ms": model_load_ms,
        "preprocess_ms": statistics.mean(item["preprocess_ms"] for item in iteration_metrics),
        "inference_ms": statistics.mean(item["inference_ms"] for item in iteration_metrics),
        "postprocess_ms": statistics.mean(item["postprocess_ms"] for item in iteration_metrics),
        "e2e_ms": statistics.mean(e2e_values),
        "latency_mean": statistics.mean(e2e_values),
        "latency_p50": percentile(e2e_values, 50),
        "latency_p95": percentile(e2e_values, 95),
        "throughput_items_s": 1000.0 * len(e2e_values) / sum(e2e_values) if sum(e2e_values) > 0 else 0.0,
    }
    metric_stats = {key: stats([item[key] for item in iteration_metrics]) for key in NUMERIC_METRICS}
    metric_stats["latency_mean"] = stats(e2e_values)
    metric_stats["latency_p50"] = stats(e2e_values)
    metric_stats["latency_p95"] = stats(e2e_values)

    summary = {
        "schema_version": "0.1",
        "run_id": run_id,
        "status": "completed" if validation_status == "VALID" else "completed_with_validation_errors",
        "iteration_count": iterations,
        "validation_status": validation_status,
        "metrics": metrics,
        "metric_stats": metric_stats,
        "iteration_metrics": iteration_metrics,
        "target": {
            "name": config.get("target", {}).get("name", "fixed-yolo-onnx"),
            "task": config.get("target", {}).get("task", "object_detection"),
            "model_path": str(model_path),
            "runtime": "onnxruntime",
            "provider": "CPUExecutionProvider",
        },
        "workload": {
            "type": "image_file",
            "image_path": str(image_path),
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "onnxruntime": ort.__version__,
        },
        "validation_details": validation_details,
    }

    write_events(result_dir / "events.jsonl", events)
    write_json(result_dir / "summary.json", summary)
    write_markdown_report(summary, result_dir / "report.md")
    write_html_report(summary, result_dir / "report.html")
    return result_dir


def validate_outputs(outputs: list[Any]) -> tuple[str, list[str]]:
    if not outputs:
        return "INVALID", ["ONNX Runtime returned no outputs."]
    details = []
    for index, output in enumerate(outputs):
        array = np.asarray(output)
        if array.size == 0:
            return "INVALID", [f"output[{index}] is empty."]
        if not np.all(np.isfinite(array)):
            return "INVALID", [f"output[{index}] contains NaN or Inf."]
        details.append(f"output[{index}] shape={list(array.shape)} dtype={array.dtype}")
    return "VALID", details


def stage_event(stage: str, iteration: int | None, start_ns: int, end_ns: int, status: str) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "iteration": iteration,
        "stage": stage,
        "clock_domain": "cpu_perf_counter_ns",
        "start_ns": start_ns,
        "end_ns": end_ns,
        "duration_ms": ns_to_ms(end_ns - start_ns),
        "status": status,
    }


def ns_to_ms(duration_ns: int) -> float:
    return duration_ns / 1_000_000.0


def percentile(values: list[float], percent: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * percent / 100.0
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[int(rank)]
    weight = rank - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def stats(values: list[float]) -> dict[str, float]:
    return {
        "min": min(values),
        "max": max(values),
        "mean": statistics.mean(values),
    }


def write_events(path: Path, events: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

