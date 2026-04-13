"""
Stage 1 — Video Download + Transcription
-----------------------------------------
Downloads a YouTube video via yt-dlp and transcribes it locally
using faster-whisper with word-level timestamps.

Output:
  <output_dir>/
    video.mp4          — downloaded video (used by later stages)
    transcript.json    — structured transcript with word-level timestamps
    transcript.txt     — plain text transcript (fed to LLM in Stage 2)

Usage:
  python stage1_transcribe.py --url "https://www.youtube.com/watch?v=..." --output ./output
  python stage1_transcribe.py --url "..." --output ./output --model large-v3 --device cuda
"""

import argparse
import json
import os
import sys
from pathlib import Path

# ── Dependencies ────────────────────────────────────────────────────────────
# pip install yt-dlp faster-whisper
try:
    import yt_dlp
except ImportError:
    sys.exit("Missing dependency: pip install yt-dlp")

try:
    from faster_whisper import WhisperModel
except ImportError:
    sys.exit("Missing dependency: pip install faster-whisper")


# ── Helpers ─────────────────────────────────────────────────────────────────

def download_video(url: str, output_dir: Path) -> Path:
    """
    Download the best available mp4 from a YouTube URL.
    Returns the path to the downloaded video file.
    """
    video_path = output_dir / "video.mp4"

    if video_path.exists():
        print(f"[stage1] Video already downloaded at {video_path}, skipping.")
        return video_path

    print(f"[stage1] Downloading video from: {url}")

    ydl_opts = {
        # Best video + audio merged into a single mp4
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": str(video_path),
        "merge_output_format": "mp4",
        "quiet": False,
        "no_warnings": False,
        # Write video metadata so later stages can read duration, title, etc.
        "writeinfojson": True,
"postprocessors": [{
    "key": "FFmpegVideoConvertor",
    "preferedformat": "mp4",
}],
"ignoreerrors": False,   # keep True only during testing
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    if not video_path.exists():
        raise FileNotFoundError(
            f"Download appeared to succeed but {video_path} was not found. "
            "Check yt-dlp output above for errors."
        )

    print(f"[stage1] Video saved to: {video_path}")
    return video_path


def transcribe_video(
    video_path: Path,
    output_dir: Path,
    model_size: str = "large-v3",
    device: str = "auto",
    compute_type: str = "auto",
) -> dict:
    """
    Transcribe a video file using faster-whisper.
    Returns a structured transcript dict and writes it to disk.

    The returned dict has the shape:
    {
        "language": "en",
        "duration": 1234.5,          # total video duration in seconds
        "segments": [
            {
                "id": 0,
                "start": 0.0,
                "end": 4.2,
                "text": "Hey guys, welcome back.",
                "words": [
                    {"word": "Hey",     "start": 0.0,  "end": 0.3,  "probability": 0.99},
                    {"word": "guys",    "start": 0.3,  "end": 0.6,  "probability": 0.98},
                    ...
                ]
            },
            ...
        ]
    }
    """
    transcript_json_path = output_dir / "transcript.json"
    transcript_txt_path  = output_dir / "transcript.txt"

    if transcript_json_path.exists():
        print(f"[stage1] Transcript already exists at {transcript_json_path}, skipping.")
        with open(transcript_json_path) as f:
            return json.load(f)

    # ── Resolve device + compute type ───────────────────────────────────────
    # "auto" picks cuda if available, otherwise cpu.
    if device == "auto":
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device = "cpu"

    if compute_type == "auto":
        # float16 on GPU, int8 on CPU (best speed/accuracy tradeoff)
        compute_type = "float16" if device == "cuda" else "int8"

    print(f"[stage1] Loading Whisper model '{model_size}' on {device} ({compute_type})")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    print(f"[stage1] Transcribing: {video_path}")
    segments_iter, info = model.transcribe(
        str(video_path),
        word_timestamps=True,  # critical — gives us per-word start/end times
        vad_filter=True,       # skip silent sections for speed
        vad_parameters={
            "min_silence_duration_ms": 500,
        },
        beam_size=5,
        language=None,         # auto-detect language
    )

    # ── Collect segments ─────────────────────────────────────────────────────
    segments = []
    plain_lines = []

    for seg in segments_iter:
        words = [
            {
                "word":        w.word.strip(),
                "start":       round(w.start, 3),
                "end":         round(w.end,   3),
                "probability": round(w.probability, 4),
            }
            for w in (seg.words or [])
        ]

        segment_dict = {
            "id":    seg.id,
            "start": round(seg.start, 3),
            "end":   round(seg.end,   3),
            "text":  seg.text.strip(),
            "words": words,
        }

        segments.append(segment_dict)
        plain_lines.append(f"[{_fmt_time(seg.start)} --> {_fmt_time(seg.end)}] {seg.text.strip()}")

        # Stream progress to console
        print(f"  [{_fmt_time(seg.start)}] {seg.text.strip()[:80]}")

    # ── Build final output dict ──────────────────────────────────────────────
    transcript = {
        "language": info.language,
        "language_probability": round(info.language_probability, 4),
        "duration": round(info.duration, 3),
        "segments": segments,
    }

    # ── Write to disk ────────────────────────────────────────────────────────
    with open(transcript_json_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, indent=2, ensure_ascii=False)

    with open(transcript_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(plain_lines))

    print(f"\n[stage1] Transcript JSON  → {transcript_json_path}")
    print(f"[stage1] Transcript TXT   → {transcript_txt_path}")
    print(f"[stage1] Language detected: {info.language} ({info.language_probability:.0%} confidence)")
    print(f"[stage1] Duration: {_fmt_time(info.duration)} | Segments: {len(segments)}")

    return transcript


def _fmt_time(seconds: float) -> str:
    """Format seconds as HH:MM:SS for readable console output."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:05.2f}"


# ── Main ─────────────────────────────────────────────────────────────────────

def run(url: str, output_dir: str, model_size: str, device: str) -> dict:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    video_path = download_video(url, out)
    transcript = transcribe_video(video_path, out, model_size=model_size, device=device)

    print("\n[stage1] Done. Outputs ready for Stage 2.")
    return transcript


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stage 1: Download + Transcribe")
    parser.add_argument("--url",    required=True,          help="YouTube video URL")
    parser.add_argument("--output", default="./output",     help="Output directory (default: ./output)")
    parser.add_argument("--model",  default="large-v3",
                        choices=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
                        help="Whisper model size (default: large-v3)")
    parser.add_argument("--device", default="auto",
                        choices=["auto", "cuda", "cpu"],
                        help="Inference device (default: auto)")
    args = parser.parse_args()

    run(
        url=args.url,
        output_dir=args.output,
        model_size=args.model,
        device=args.device,
    )