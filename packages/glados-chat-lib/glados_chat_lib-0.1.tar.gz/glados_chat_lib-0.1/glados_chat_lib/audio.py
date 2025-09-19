import sounddevice as sd
import soundfile as sf
import numpy as np


def list_devices(include_inputs=True, include_outputs=True):
    """Return available audio devices as a list of dicts."""
    devices = []
    print("\n=== Available Audio Devices ===")
    for idx, d in enumerate(sd.query_devices()):
        if include_outputs and d["max_output_channels"] > 0:
            devices.append({"name": f"[OUT] {d['name']}", "index": idx, "type": "output"})
            print(f"{idx}: [OUT] {d['name']}")
        if include_inputs and d["max_input_channels"] > 0:
            devices.append({"name": f"[IN] {d['name']}", "index": idx, "type": "input"})
            print(f"{idx}: [IN] {d['name']}")
    print("===============================\n")
    return devices


def play_audio(file_path, device_index=None, block=True):
    try:
        data, sr = sf.read(file_path, dtype="float32")

        if device_index is None:
            device_index = sd.default.device[1]

        info = sd.query_devices(device_index, "output")
        max_ch = info["max_output_channels"]

        if data.ndim > 1 and max_ch < data.shape[1]:
            data = data.mean(axis=1)

        sd.play(data, samplerate=sr, device=device_index)
        if block:
            sd.wait()
    except Exception as e:
        print(f"[AudioManager] Could not play {file_path}: {e}")
