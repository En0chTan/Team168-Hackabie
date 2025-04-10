from openai import OpenAI
client = OpenAI(api_key="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")
transcript = client.audio.translations.create(
    model="whisper-1",
    file=open("porcupine_testing.wav", "rb")
)
print(transcript)