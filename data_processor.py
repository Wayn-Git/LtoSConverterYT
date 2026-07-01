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

CHUNK_SIZE = 300

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


with open("final_transcript.json", "w") as f:
    json.dump(chunks, f, indent=2)

