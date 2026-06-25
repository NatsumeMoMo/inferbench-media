from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

from PIL import Image

from .runner import run_benchmark
from .tiny_onnx import create_tiny_image_model


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="InferBench-Media fixed image benchmark CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a benchmark from a YAML config.")
    run_parser.add_argument("config", type=Path)
    run_parser.add_argument("--output-root", type=Path, default=Path("results"))
    run_parser.add_argument("--run-id", default=None)
    run_parser.add_argument("--iterations", type=int, default=None)

    demo_parser = subparsers.add_parser("demo", help="Run a generated fixed-image ONNX CPU demo.")
    demo_parser.add_argument("--output-root", type=Path, default=Path("results"))
    demo_parser.add_argument("--run-id", default=None)
    demo_parser.add_argument("--iterations", type=int, default=1)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            run_id = args.run_id or default_run_id()
            result_dir = run_benchmark(args.config, args.output_root, run_id, args.iterations)
            print(result_dir)
            return 0
        if args.command == "demo":
            run_id = args.run_id or default_run_id()
            config_path = create_demo_assets(args.output_root, args.iterations)
            result_dir = run_benchmark(config_path, args.output_root, run_id)
            print(result_dir)
            return 0
    except FileNotFoundError as exc:
        print(f"missing_artifact: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"invalid_config: {exc}", file=sys.stderr)
        return 2
    parser.error(f"unknown command: {args.command}")
    return 2


def default_run_id() -> str:
    return f"{dt.datetime.now().strftime('%Y%m%d')}-yolo-ort-cpu-image"


def create_demo_assets(output_root: Path, iterations: int) -> Path:
    assets_dir = output_root / "_demo_assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    image_path = assets_dir / "fixed_image.png"
    model_path = assets_dir / "fixed_yolo_contract.onnx"
    config_path = assets_dir / "config.yaml"

    Image.new("RGB", (320, 192), (50, 120, 200)).save(image_path)
    create_tiny_image_model(model_path, input_shape=(1, 3, 64, 64))
    config_path.write_text(
        "\n".join(
            [
                'schema_version: "0.1"',
                "experiment:",
                "  name: yolo-ort-cpu-image",
                f"  iterations: {iterations}",
                "target:",
                "  name: fixed-yolo-contract",
                "  task: object_detection",
                f"  model_path: {model_path.name}",
                "  runtime:",
                "    name: onnxruntime",
                "    provider: CPUExecutionProvider",
                "preprocess:",
                "  input_shape: [1, 3, 64, 64]",
                "  color: RGB",
                "  resize: letterbox",
                "  padding_value: 114",
                "workload:",
                "  input:",
                "    type: image_file",
                f"    path: {image_path.name}",
                "validation:",
                "  mode: output_structure",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return config_path


if __name__ == "__main__":
    raise SystemExit(main())
