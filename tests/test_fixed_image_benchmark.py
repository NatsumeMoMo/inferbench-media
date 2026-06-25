import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


class FixedImageBenchmarkTests(unittest.TestCase):
    def test_demo_assets_config_uses_paths_resolvable_from_config_directory(self) -> None:
        from inferbench_media.cli import create_demo_assets
        from inferbench_media.runner import run_benchmark

        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                output_root = Path("results")
                config_path = create_demo_assets(output_root, iterations=2)

                result_dir = run_benchmark(
                    config_path=config_path,
                    output_root=output_root,
                    run_id="20260625-yolo-ort-cpu-image",
                )

                self.assertTrue((result_dir / "summary.json").exists())
                summary = json.loads((result_dir / "summary.json").read_text(encoding="utf-8"))
                self.assertEqual(summary["iteration_count"], 2)
            finally:
                os.chdir(old_cwd)

    def test_run_benchmark_writes_requested_artifacts_and_metrics(self) -> None:
        from inferbench_media.runner import run_benchmark
        from inferbench_media.tiny_onnx import create_tiny_image_model

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            image_path = tmp / "fixed.png"
            model_path = tmp / "fixed_yolo_contract.onnx"
            config_path = tmp / "config.yaml"
            output_root = tmp / "results"

            Image.new("RGB", (300, 180), (32, 96, 160)).save(image_path)
            create_tiny_image_model(model_path, input_shape=(1, 3, 64, 64))
            config_path.write_text(
                "\n".join(
                    [
                        'schema_version: "0.1"',
                        "experiment:",
                        "  name: yolo-ort-cpu-image",
                        "  iterations: 3",
                        "target:",
                        "  name: fixed-yolo-contract",
                        "  task: object_detection",
                        f"  model_path: {model_path.as_posix()}",
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
                        f"    path: {image_path.as_posix()}",
                        "validation:",
                        "  mode: output_structure",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result_dir = run_benchmark(
                config_path=config_path,
                output_root=output_root,
                run_id="20260625-yolo-ort-cpu-image",
            )

            self.assertEqual(result_dir.name, "20260625-yolo-ort-cpu-image")
            for name in ["config.yaml", "events.jsonl", "summary.json", "report.md", "report.html"]:
                self.assertTrue((result_dir / name).exists(), name)

            events = [
                json.loads(line)
                for line in (result_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            stages = {event["stage"] for event in events}
            self.assertIn("model_load", stages)
            self.assertIn("preprocess", stages)
            self.assertIn("inference", stages)
            self.assertIn("postprocess", stages)
            self.assertIn("e2e", stages)

            summary = json.loads((result_dir / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["validation_status"], "VALID")
            self.assertEqual(summary["iteration_count"], 3)
            for metric in [
                "model_load_ms",
                "preprocess_ms",
                "inference_ms",
                "postprocess_ms",
                "e2e_ms",
                "latency_mean",
                "latency_p50",
                "latency_p95",
                "throughput_items_s",
            ]:
                self.assertIn(metric, summary["metrics"])
                self.assertIn(metric, summary["metric_stats"])
                self.assertGreaterEqual(summary["metrics"][metric], 0)
                self.assertIn("min", summary["metric_stats"][metric])
                self.assertIn("max", summary["metric_stats"][metric])
                self.assertIn("mean", summary["metric_stats"][metric])

            report_md = (result_dir / "report.md").read_text(encoding="utf-8")
            self.assertIn("固定图片 ONNX Runtime CPU Benchmark 报告", report_md)
            self.assertIn("验证状态", report_md)

            report_html = (result_dir / "report.html").read_text(encoding="utf-8")
            self.assertIn("<svg", report_html)
            self.assertIn("阶段耗时", report_html)

    def test_cli_run_writes_requested_artifacts(self) -> None:
        from inferbench_media.tiny_onnx import create_tiny_image_model

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            image_path = tmp / "fixed.png"
            model_path = tmp / "fixed_yolo_contract.onnx"
            config_path = tmp / "config.yaml"
            output_root = tmp / "results"

            Image.new("RGB", (128, 96), (220, 40, 40)).save(image_path)
            create_tiny_image_model(model_path, input_shape=(1, 3, 64, 64))
            config_path.write_text(
                "\n".join(
                    [
                        'schema_version: "0.1"',
                        "experiment:",
                        "  name: yolo-ort-cpu-image",
                        "  iterations: 1",
                        "target:",
                        "  name: fixed-yolo-contract",
                        "  task: object_detection",
                        f"  model_path: {model_path.as_posix()}",
                        "  runtime:",
                        "    name: onnxruntime",
                        "    provider: CPUExecutionProvider",
                        "preprocess:",
                        "  input_shape: [1, 3, 64, 64]",
                        "workload:",
                        "  input:",
                        "    type: image_file",
                        f"    path: {image_path.as_posix()}",
                        "validation:",
                        "  mode: output_structure",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "inferbench_media.cli",
                    "run",
                    str(config_path),
                    "--output-root",
                    str(output_root),
                    "--run-id",
                    "20260625-yolo-ort-cpu-image",
                ],
                text=True,
                capture_output=True,
                cwd=Path(__file__).resolve().parents[1],
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            result_dir = output_root / "20260625-yolo-ort-cpu-image"
            self.assertTrue((result_dir / "summary.json").exists())
            self.assertTrue((result_dir / "report.html").exists())

    def test_cli_reports_missing_model_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            image_path = tmp / "fixed.png"
            config_path = tmp / "config.yaml"
            Image.new("RGB", (64, 64), (20, 20, 20)).save(image_path)
            config_path.write_text(
                "\n".join(
                    [
                        'schema_version: "0.1"',
                        "experiment:",
                        "  name: missing-model",
                        "  iterations: 1",
                        "target:",
                        "  name: missing",
                        "  task: object_detection",
                        "  model_path: missing.onnx",
                        "  runtime:",
                        "    name: onnxruntime",
                        "    provider: CPUExecutionProvider",
                        "preprocess:",
                        "  input_shape: [1, 3, 64, 64]",
                        "workload:",
                        "  input:",
                        "    type: image_file",
                        f"    path: {image_path.as_posix()}",
                        "validation:",
                        "  mode: output_structure",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "inferbench_media.cli",
                    "run",
                    str(config_path),
                    "--output-root",
                    str(tmp / "results"),
                ],
                text=True,
                capture_output=True,
                cwd=Path(__file__).resolve().parents[1],
            )

            self.assertEqual(completed.returncode, 2)
            self.assertIn("missing_artifact", completed.stderr)
            self.assertNotIn("Traceback", completed.stderr)


if __name__ == "__main__":
    unittest.main()
