import tensorflow as tf


@tf.keras.utils.register_keras_serializable(package="custom")
class Reshape(tf.keras.layers.Layer):
    def __init__(self, target_shape, **kwargs):
        super(Reshape, self).__init__(**kwargs)
        self.target_shape = target_shape

    def call(self, x):
        return tf.reshape(x, self.target_shape)

    def get_config(self):
        # include our own arg so it’s saved/loaded
        config = super().get_config()
        config.update({"target_shape": self.target_shape})
        return config


@tf.keras.utils.register_keras_serializable(package="custom")
class Softmax(tf.keras.layers.Layer):
    def __init__(self, axis, **kwargs):
        super(Softmax, self).__init__(**kwargs)
        self.axis = axis

    def call(self, x):
        return tf.nn.softmax(x, axis=self.axis)

    def get_config(self):
        # include our own arg so it’s saved/loaded
        config = super().get_config()
        config.update({"axis": self.axis})
        return config


@tf.keras.utils.register_keras_serializable(package="custom")
class Concat(tf.keras.layers.Layer):
    def __init__(self, axis, **kwargs):
        super(Concat, self).__init__(**kwargs)
        self.axis = axis

    def call(self, x):
        return tf.concat(x, axis=self.axis)

    def get_config(self):
        # include our own arg so it’s saved/loaded
        config = super().get_config()
        config.update({"axis": self.axis})
        return config


@tf.keras.utils.register_keras_serializable(package="custom")
class ReduceSum(tf.keras.layers.Layer):
    def __init__(self, axis, keepdims, **kwargs):
        super(ReduceSum, self).__init__(**kwargs)
        self.axis = axis
        self.keepdims = keepdims

    def call(self, x):
        return tf.reduce_sum(x, axis=self.axis, keepdims=self.keepdims)

    def get_config(self):
        # include our own arg so it’s saved/loaded
        config = super().get_config()
        config.update({"axis": self.axis})
        config.update({"keepdims": self.keepdims})
        return config


@tf.keras.utils.register_keras_serializable(package="custom")
class Multiply(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super(Multiply, self).__init__(**kwargs)

    def call(self, x, y):
        return tf.multiply(x, y)


@tf.keras.utils.register_keras_serializable(package="custom")
class Loss(tf.keras.layers.Layer):
    def __init__(self, pos_weight, **kwargs):
        super(Loss, self).__init__(**kwargs)
        self.pos_weight = pos_weight

    def call(self, x, y):
        lv = tf.nn.weighted_cross_entropy_with_logits(labels=x, logits=y, pos_weight=self.pos_weight)
        return tf.reduce_mean(lv)

    def get_config(self):
        # include our own arg so it’s saved/loaded
        config = super().get_config()
        config.update({"pos_weight": self.pos_weight})
        return config
