import sounddevice as sd
import soundfile as sf
import pyttsx3
import numpy as np
import keyboard
from resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path
from scipy.io.wavfile import write as write_wav

# Text-to-speech setup
engine = pyttsx3.init()
engine.setProperty("rate", 150)

# Voice verification setup
encoder = VoiceEncoder()
samplerate = 16000
verify_duration = 3  # seconds
chat_duration = 5    # seconds

def record_audio(duration=5, samplerate=16000):
    print(f"🎙️ Recording for {duration} seconds...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    print("✅ Done recording.")
    return np.squeeze(audio)

def save_wav(filename, audio, samplerate=16000):
    sf.write(filename, audio, samplerate)

def get_embedding(filename):
    wav = preprocess_wav(Path(filename))
    return encoder.embed_utterance(wav) 

def verify_driver():
    print("🔐 Voice Verification")
    print("🎙️ Press SPACE to record your reference voice...")
    keyboard.wait("space")
    ref_audio = record_audio(verify_duration, samplerate)
    save_wav("ref.wav", ref_audio)

    print("🎙️ Press SPACE again to verify your voice...")
    keyboard.wait("space")
    test_audio = record_audio(verify_duration, samplerate)
    save_wav("test.wav", test_audio)

    ref_embed = get_embedding("ref.wav")
    test_embed = get_embedding("test.wav")

    similarity = np.dot(ref_embed, test_embed) / (
        np.linalg.norm(ref_embed) * np.linalg.norm(test_embed)
    )
    print(f"🔍 Similarity Score: {similarity:.3f}")

    if similarity > 0.70:
        print("✅ Voice Verified. Welcome, driver!")
        engine.say("Welcome, driver!")
        engine.runAndWait()
        return True
    else:
        print("❌ Voice Not Recognized")
        engine.say("Access denied. Voice not recognized.")
        engine.runAndWait()
        return False


# === MAIN LOGIC ===
if __name__ == "__main__":
    if verify_driver():
        print("🟢 Assistant activated. Press SPACE to speak. Press ESC to exit.")
