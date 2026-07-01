from youtube_transcript_api import YouTubeTranscriptApi
import json
from pprint import pprint

ytt_api = YouTubeTranscriptApi()
vid_transcript = ytt_api.fetch("x1SkQpKd8a8")

fetch_transcript = vid_transcript.to_raw_data()

with open ("output/transcript.json", "w") as r: 
    json.dump(fetch_transcript, r, indent=2)


