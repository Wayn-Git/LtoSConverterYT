# stage2_analyze.py
# LLM moment detection (Groq)

from groq import Groq

client = Groq()
completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
      {
        "role": "system",
        "content": """
You are analyzing one chunk of a larger transcript.

The timestamps are absolute timestamps from the original video.

Identify all complete, high-quality clips that begin and end within this chunk.

Do not invent timestamps.

"""
      },
      {
        "role": "user",
        "content": ""
      }
    ],
    temperature=1,
    max_completion_tokens=1024,
    top_p=1,
    stream=True,
    stop=None
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
