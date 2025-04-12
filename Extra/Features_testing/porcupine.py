import pvporcupine
import pyaudio
import struct
import os
import wave
import pvcobra
import time
from openai import OpenAI
from deepgram import Deepgram
import asyncio
from dotenv import dotenv_values

def main():
    config = dotenv_values(".env")
    access_key = config["PICO-API"]  # From Picovoice Console
    keyword_path = "hey_grab_ppn.ppn"
    filename = "audio/porcupine.wav"
    
    # Set your API key here
    DEEPGRAM_API_KEY = OpenAI(api_key=config["OPEN-API"])

    # Async function to handle transcription
    async def transcribe():
        dg_client = Deepgram(DEEPGRAM_API_KEY)

        with open(filename, "rb") as audio:
            source = {
                "buffer": audio,
                "mimetype": "audio/wav"
            }

            response = await dg_client.transcription.prerecorded(
                source,
                {"punctuate": True, "language": "en"}
            )

            print(response["results"]["channels"][0]["alternatives"][0]["transcript"])


    cobra = pvcobra.create(access_key=access_key)
    porcupine = pvporcupine.create(
        access_key=access_key,
        keyword_paths=[keyword_path]
    )

    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate, #16k 
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length #512
    )

    print("Listening for 'Hey Grab'...")
    rate = porcupine.sample_rate
    chunk = porcupine.frame_length
    record = False #As a trigger to start recording
    frames = [] #To put chunks of audio
    count = 30
    result = -1
    try:
        while True:
            pcm_b = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm_b)
            if result < 0:
                result = porcupine.process(pcm)
            if result >= 0:
                record = True  #Start recording
                # You can now trigger your recording logic here
                if record:
                    voice_probability = cobra.process(pcm)
                    if voice_probability < 0.3:
                        count -= 1
                        if count <= 0:
                            audio_stream.stop_stream()
                            audio_stream.close()
                            pa.terminate()
                            porcupine.delete()
                            wf = wave.open(filename, 'wb')
                            wf.setnchannels(1)
                            wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
                            wf.setframerate(rate)
                            wf.writeframes(b''.join(frames))
                            wf.close()
                            print(f"Saved to {filename}")
                            asyncio.run(transcribe())
                    else:
                        count = 30
                    frames.append(pcm_b)

    except KeyboardInterrupt:
        print("Stopping...")

    finally:
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        porcupine.delete()
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        print(f"Saved to {filename}")

if __name__ == "__main__":
    main()