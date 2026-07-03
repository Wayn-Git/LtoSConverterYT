import config
import json

"""
Data Format

[
  {
    "chunk_id": 1,
    "chunk_start": 0.0,
    "chunk_end": 295.0,
    "segments": [
      {
        "text": "I built this entire app with Claude",
        "start": 0.0,
        "end": 4.56,
        "duration": 4.56
      },
      {
        "text": "code. Now let's see if it's production ready.",
        "start": 4.56,
        "end": 9.24,
        "duration": 4.68
      }
    ]
  },
  ...
  ]

"""

with open("output/transcript.json", "r") as f:
    data = json.load(f)

CHUNK_SIZE = 120

chunks = []

current_chunk = {
    "chunk_id": 1,
    "chunk_start": 0.0,
    "chunk_end": CHUNK_SIZE,   
    "segment": []
}



for segment in data:
    while segment['start'] >= current_chunk['chunk_end']:
        chunks.append(current_chunk)
        
        current_chunk = {
            "chunk_id": current_chunk['chunk_id'] + 1,
            "chunk_start": current_chunk['chunk_end'],
            "chunk_end" : current_chunk['chunk_end'] + CHUNK_SIZE,
            "segment":[]
        }

    current_chunk["segment"].append(segment)


# appending the last segment
if current_chunk["segment"]:
    chunks.append(current_chunk)


# --- NEW: just add a bit of neighboring text to each chunk ---
BUFFER_WORDS = 40

def edge_text(segments, n, from_end=True):
    words = " ".join(s['text'] for s in segments).split()
    return " ".join(words[-n:] if from_end else words[:n])

for i, chunk in enumerate(chunks):
    chunk["previous_context"] = edge_text(chunks[i-1]["segment"], BUFFER_WORDS, from_end=True) if i > 0 else ""
    chunk["next_context"] = edge_text(chunks[i+1]["segment"], BUFFER_WORDS, from_end=False) if i < len(chunks)-1 else ""

with open("final_transcript.json", "w") as f:
    json.dump(chunks, f, indent=2)
