# glados_chat_lib/cli.py
import argparse
import sys
import json
import os
import uuid
import tempfile
from pathlib import Path
from colorama import Fore, Style, init

from .audio import list_devices, play_audio
from .chat import GladosChat
from .stt import transcribe_audio  # Whisper backend

import sounddevice as sd
import soundfile as sf
import numpy as np
import webrtcvad
import collections

init(autoreset=True)

_CONFIG_PATH = Path.home() / ".glados-cli.json"
_selected_device = None


def _load_saved_config():
    global _selected_device
    try:
        if _CONFIG_PATH.exists():
            data = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
            dev = data.get("audio_device_index", None)
            if isinstance(dev, int):
                _selected_device = dev
    except Exception:
        _selected_device = None


def _save_selected_device(index: int):
    try:
        _CONFIG_PATH.write_text(json.dumps({"audio_device_index": index}), encoding="utf-8")
    except Exception as e:
        print(Fore.RED + f"Warning: couldn't save config: {e}")


_load_saved_config()


def cmd_audiosource():
    devices = list_devices(include_inputs=False, include_outputs=True)
    if not devices:
        print(Fore.RED + "No audio output devices found.")
        return

    print(Fore.CYAN + "Available audio output devices:")
    for i, d in enumerate(devices):
        print(Fore.YELLOW + f"[{i}] {d['name']} (sd-index {d['index']})")

    try:
        choice = int(input(Fore.CYAN + "Select device number: "))
        if 0 <= choice < len(devices):
            global _selected_device
            _selected_device = devices[choice]["index"]
            _save_selected_device(_selected_device)
            print(Fore.GREEN + f"✅ Selected device: {devices[choice]['name']} (sd-index {_selected_device})")
        else:
            print(Fore.RED + "Invalid choice.")
    except ValueError:
        print(Fore.RED + "Invalid input.")


def _speak_chunk(chat, text, device_index):
    try:
        tmp_wav = os.path.join(tempfile.gettempdir(), f"glados_{uuid.uuid4().hex}.wav")
        wav = chat.speak(text, output_path=tmp_wav)
        if wav:
            play_audio(wav, device_index, block=True)
            os.remove(wav)
    except Exception as e:
        print(Fore.RED + f"[TTS Error] {e}")


def _vad_record(samplerate=16000, frame_duration=30):
    """Wait for speech, then record until silence, return filename."""
    vad = webrtcvad.Vad(2)  # 0=aggressive, 3=very aggressive
    frame_size = int(samplerate * frame_duration / 1000)
    ring_buffer = collections.deque(maxlen=10)
    triggered = False
    voiced_frames = []

    print(Fore.CYAN + "🎙️ Waiting for you to speak...")

    with sd.InputStream(samplerate=samplerate, channels=1, dtype="int16") as stream:
        while True:
            frame, _ = stream.read(frame_size)
            is_speech = vad.is_speech(frame.tobytes(), samplerate)

            if not triggered:
                ring_buffer.append((frame.copy(), is_speech))
                if sum(f[1] for f in ring_buffer) > 0.9 * ring_buffer.maxlen:
                    triggered = True
                    print(Fore.CYAN + "🎤 Listening...")
                    voiced_frames.extend(f[0] for f in ring_buffer)
                    ring_buffer.clear()
            else:
                voiced_frames.append(frame.copy())
                ring_buffer.append((frame.copy(), is_speech))
                if sum(f[1] for f in ring_buffer) < 0.1 * ring_buffer.maxlen:
                    print(Fore.CYAN + "✅ Done speaking.")
                    break

    audio = np.concatenate(voiced_frames, axis=0)
    filename = os.path.join(tempfile.gettempdir(), f"glados_input_{uuid.uuid4().hex}.wav")
    sf.write(filename, audio, samplerate)
    return filename


def cmd_start(args):
    global _selected_device
    if args.audiosource is not None:
        _selected_device = args.audiosource
        print(Fore.GREEN + f"Using provided audio device index: {_selected_device}")
    elif _selected_device is not None:
        print(Fore.GREEN + f"Using saved audio device index: {_selected_device}")
    else:
        print(Fore.YELLOW + "No audio device chosen — using system default output.")

    chat = GladosChat(enable_tts=args.tts, enable_stt=args.stt)

    print(Fore.MAGENTA + Style.BRIGHT + "=== GLaDOS Chat ===")
    if args.stt:
        print(Fore.CYAN + "Speak when ready. Ctrl+C to quit.\n")
    else:
        print(Fore.CYAN + "Type 'exit' to quit.\n")

    while True:
        try:
            if args.stt:
                audio_file = _vad_record()
                user_input = transcribe_audio(audio_file).strip()
                if not user_input:
                    continue
                print(Fore.YELLOW + f"You (spoken): {user_input}")
            else:
                user_input = input(Fore.YELLOW + "You: " + Style.RESET_ALL).strip()
                if not user_input:
                    continue
                if user_input.lower() in {"exit", "quit"}:
                    print(Fore.RED + "👋 Exiting GLaDOS CLI.")
                    break

            if args.stream:
                print(Fore.GREEN + "GLaDOS: " + Style.RESET_ALL, end="", flush=True)
                reply, buffer = "", ""
                for piece in chat.ask(user_input, stream=True):
                    reply += piece
                    buffer += piece
                    if any(buffer.endswith(p) for p in [".", "!", "?", "\n"]):
                        chunk = buffer.strip()
                        buffer = ""
                        sys.stdout.write(Fore.GREEN + chunk + " " + Style.RESET_ALL)
                        sys.stdout.flush()
                        if args.tts and chunk:
                            _speak_chunk(chat, chunk, _selected_device)
                if buffer.strip():
                    chunk = buffer.strip()
                    sys.stdout.write(Fore.GREEN + chunk + " " + Style.RESET_ALL)
                    sys.stdout.flush()
                    if args.tts:
                        _speak_chunk(chat, chunk, _selected_device)
                print()
            else:
                reply = chat.ask(user_input)
                print(Fore.GREEN + f"GLaDOS: {reply}" + Style.RESET_ALL)
                if args.tts and reply.strip():
                    _speak_chunk(chat, reply.strip(), _selected_device)
        except KeyboardInterrupt:
            print(Fore.RED + "\n👋 Exiting GLaDOS CLI.")
            break


def main():
    parser = argparse.ArgumentParser(prog="glados-cli", description="Talk with GLaDOS through your terminal.")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("audiosource", help="List and select audio output devices (persisted).")

    sp_start = subparsers.add_parser("start", help="Start chatting with GLaDOS.")
    sp_start.add_argument("--tts", action="store_true", help="Enable TTS output.")
    sp_start.add_argument("--stt", action="store_true", help="Enable STT input (speak instead of type).")
    sp_start.add_argument("--audiosource", type=int, help="Set audio device index for this session.")
    sp_start.add_argument("--stream", action="store_true", help="Stream replies sentence-by-sentence.")

    args = parser.parse_args()
    if args.command == "audiosource":
        cmd_audiosource()
    elif args.command == "start":
        cmd_start(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
