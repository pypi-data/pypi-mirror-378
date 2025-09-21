import tensorflow as tf
from huggingface_hub import hf_hub_download

from monkeycall.custom_objects.spider_monkey_custom_objects import custom_objects

repo_id = "georgiosrizos/spider-monkey-detector-SEResNet"

# Download the exact model file
model_path = hf_hub_download(repo_id=repo_id, filename="spider-monkey-detector-SEResNet.keras")

# Load it
model = tf.keras.models.load_model(model_path, custom_objects=custom_objects, compile=False)

# Predict (example)
import numpy as np
dummy_input = np.random.rand(5, 300, 128).astype("float32")
probs = model.predict(dummy_input)        # or model(dummy_input, training=False)
print("Predicted probabilities:", type(probs))
