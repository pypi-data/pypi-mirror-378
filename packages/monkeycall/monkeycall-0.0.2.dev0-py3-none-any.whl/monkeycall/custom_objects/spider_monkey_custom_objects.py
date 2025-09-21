from monkeycall.custom_objects.conv_blocks import ConvBlock, ResBlock, SEBlock
from monkeycall.custom_objects.custom_keras_layers import Reshape, Concat, ReduceSum, Softmax, Multiply, Loss

custom_objects = dict()
custom_objects["ConvBlock"] = ConvBlock
custom_objects["ResBlock"] = ResBlock
custom_objects["SEBlock"] = SEBlock
custom_objects["Reshape"] = Reshape
custom_objects["Concat"] = Concat
custom_objects["ReduceSum"] = ReduceSum
custom_objects["Softmax"] = Softmax
custom_objects["Multiply"] = Multiply
custom_objects["Loss"] = Loss
