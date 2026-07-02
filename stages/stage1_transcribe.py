# Youtube Related Libraries

from youtube_transcript_api import YouTubeTranscriptApi
from pytubefix import YouTube

#System realted lirbaries

import sys
import json
from pathlib import Path

import re

sys.path.append(str(Path(__file__).resolve().parent.parent))

import config

# youtube url = https://www.youtube.com/watch?v=gyGPcGOKlGI

class TranscribeVId:
    def __init__(self, video_link: str):
        self.video_link = video_link
        # self.video_transcript = "" I don't know why I have this line but I had a good implimenteation with this
        self.ytt_api = YouTubeTranscriptApi()

    
    def _extract_video_code(self) -> str:
        self.url_split = self.video_link.split("=")
        self.video_code = self.url_split[1]
        return self.video_code
    
    def _video_title(self) -> str:
        # Where did I get this block of code from ?
        #This https://www.reddit.com/r/learnpython/comments/p0kap1/how_can_i_get_the_name_of_a_youtube_video_if_i/
        url = "=".join(self.url_split)

        print(f"URL: {repr(url)}")

        yt = YouTube(url)
        title = yt.title

        # getting rid of shitty stuff in the title (copy pasted from somewhere)
        title = re.sub(r'[\\/*?:"<>|]', "", title)

        title = title.replace(" ", "_") # to access better maybe better to replace with transcript1, transcript2 and shi 

        return title

    def transcribe(self) -> list:
        fetched_transcript = self.ytt_api.fetch(self._extract_video_code())
        raw_transcript = fetched_transcript.to_raw_data()
        return raw_transcript
    
    def save_transcript_json(self) -> Path:
        
        output = Path(config.OUTPUT_FOLDER) / f"{self._video_title()}.json"
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output, 'w') as f:
            json.dump(self.transcribe(), f, indent=2)
        return output
        