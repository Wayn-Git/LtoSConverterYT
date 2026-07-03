import json
import time
from groq import Groq

client = Groq()

INPUT_FILE = "final_transcript.json"
OUTPUT_FILE = "candidate_clips.json"

MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """You are analyzing one chunk of a larger YouTube transcript.

Your goal is to identify ONLY the strongest moments that would become engaging
30–60 second short-form videos (YouTube Shorts, TikTok, Reels).

Each clip MUST be between 30 and 60 seconds long.

Do NOT return isolated moments lasting only a few seconds.

If you identify an interesting moment, expand the start and end timestamps to include the surrounding context so the clip is understandable on its own.

A viewer should be able to watch the clip without needing the rest of the video.

Rules:
- Return at most 2 clips per chunk.
- Only return a clip if it is genuinely interesting.
- Ignore filler, introductions, transitions, greetings, ads, and repetitive content.
- Prefer moments with:
  - surprising insights
  - strong opinions
  - practical advice
  - impressive demos
  - funny moments
  - emotional moments
  - memorable quotes
- Each clip should be between 30 and 60 seconds whenever possible.
- If no good clip exists, return an empty list.

Return ONLY valid JSON.

{
  "clips": [
    {
      "start": 123.4,
      "end": 156.8,
      "score": 9,
      "reason": "..."
    }
  ]

I SHOULDN'T BE SEEING THE DIFFERENCE BETWEEN START AND END TO BE BELOW 30 SECONDS STRICKLY QUALITY OVER QUANITTY
  
}"""


def build_user_content(chunk):
    transcript = "\n".join(
        f"[{s['start']:.2f}] {s['text']}"
        for s in chunk["segment"]   # <-- singular
    )

    return f"""
Previous Context:
{chunk["previous_context"]}

Current Transcript:
{transcript}

Next Context:
{chunk["next_context"]}
"""

def analyze_chunk(chunk):
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_content(chunk)}
            ],
            temperature=0.3,
            max_completion_tokens=300,
            response_format={"type": "json_object"},
        )

        response = completion.choices[0].message.content
        return json.loads(response).get("clips", [])

    except Exception as e:
        print(f"Error in chunk {chunk['chunk_id']}: {e}")
        return []


def main():
    with open(INPUT_FILE, "r") as f:
        chunks = json.load(f)

    all_clips = []

    for chunk in chunks:
        print(f"Analyzing chunk {chunk['chunk_id']}...")

        clips = analyze_chunk(chunk)

        for clip in clips:
            clip["chunk_id"] = chunk["chunk_id"]

        all_clips.extend(clips)

        time.sleep(1)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_clips, f, indent=2)

    print(f"Saved {len(all_clips)} clips to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()