# InferBench-Media Project Brief

> This document is an independent onboarding brief for agents and contributors. It is not part of the project memory system. Project memory lives in `AGENTS.md` and `.ai-dev/`.

## Source Context

This project brief is distilled from:

- `D:\Atlas\Discussions\AI-Infra\open-source-inference-roadmap-0624\README.md`
- `D:\Atlas\Discussions\AI-Infra\open-source-inference-roadmap-0624\01-inferbench-media.md`

The source documents describe a five-project AI inference deployment roadmap:

```text
InferBench-Media
  -> MediaInferKit
  -> CppInferSDK
  -> EdgeQuantLab
  -> MediaInferLab
```

`InferBench-Media` is the first project. Its role is to build the measurement and evidence layer before later projects add media pipelines, C++ runtime abstraction, quantization decisions, and deployment governance.

## One-Line Positioning

`InferBench-Media` is a reproducible, task-aware inference benchmarking toolkit for vision, audio, and later local AI workloads.

It measures runtime-only and end-to-end media pipelines with stage-level latency, throughput, resource usage, correctness checks, and reproducible reports.

## Why This Project Exists

The project should not become another model demo or a replacement for existing runtime benchmark tools.

Existing tools such as ONNX Runtime profiling, TensorRT `trtexec`, OpenVINO `benchmark_app`, and MLPerf answer parts of the performance question. `InferBench-Media` fills the layer around them:

```text
What exactly was measured?
Was the result correct?
Were warmup and measurement separated?
Was GPU asynchronous execution timed honestly?
Were input, model, preprocessing, runtime, and environment fixed?
Can two reports be compared by machine, or only by guesswork?
```

The central value is not "support many models." The central value is a trustworthy way to answer:

> Is this deployment方案 actually faster, correct, reproducible, and comparable?

## Repository Boundary

This directory is the formal project root:

```text
D:\Atlas\Projects\Computer\AI-Infra\AI Infer\inferbench-media
```

The parent directory remains a shared model and data asset workspace:

```text
D:\Atlas\Projects\Computer\AI-Infra\AI Infer
```

Initial shared assets already live outside this project directory:

```text
../models/
../data/
../scripts/assets/
../tests/
```

Early implementation may consume those shared anchors, but the benchmark tool itself should keep its code, recipes, reports, docs, and project memory inside `inferbench-media`.

## What This Project Should Do

The project should standardize:

- experiment configuration
- environment snapshot collection
- target and workload description
- cold start, warmup, and measurement lifecycle
- stage-level timing
- FPS, RTF, latency, and resource metric definitions
- correctness validation
- raw result storage
- JSON and Markdown report generation
- result comparison and regression gates

## What This Project Should Not Do Yet

The first versions should not:

- reimplement ONNX Runtime, TensorRT, OpenVINO, YOLO, Whisper, or llama.cpp
- become a production-grade audio/video pipeline framework
- train models
- search quantization strategies automatically
- publish a public hardware leaderboard
- claim MLPerf equivalence
- support every model, runtime, device, and input source
- hide correctness failures behind good-looking performance numbers

## First Anchor Workloads

The roadmap uses two long-running task anchors.

Vision anchor:

```text
YOLOX-Tiny
  -> COCO images
  -> local video files
  -> ONNX Runtime CPU/CUDA
  -> later TensorRT/OpenVINO/quantized candidates
```

Audio anchor:

```text
Whisper Base
  -> short and long audio
  -> whisper.cpp external target
  -> RTF and offline ASR reports
```

Audio is intentionally later than the first vision slice.

## Initial Implementation Slice

The realistic first two weeks are:

Week 1: define the method before expanding features.

```text
README problem statement
project boundary and non-goals
five-level benchmark model
core metric definitions
ExperimentSpec draft
RunResult draft
YOLO data-flow diagram
benchmark code review checklist
```

Week 2: run the smallest trustworthy loop.

```text
fixed YOLO ONNX model
fixed image input
ONNX Runtime CPU
prepare / warmup / measure lifecycle
preprocess / inference / postprocess timing
raw JSON result
Markdown summary
basic golden-sample validation
```

Do not start with video, CUDA, TensorRT, resource sampling, or multi-runtime comparison until the fixed-image CPU loop produces a clear and reproducible result.

## Benchmark Levels

The roadmap defines five measurement levels:

```text
L0: startup and model loading
L1: runtime-only microbenchmark
L2: task pipeline benchmark
L3: media end-to-end benchmark
L4: real-time or service benchmark
```

Early versions should focus on L0, L1, and a minimal L2 for vision.

## Core Data Contracts

The first stable concepts should be:

- `ExperimentSpec`: full experimental plan
- `EnvironmentSnapshot`: OS, CPU, GPU, driver, runtime, Python/C++ versions, model/input hashes, git commit, and key runtime config
- `StageEvent`: per-sample stage event with explicit clock domain
- `RunResult`: run status, environment, target, workload, validation, raw samples, aggregate metrics, warnings, errors, and reproduction command

Important rule:

```text
Do not add absolute timestamps from different clock domains.
Do not write unavailable metrics as 0.
```

## Metrics That Matter

Generic metrics:

- model load time
- cold first result time
- end-to-end latency
- queue wait
- throughput
- error rate
- CPU memory
- GPU memory
- CPU/GPU utilization when available
- validation status

Each latency metric should keep distribution statistics:

```text
count, min, max, mean, standard deviation, p50, p90, p95, p99 when sample size is sufficient
```

Vision-specific metrics:

- source FPS
- decode FPS
- inference FPS
- effective FPS
- drop rate
- frame age
- preprocess time
- postprocess time
- render time, if rendering is enabled

Audio-specific metrics for later versions:

- RTF
- audio duration
- chunk latency
- first partial latency
- final result latency
- endpoint delay
- resample, VAD, and decoder time

## Correctness Before Performance

A fast wrong result is not an optimization.

Each formal benchmark should distinguish:

```text
VALID
INVALID
PARTIAL
UNVERIFIED
```

Vision validation should begin with:

- output shape checks
- NaN/Inf checks
- legal bbox coordinates
- legal class IDs
- confidence range checks
- basic golden-sample comparison with tolerances

## First Architecture Shape

The system has a control plane and a data plane.

Control plane:

```text
CLI / Config Loader
  -> Experiment Planner
  -> Environment Probe + Validation
  -> Benchmark Lifecycle Controller
  -> Aggregator
  -> Comparator
  -> Reporter
  -> Gate
```

Data plane:

```text
Media Source
  -> Decode
  -> Preprocess
  -> Runtime
  -> Postprocess
  -> Sink
```

A `StageRecorder` should observe stage spans without turning the first version into a full media framework.

## Early Interface Principle

Do not over-abstract on day one.

The first target interface can stay coarse:

```python
class BenchmarkTarget:
    def prepare(self, context):
        ...

    def warmup(self, sample):
        ...

    def run(self, sample, recorder):
        ...

    def synchronize(self):
        ...
```

Split finer abstractions only after the benchmark loop exposes real duplication or runtime-specific pressure.

## Agent Review Checklist

Agents working on this project must be especially careful about benchmark truthfulness:

- Do not use `time.time()` for precise interval timing.
- Do not mix warmup samples into measured results.
- Do not silently delete outliers.
- Do not silently fall back from CUDA to CPU.
- Do not compare runs with different inputs, shapes, dtype, precision, preprocessing, or measurement levels.
- Do not forget model and input hashes.
- Do not let logging, rendering, or file writes contaminate the hot path.
- Do not write `unavailable` metrics as `0`.
- Do not use `shell=True` with user-composed command strings.
- Do not catch exceptions and continue as if the run were valid.
- Do not report performance without correctness validation.

## First-Read Guidance For Future Agents

When receiving this project for the first time:

1. Read `AGENTS.md`.
2. Read `.ai-dev/README.md`, `.ai-dev/RULES.md`, and `.ai-dev/current/active.md`.
3. Read this `PROJECT_BRIEF.md`.
4. Check the parent asset workspace `../README.md`, `../models/README.md`, and `../data/README.md`.
5. Treat roadmap discussion docs as background, not as implemented code.

