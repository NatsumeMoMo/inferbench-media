# Current Task

Task ID: FEATURE-0001
Task Type: FEATURE
Status: AWAITING_USER_ACCEPTANCE
Branch: main
Started At: 2026-06-25T20:42:26+08:00
Base Commit: Atlas eac4238

## Goal

Implement the first fixed-image ONNX Runtime CPU benchmark loop for InferBench-Media.

## Background Loaded

- AGENTS.md
- .ai-dev/README.md
- .ai-dev/RULES.md
- .ai-dev/implemented/index.md
- .ai-dev/discussions/index.md
- PROJECT_BRIEF.md
- User-provided first-slice requirements from 2026-06-25

## User Requirements

- First step only: fixed image -> fixed YOLO ONNX model -> fixed ONNX Runtime CPU -> fixed preprocessing -> inference -> fixed postprocessing or output structure validation -> stage timing -> JSON output.
- Generate `results/2026xxxx-yolo-ort-cpu-image/` with `config.yaml`, `events.jsonl`, `summary.json`, Chinese `report.md`, and visual `report.html` with charts.
- Output metrics: `model_load_ms`, `preprocess_ms`, `inference_ms`, `postprocess_ms`, `e2e_ms`, `latency_mean`, `latency_p50`, `latency_p95`, `throughput_items_s`, `validation_status`.
- Support one run or specified iteration count.
- For multiple iterations, record min, max, and mean for each numeric metric.
- Use `C:\Software\anaconda3\envs\ai-infer-py311\python.exe` for Python work.
- Self-test first, then create a git repository and push to a public GitHub repository.

## Acceptance Criteria

- Tests cover the fixed image benchmark artifact contract.
- CLI can run a generated demo benchmark and produce all requested files.
- Reports are written, with `report.md` in Chinese and `report.html` containing visual charts.
- Missing real YOLOX ONNX artifact is represented honestly, not faked as a completed YOLOX export.
- A local git repository exists in `inferbench-media`, with the intended project files committed.
- Public GitHub repository push succeeds or any blocker is reported explicitly.

## Current Implementation Summary

- Implemented a Python package with CLI, fixed image preprocessing, ONNX Runtime CPU execution, output-structure validation, stage timing, JSONL events, JSON summary, Chinese Markdown report, and standalone HTML report with SVG charts.
- Added a demo mode that generates a fixed tiny ONNX contract model for self-test because the real YOLOX ONNX artifact is not present yet.
- Added default YOLOX CPU recipe that points at the planned parent asset path and fails clearly with `missing_artifact` while the ONNX artifact is absent.
- Verified with `ai-infer-py311`: `python -m unittest discover -s tests -v` passed, demo generated `results/20260625-yolo-ort-cpu-image`, and default YOLOX recipe fail-closed on missing `models/yolox_tiny_416_fp32.onnx`.

## Files Touched

- .ai-dev/current/active.md
- .gitignore
- AGENTS.md
- PROJECT_BRIEF.md
- README.md
- docs/superpowers/plans/2026-06-25-fixed-image-ort-cpu.md
- pyproject.toml
- recipes/yolo_ort_cpu_image.yaml
- src/inferbench_media/__init__.py
- src/inferbench_media/cli.py
- src/inferbench_media/config.py
- src/inferbench_media/image.py
- src/inferbench_media/reporting.py
- src/inferbench_media/runner.py
- src/inferbench_media/tiny_onnx.py
- tests/test_fixed_image_benchmark.py

## WIP Commits

- 311558d FEATURE-0001: add fixed image ORT CPU benchmark
- 242d693 FEATURE-0001: record benchmark task state

## Open Questions / Risks

- Parent asset workspace has `models/cache/yolox_tiny.pth`, but `models/yolox_tiny_416_fp32.onnx` is currently missing.
- The first self-test uses a generated tiny ONNX contract model while the real YOLOX ONNX artifact remains unavailable.
- Generated `results/` are ignored by git; rerun the demo command to regenerate local reports.

## Next Step

Await user review and explicit acceptance. If accepted, migrate this task to `.ai-dev/implemented/` in a follow-up memory update.

## User Acceptance

Accepted: No
Accepted At:
Final Commit:
