from faster_whisper import WhisperModel

_model = None

def load_model(model_size="base", device="cpu"):
    global _model
    if _model is None:
        _model = WhisperModel(model_size, device=device)
    return _model

def transcribe_audio(file_path: str, model_size="base", device="cpu") -> str:
    model = load_model(model_size=model_size, device=device)
    segments, _ = model.transcribe(file_path)
    return " ".join(seg.text for seg in segments)
