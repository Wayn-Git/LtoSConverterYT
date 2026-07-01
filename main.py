from stages.stage1_transcribe import TranscribeVId


tv = TranscribeVId("https://www.youtube.com/watch?v=gyGPcGOKlGI")
tv.transcribe()
tv.save_transcript_json()