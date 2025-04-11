import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import time
import pvporcupine
import pyaudio
import struct
import wave
import pvcobra
from openai import OpenAI
from resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path
import numpy as np
import sounddevice as sd
import soundfile as sf
import keyboard

# Global encoder and embedding
encoder = VoiceEncoder()
reference_embedding = None

def record_reference_voiceprint():
    global reference_embedding
    duration = 5  # ⏱️ Change recording time to 5 seconds
    samplerate = 16000

    print("🎤 Recording reference voice for 5 seconds...")
    my_recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()

    sf.write("ref_voice.wav", my_recording, samplerate)
    wav = preprocess_wav(Path("ref_voice.wav"))
    reference_embedding = encoder.embed_utterance(wav)
    print("✅ Voiceprint saved.")

class VoiceAssistantApp:
    def __init__(self, master):
        self.master = master
        self.master.title("HeyGrab")
        self.master.geometry("500x500")
        self.master.configure(bg="#2c3e50")
        
        self.access_key = "y5PyL9njmEig0sDZHR/27jaX2Cu3oT5ufGLlevkqd4u+pRRSRA6xxw=="
        self.keyword_path = "hey_grab_ppn.ppn"
        self.filename = "porcupine_testing.wav"
        self.client = OpenAI(api_key="your_openai_api_key")
        
        self.create_widgets()

        self.is_listening = False
        self.is_recording = False

    def create_widgets(self):
        self.toggle_button = tk.Button(self.master, text="Start Listening", command=self.toggle_listening, bg="#1ebd60", fg="white", width=20)
        self.toggle_button.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.register_button = tk.Button(self.master, text="Register My Voice", command=record_reference_voiceprint, bg="#1ebd60", fg="white", width=20)
        self.register_button.grid(row=1, column=0, columnspan=2, pady=10)

        self.status_label = tk.Label(self.master, text="Status: Idle", fg="black", bg="#e9f8ef", font=("Arial", 14))
        self.status_label.grid(row=2, column=0, columnspan=2, pady=10)

        self.transcription_area = scrolledtext.ScrolledText(self.master, width=50, height=10, wrap=tk.WORD, font=("Arial", 12))
        self.transcription_area.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.log_console = scrolledtext.ScrolledText(self.master, width=50, height=6, wrap=tk.WORD, font=("Arial", 10))
        self.log_console.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.microphone_icon = tk.Label(self.master, text="🔴", font=("Arial", 24), fg="gray", bg="#e9f8ef")
        self.microphone_icon.grid(row=5, column=0, columnspan=2, pady=10)

    def update_status(self, status, color="white"):
        self.status_label.config(text=f"Status: {status}", fg=color)
        self.master.update()

    def update_log(self, message):
        self.log_console.insert(tk.END, f"{message}\n")
        self.log_console.yview(tk.END)
        self.master.update()

    def update_microphone_icon(self, listening):
        self.microphone_icon.config(fg="green" if listening else "gray")
        self.master.update()

    def transcribe(self):
        self.update_log("Transcribing audio...")
        transcript = self.client.audio.translations.create(
            model="whisper-1",
            file=open(self.filename, "rb"),
            prompt="Transcribe without translation."
        )
        self.transcription_area.insert(tk.END, f"{transcript.text}\n")
        self.transcription_area.yview(tk.END)

    def start_listening(self):
        global reference_embedding

        if reference_embedding is None:
            messagebox.showwarning("No Voice Registered", "Please register your voice first.")
            self.update_log("⚠️ Attempted to listen without registering voice.")
            return

        if self.is_listening:
            self.update_log("Already listening...")
            return

        self.update_status("Listening for 'Hey Grab'...", "black")
        self.update_microphone_icon(True)
        self.is_listening = True

        def listen():
            cobra = pvcobra.create(access_key=self.access_key)
            porcupine = pvporcupine.create(access_key=self.access_key, keyword_paths=[self.keyword_path])
            pa = pyaudio.PyAudio()
            audio_stream = pa.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=porcupine.frame_length)

            rate = porcupine.sample_rate
            frames = []
            result = -1
            count = 30
            try:
                while self.is_listening:
                    pcm_b = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
                    pcm = struct.unpack_from("h" * porcupine.frame_length, pcm_b)

                    if result < 0:
                        result = porcupine.process(pcm)

                    if result >= 0:
                        self.update_log("Heard 'Hey Grab', recording voice...")
                        sample_filename = "test_voice.wav"
                        with wave.open(sample_filename, 'wb') as wf:
                            wf.setnchannels(1)
                            wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
                            wf.setframerate(rate)
                            wf.writeframes(pcm_b)

                        test_wav = preprocess_wav(Path(sample_filename))
                        test_embedding = encoder.embed_utterance(test_wav)

                        similarity = np.dot(reference_embedding, test_embedding) / (
                            np.linalg.norm(reference_embedding) * np.linalg.norm(test_embedding)
                        )

                        if similarity > 0.70:
                            self.update_log("✅ Voice verified! Recording continues...")
                        else:
                            self.update_log("❌ Unauthorized voice. Ignoring trigger.")
                            self.update_status("Unauthorized", "red")
                            break

                        self.update_status("Recording...", "black")
                        self.is_recording = True
                        frames.append(pcm_b)

                        voice_probability = cobra.process(pcm)
                        if voice_probability < 0.3:
                            count -= 1
                            if count <= 0:
                                with wave.open(self.filename, 'wb') as wf:
                                    wf.setnchannels(1)
                                    wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
                                    wf.setframerate(rate)
                                    wf.writeframes(b''.join(frames))
                                self.update_log(f"Saved to {self.filename}")
                                self.transcribe()
                                break
                        else:
                            count = 30
            except Exception as e:
                self.update_log(f"Error while recording: {e}")
                self.stop_listening()

        threading.Thread(target=listen, daemon=True).start()

    def stop_listening(self):
        if not self.is_listening:
            self.update_log("Not currently listening...")
            return
        self.update_status("Stopped.", "black")
        self.update_microphone_icon(False)
        self.is_listening = False
        self.is_recording = False
        self.update_log("Listening stopped.")

    def toggle_listening(self):
        if self.is_listening:
            self.stop_listening()
            self.toggle_button.config(text="Start Listening")
        else:
            self.start_listening()
            self.toggle_button.config(text="Stop Listening")

def run():
    root = tk.Tk()
    app = VoiceAssistantApp(root)
    root.config(bg="#e9f8ef")
    root.mainloop()

if __name__ == "__main__":
    run()
