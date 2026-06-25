# Fixed Image ORT CPU Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first fixed-image ONNX Runtime CPU benchmark loop that records stage timings and writes JSONL, JSON, Chinese Markdown, and HTML reports.

**Architecture:** Keep v0 minimal: a Python CLI loads one YAML config, reads one fixed image, loads one fixed ONNX model with CPUExecutionProvider, runs one or more measured iterations, validates output structure, aggregates metrics, and renders reports. The default recipe points at the parent YOLOX-Tiny ONNX artifact path, while tests use a generated tiny ONNX contract model because the real YOLOX ONNX artifact is not yet present.

**Tech Stack:** Python 3.13, ONNX Runtime CPU, Pillow, NumPy, PyYAML, unittest.

---

### File Map

- Create `pyproject.toml`: package metadata, console script, runtime dependencies.
- Create `src/inferbench_media/cli.py`: command-line entrypoint.
- Create `src/inferbench_media/config.py`: YAML loading and default config generation.
- Create `src/inferbench_media/image.py`: fixed preprocessing for image-to-NCHW float32 tensor.
- Create `src/inferbench_media/runner.py`: ORT CPU lifecycle, timing, validation, aggregation, and artifact writing.
- Create `src/inferbench_media/reporting.py`: Chinese Markdown and HTML report renderers.
- Create `src/inferbench_media/tiny_onnx.py`: test/support generator for a fixed tiny image ONNX model.
- Create `recipes/yolo_ort_cpu_image.yaml`: default fixed YOLOX ONNX CPU image recipe.
- Create `tests/test_fixed_image_benchmark.py`: end-to-end behavior tests using a generated tiny ONNX model and generated image.
- Modify `.ai-dev/current/active.md`: record the active feature task.

### Task 1: Active Task Record

- [ ] **Step 1: Record current task metadata**

Write `.ai-dev/current/active.md` with `FEATURE-0001`, user requirements, acceptance criteria, risks, and next step.

### Task 2: Failing End-to-End Test

- [ ] **Step 1: Write the failing test**

Create `tests/test_fixed_image_benchmark.py` with a unittest that imports `inferbench_media.runner.run_benchmark`, creates a generated PNG and tiny ONNX model, runs three iterations, and asserts `config.yaml`, `events.jsonl`, `summary.json`, `report.md`, and `report.html` exist with required metrics.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_fixed_image_benchmark -v`

Expected: fails because `inferbench_media` does not exist.

### Task 3: Minimal Package And Runner

- [ ] **Step 1: Add package files**

Create the package, model/image helpers, runner, and report renderer.

- [ ] **Step 2: Run test to verify it passes**

Run: `python -m unittest tests.test_fixed_image_benchmark -v`

Expected: passes.

### Task 4: CLI And Default Recipe

- [ ] **Step 1: Write CLI test coverage**

Extend the unittest to call `python -m inferbench_media.cli run <config> --output-root <tmp> --run-id 20260625-yolo-ort-cpu-image` and assert artifacts exist.

- [ ] **Step 2: Verify the new CLI test fails before CLI code exists**

Run: `python -m unittest tests.test_fixed_image_benchmark -v`

Expected: CLI invocation fails.

- [ ] **Step 3: Implement CLI and default recipe**

Add `cli.py`, console script metadata, and `recipes/yolo_ort_cpu_image.yaml`.

- [ ] **Step 4: Verify tests pass**

Run: `python -m unittest tests.test_fixed_image_benchmark -v`

Expected: passes.

### Task 5: Local Self-Test

- [ ] **Step 1: Install runtime dependencies when missing**

Run: `python -m pip install -e .`

- [ ] **Step 2: Run the benchmark with generated fixed ONNX and image**

Run: `python -m inferbench_media.cli demo --output-root results --run-id 20260625-yolo-ort-cpu-image --iterations 3`

Expected: creates the required result directory and all five artifacts.

- [ ] **Step 3: Run all tests**

Run: `python -m unittest discover -s tests -v`

Expected: all tests pass.

### Task 6: GitHub Publish

- [ ] **Step 1: Initialize a git repository in `inferbench-media` after self-test**

Run: `git init -b main`.

- [ ] **Step 2: Inspect and stage only intended project files**

Run: `git status -sb`, then stage source, docs, recipes, tests, project memory, and generated sample result only if intended.

- [ ] **Step 3: Commit**

Run: `git commit -m "FEATURE-0001: add fixed image ORT CPU benchmark"`.

- [ ] **Step 4: Create and push public GitHub repository**

Run: `gh repo create inferbench-media --public --source . --remote origin --push`.

