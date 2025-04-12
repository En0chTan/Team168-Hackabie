import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import time
import pvporcupine
import pyaudio
import struct
import wave
import pvcobra
import numpy as np
import torch
import torchaudio
import os
from openai import OpenAI
from speechbrain.pretrained import SpeakerRecognition


class VoiceAssistantApp:
    def __init__(self, master):
        self.master = master
        self.master.title("HeyGrab")
        self.master.geometry("500x550")
        self.master.configure(bg="#2c3e50")

        self.access_key = "y5PyL9njmEig0sDZHR/27jaX2Cu3oT5ufGLlevkqd4u+pRRSRA6xxw=="
        self.keyword_path = "hey_grab_ppn.ppn"
        self.filename = "recorded_voice.wav"
        self.client = OpenAI(api_key="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")

        # Voice Verification Init
        self.verification_done = False
        self.verification_threshold = 0.8
        self.verifier = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/speaker")
        self.enrolled_embedding = None

        # Load enrolled voice if exists
        if os.path.exists("test_voice.npy"):
            self.enrolled_embedding = torch.tensor(np.load("test_voice.npy"))

        self.create_widgets()
        self.is_listening = False

    def create_widgets(self):
        self.toggle_button = tk.Button(self.master, text="Start Listening", command=self.toggle_listening, bg="#1ebd60", fg="white", width=20)
        self.toggle_button.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.register_button = tk.Button(self.master, text="Register Voice", command=self.register_voice, bg="#1ebd60", fg="white", width=20)
        self.register_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

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

    def record_audio(self, output_filename, duration=4):
        self.update_log("Recording voice sample...")
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
        frames = []

        for _ in range(int(16000 / 1024 * duration)):
            data = stream.read(1024)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(output_filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))
        wf.close()

    def register_voice(self):
        self.update_status("Recording your voice...", "black")
        self.record_audio("test_sample.wav", duration=4)
        self.update_log("Generating voiceprint...")

        signal, _ = torchaudio.load("test_sample.wav")
        embedding = self.verifier.encode_batch(signal).squeeze().detach().cpu().numpy()
        np.save("test_voice.npy", embedding)
        self.enrolled_embedding = torch.tensor(embedding)
        self.verification_done = False  # Require re-verification on next wakeword
        self.update_log("✅ Voice registered successfully!")

    def transcribe(self):
        self.update_log("Transcribing audio...")
        try:
            transcript = self.client.audio.translations.create(
                model="whisper-1",
                file=open(self.filename, "rb"),
                prompt="Transcribe clearly spoken English commands."
            )
            self.transcription_area.insert(tk.END, f"{transcript.text}\n")
            self.transcription_area.yview(tk.END)
        except Exception as e:
            self.update_log(f"Transcription error: {e}")

    def verify_user_voice(self, audio_path):
        self.update_log("Verifying user voice...")
        try:
            test_embedding = self.verifier.encode_batch(torch.tensor(torchaudio.load(audio_path)[0]).unsqueeze(0))[0]
            similarity = torch.nn.functional.cosine_similarity(test_embedding, self.enrolled_embedding, dim=0).item()
            self.update_log(f"Voice similarity: {similarity:.2f}")
            return similarity > self.verification_threshold
        except Exception as e:
            self.update_log(f"Verification failed: {e}")
            return False

    def start_listening(self):
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
            stream = pa.open(
                rate=porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=porcupine.frame_length
            )

            frames = []
            count = 30
            result = -1

            try:
                while self.is_listening:
                    pcm_b = stream.read(porcupine.frame_length, exception_on_overflow=False)
                    pcm = struct.unpack_from("h" * porcupine.frame_length, pcm_b)
                    if result < 0:
                        result = porcupine.process(pcm)
                    if result >= 0:
                        self.update_log("Detected 'Hey Grab' wake word!")
                        self.update_status("Recording...", "black")
                        frames = [pcm_b]
                        while True:
                            pcm_b = stream.read(porcupine.frame_length, exception_on_overflow=False)
                            frames.append(pcm_b)
                            voice_prob = cobra.process(struct.unpack_from("h" * porcupine.frame_length, pcm_b))
                            count = count - 1 if voice_prob < 0.3 else 30
                            if count <= 0:
                                wf = wave.open(self.filename, 'wb')
                                wf.setnchannels(1)
                                wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
                                wf.setframerate(porcupine.sample_rate)
                                wf.writeframes(b''.join(frames))
                                wf.close()

                                if self.enrolled_embedding is None:
                                    self.update_log("⚠️ Voice not registered. Please register your voice first.")
                                    break

                                if not self.verification_done:
                                    if self.verify_user_voice(self.filename):
                                        self.update_log("✅ Verified registered user.")
                                        self.verification_done = True
                                    else:
                                        self.update_log("❌ Voice not recognized.")
                                        break

                                self.transcribe()
                                break
            except Exception as e:
                self.update_log(f"Error in listening: {e}")
            finally:
                stream.stop_stream()
                stream.close()
                pa.terminate()

        threading.Thread(target=listen, daemon=True).start()

    def stop_listening(self):
        self.update_status("Stopped", "black")
        self.update_microphone_icon(False)
        self.is_listening = False
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
