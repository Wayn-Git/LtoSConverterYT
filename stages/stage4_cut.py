import json
import os
from pytubefix import YouTube
from moviepy import VideoFileClip
from moviepy.video.fx import Crop

def download_video(url, output_path="output/source_video.mp4"):
    if not os.path.exists(output_path):
        print(f"Downloading video from {url}...")
        yt = YouTube(url)
        # Get highest resolution progressive video
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if not stream:
            stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        stream.download(output_path=os.path.dirname(output_path), filename=os.path.basename(output_path))
        print("Download complete.")
    else:
        print("Video already downloaded.")
    return output_path

def cut_and_crop(video_path, clips_data, output_dir="output/clips"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Get dimensions once
    with VideoFileClip(video_path) as video:
        w, h = video.size
        
    target_ratio = 9 / 16
    if w / h > target_ratio:
        # Video is wider than 9:16, crop width
        new_w = int(h * target_ratio)
        x_center = w / 2
        y_center = h / 2
        x1 = x_center - new_w / 2
        x2 = x_center + new_w / 2
        y1 = 0
        y2 = h
    else:
        # Video is taller, crop height
        new_h = int(w / target_ratio)
        x_center = w / 2
        y_center = h / 2
        x1 = 0
        x2 = w
        y1 = y_center - new_h / 2
        y2 = y_center + new_h / 2

    for i, clip_info in enumerate(clips_data):
        start = clip_info.get("start")
        end = clip_info.get("end")
        if start is None or end is None:
            continue
            
        print(f"Processing clip {i+1} (from {start}s to {end}s)")
        
        # Open video fresh for each clip to avoid reader process issues
        with VideoFileClip(video_path) as video:
            # Cut the clip
            subclip = video.subclipped(start, end)
            
            # Crop to 9:16
            cropped_clip = subclip.with_effects([Crop(x1=int(x1), y1=int(y1), x2=int(x2), y2=int(y2))])
            
            # Write to file
            out_filename = os.path.join(output_dir, f"clip_{i+1}_score_{clip_info.get('score', 'NA')}.mp4")
            cropped_clip.write_videofile(out_filename, codec="libx264", audio_codec="aac")
            
            # No need to explicitly close here if using context manager, but we do it anyway for the subclips
            cropped_clip.close()
            subclip.close()

    print("All clips processed.")

def main():
    try:
        with open("candidate_clips.json", "r") as f:
            clips_data = json.load(f)
    except FileNotFoundError:
        print("candidate_clips.json not found. Please run earlier stages first.")
        return
        
    url = "https://www.youtube.com/watch?v=gyGPcGOKlGI" # Default URL
    print(f"Using default video URL: {url}")
    
    video_path = download_video(url)
    cut_and_crop(video_path, clips_data)

if __name__ == "__main__":
    main()
