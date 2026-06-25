# InferBench-Media

First implementation slice for the AI inference deployment roadmap.

The current scope is deliberately narrow:

```text
fixed image
  -> fixed ONNX model
  -> ONNX Runtime CPU
  -> fixed preprocessing
  -> inference
  -> output-structure validation
  -> stage timing
  -> JSONL / JSON / Markdown / HTML reports
```

The default recipe is `recipes/yolo_ort_cpu_image.yaml`. It points at the parent asset workspace's planned YOLOX-Tiny ONNX export:

```text
../models/yolox_tiny_416_fp32.onnx
```

If that artifact is missing, the run fails clearly instead of pretending YOLOX is available. Use the demo command to validate the benchmark/report pipeline with a generated tiny ONNX contract model.

## Setup

```powershell
python -m pip install -e .
```

## Run Demo

```powershell
python -m inferbench_media.cli demo --output-root results --run-id 20260625-yolo-ort-cpu-image --iterations 3
```

## Run Default Recipe

```powershell
python -m inferbench_media.cli run recipes/yolo_ort_cpu_image.yaml --iterations 1
```

Expected outputs:

```text
results/
  2026xxxx-yolo-ort-cpu-image/
    config.yaml
    events.jsonl
    summary.json
    report.md
    report.html
```

`report.md` is Chinese. `report.html` contains inline visual charts and requires no external assets.

