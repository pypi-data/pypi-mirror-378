# Monkey Call Detector

Detect spider monkey whinny calls (and howler monkey calls) in audio recordings using pre-trained TensorFlow models.

This package downloads a model from [🤗 Hugging Face](https://huggingface.co/georgiosrizos/spider-monkey-dummy-detector)
and provides simple functions for ecologists and data scientists to run inference on short clips or entire recordings.

---

## Installation

This has been tested with a fresh python 3.13 installation.

(Optional) Make a virtual environment (python -m venv /path/to/new/virtual/environment)

```bash
pip3 install monkeycall  # This will also install requirements.
```

## Usage examples

You can now detect monkey calls. To detect spider monkeys try the following:


```bash
from monkeycall.spider_monkey import load_model, predict_recording

recording_path = "/path/to/sample.WAV"

repo_id = "georgiosrizos/spider-monkey-detector-SEResNet"

print("Reading pre-trained model.")
model = load_model(architecture=repo_id)

print("Reading long recording:", recording_path)
output_df = predict_recording(audio_path=recording_path,
                              model=model,
                              hop_size=1)

print("The recording has been clipped in 3 sec window clips. The whinny detection probabilities are:", output_df)

# You can save the pandas DataFrame to review later.
# output_df.to_csv("predictions.csv", index=False)
```

Or if you already have a 3 sec clip:


```bash
from monkeycall.spider_monkey import load_model, predict_3_sec_clip

recording_path = "/path/to/3sec.WAV"

repo_id = "georgiosrizos/spider-monkey-detector-SEResNet"

print("Reading pre-trained model.")
model = load_model(architecture=repo_id)

print("Reading clip:", negative)
output = predict_3_sec_clip(audio_path=recording_path,
                            model=model)

print("The probability this sample contains a whinny is:", output)
```