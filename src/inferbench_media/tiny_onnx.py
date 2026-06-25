from __future__ import annotations

from pathlib import Path

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper


def create_tiny_image_model(path: Path, input_shape: tuple[int, int, int, int] = (1, 3, 64, 64)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    weights = np.array(
        [
            [0.25, -0.5, 0.75],
            [0.1, 0.2, -0.3],
            [0.4, 0.05, 0.15],
        ],
        dtype=np.float32,
    )
    bias = np.array([0.1, 0.2, 0.3], dtype=np.float32)

    graph = helper.make_graph(
        [
            helper.make_node("ReduceMean", ["images"], ["pooled"], axes=[2, 3], keepdims=0),
            helper.make_node("MatMul", ["pooled", "weights"], ["matmul_out"]),
            helper.make_node("Add", ["matmul_out", "bias"], ["detections"]),
        ],
        "fixed_yolo_contract",
        [helper.make_tensor_value_info("images", TensorProto.FLOAT, list(input_shape))],
        [helper.make_tensor_value_info("detections", TensorProto.FLOAT, [1, 3])],
        [
            numpy_helper.from_array(weights, name="weights"),
            numpy_helper.from_array(bias, name="bias"),
        ],
    )
    model = helper.make_model(
        graph,
        producer_name="inferbench-media",
        opset_imports=[helper.make_operatorsetid("", 13)],
    )
    model.ir_version = 8
    onnx.checker.check_model(model)
    onnx.save(model, path)

