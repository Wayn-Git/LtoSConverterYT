# Storing the data part

```
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
  {
    "chunk_id": 2,
    "chunk_start": 275.0,
    "chunk_end": 570.0,
    "segments": [
      ...
    ]
  }
]

```

--- 

# Analysis Part

## Two-pass system

### Pass 1: Process chunks independently and collect candidate highlights.

Video

 ↓

Chunk 1 → 3 candidate clips
Chunk 2 → 2 candidate clips
Chunk 3 → 4 candidate clips
...

Now you might have 30 candidate clips.

### Pass 2: Give those 30 candidates to another LLM call.

Ask it to:

- merge overlapping clips,
- remove duplicates,
- rank them,
- return the best 5.

Now the model has a global view, but it's looking at only 30 objects instead of a huge transcript.