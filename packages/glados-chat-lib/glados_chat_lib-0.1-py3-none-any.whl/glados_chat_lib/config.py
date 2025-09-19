class Config:
    def __init__(self, enable_tts=True, enable_stt=False, model="llama2:7b"):
        self.enable_tts = enable_tts
        self.enable_stt = enable_stt
        self.model = model
