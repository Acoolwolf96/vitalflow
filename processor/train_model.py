import numpy as np
import onnx
from onnx import helper, checker, TensorProto

# Create a simple ONNX model that takes 64 features and outputs a probability
# This avoids skl2onnx dependency entirely

# Input: 64-dim feature vector
input_tensor = helper.make_tensor_value_info('float_input', TensorProto.FLOAT, [None, 64])
output_tensor = helper.make_tensor_value_info('output', TensorProto.FLOAT, [None, 1])

# Create a simple model: take mean of features and apply sigmoid
node1 = helper.make_node(
    'ReduceMean',
    inputs=['float_input'],
    outputs=['mean'],
    keepdims=1
)

node2 = helper.make_node(
    'Sigmoid',
    inputs=['mean'],
    outputs=['output']
)

graph = helper.make_graph(
    [node1, node2],
    'simple_health_model',
    [input_tensor],
    [output_tensor]
)

model = helper.make_model(graph, producer_name='vitalflow')
checker.check_model(model)

with open("breathing_model.onnx", "wb") as f:
    f.write(model.SerializeToString())

print("Simple ONNX model saved as breathing_model.onnx")
print("Model input: float_input (64 features)")
print("Model output: output (probability between 0-1)")
