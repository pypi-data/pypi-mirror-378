import httpx, ollama
from .config import Config
from .tts import tts_glados
from .stt import transcribe_audio

_messages = [
    {"role": "system", "content": "You are GLaDOS from Portal 2: cold, sarcastic, clinical."}
]

class GladosChat:
    def __init__(self, enable_tts=True, enable_stt=False, model="llama2:7b"):
        self.cfg = Config(enable_tts, enable_stt, model)

    def ask(self, user_message: str, stream: bool = False):
        global _messages
        _messages.append({"role": "user", "content": user_message})
        for host in ["http://127.0.0.1:11434", "http://localhost:11434"]:
            try:
                client = ollama.Client(host=host)
                if stream:
                    def generator():
                        full_reply = ""
                        for chunk in client.chat(model=self.cfg.model, messages=_messages, stream=True):
                            if "message" in chunk and "content" in chunk["message"]:
                                piece = chunk["message"]["content"]
                                full_reply += piece
                                yield piece
                        _messages.append({"role": "assistant", "content": full_reply})
                    return generator()
                else:
                    result = client.chat(model=self.cfg.model, messages=_messages)
                    reply = result["message"]["content"]
                    _messages.append({"role": "assistant", "content": reply})
                    return reply
            except httpx.ConnectError:
                continue
        raise RuntimeError("Could not connect to Ollama.")

    def speak(self, text: str, output_path="response.wav"):
        if not self.cfg.enable_tts:
            return None
        return tts_glados(text, output_path)

    def transcribe(self, file_path: str) -> str:
        if not self.cfg.enable_stt:
            return None
        return transcribe_audio(file_path)
