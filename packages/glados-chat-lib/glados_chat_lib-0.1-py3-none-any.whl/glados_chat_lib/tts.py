import os, re, numpy as np, soundfile as sf
from huggingface_hub import hf_hub_download
from piper.voice import PiperVoice

MODEL_REPO = "csukuangfj/vits-piper-en_US-glados-high"
MODEL_DIR = "./glados_tts"
ONNX_FILENAME = "en_US-glados-high.onnx"
CONFIG_FILENAME = "en_US-glados-high.onnx.json"

MODEL_PATH = os.path.join(MODEL_DIR, ONNX_FILENAME)
CONFIG_PATH = os.path.join(MODEL_DIR, CONFIG_FILENAME)

# Ensure model + config exist
if not os.path.exists(MODEL_PATH) or not os.path.exists(CONFIG_PATH):
    os.makedirs(MODEL_DIR, exist_ok=True)
    print(f"⬇️ Downloading GLaDOS voice model from {MODEL_REPO} ...")
    hf_hub_download(MODEL_REPO, ONNX_FILENAME, local_dir=MODEL_DIR)
    hf_hub_download(MODEL_REPO, CONFIG_FILENAME, local_dir=MODEL_DIR)

_voice = None

def get_voice():
    global _voice
    if _voice is None:
        _voice = PiperVoice.load(MODEL_PATH, config_path=CONFIG_PATH)
    return _voice


def clean_text(text: str) -> str:
    text = re.sub(r"\*.*?\*", "", text)  # remove *markers*
    text = re.sub(r"[^a-zA-Z0-9\s.,!?'\-]", "", text)  # keep safe chars
    return re.sub(r"\s+", " ", text).strip()


def tts_glados(text: str, output_path: str = None, verbose: bool = False):
    voice = get_voice()

    text = clean_text(text)
    if not text:
        return None

    if verbose:
        print(f"[TTS] Synthesizing: {text}")

    audio_chunks = []
    for chunk in voice.synthesize(text):
        audio_chunks.append(chunk.audio_float_array.astype(np.float32))

    if not audio_chunks:
        raise RuntimeError("No audio produced.")

    audio = np.concatenate(audio_chunks).astype(np.float32)
    if audio.ndim > 1:
        audio = audio[:, 0]

    if output_path is None:
        import tempfile, uuid, os
        output_path = os.path.join(tempfile.gettempdir(), f"glados_{uuid.uuid4().hex}.wav")

    sf.write(output_path, audio, voice.config.sample_rate)
    return output_path
