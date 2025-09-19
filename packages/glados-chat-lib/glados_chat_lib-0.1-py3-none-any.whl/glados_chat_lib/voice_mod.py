import numpy as np, soundfile as sf

def change_speed(data: np.ndarray, speed: float) -> np.ndarray:
    if speed <= 0:
        raise ValueError("Speed must be positive")
    orig_indices = np.arange(len(data))
    new_length = int(len(data) / speed)
    new_indices = np.linspace(0, len(data) - 1, new_length)
    return np.interp(new_indices, orig_indices, data).astype(data.dtype)

def modify_file(input_path: str, output_path: str, speed: float = 1.0):
    data, sr = sf.read(input_path, dtype="float32")
    if data.ndim > 1:
        data = data.mean(axis=1)
    modified = change_speed(data, speed)
    sf.write(output_path, modified, sr)
    return output_path
