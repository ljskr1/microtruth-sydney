#!/usr/bin/env python3
"""
Generate action-synchronized Kokoro voiceover for the 41.93s pitch.mp4 video and mux them together.
"""

import os
import sys
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

CACHE_DIR = os.path.expanduser("~/.cache/kokoro")
MODEL_PATH = os.path.join(CACHE_DIR, "kokoro-v1.0.onnx")
VOICES_PATH = os.path.join(CACHE_DIR, "voices-v1.0.bin")

VIDEO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "submission", "pitch.mp4"))
OUT_AUDIO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "recordings", "pitch_video_voiceover.wav"))
OUT_AUDIO_MP3 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "recordings", "pitch_video_voiceover.mp3"))
COMBINED_VIDEO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "submission", "pitch_with_voiceover.mp4"))

# Calibrated cues for the 41.93s video:
CUES = [
    {
        "start": 0.5,
        "text": "In Sydney, property listings rarely tell the whole story. Agents underquote price guides to pack auctions with hopeful buyers."
    },
    {
        "start": 6.5,
        "text": "MicroTruth changes that. Right on Domain, our badge compares the agent's guide against Microburbs data, instantly exposing a twelve percent underquote."
    },
    {
        "start": 14.0,
        "text": "Click 'Inspect', and the drawer slides in—revealing the live suburb boundary and three core market signals, showing homes here clear in just 27 days."
    },
    {
        "start": 23.5,
        "text": "Best of all: the Building Ledger. We indexed municipal records to reveal five recent sales and leases inside this exact block that the agent didn't advertise."
    },
    {
        "start": 33.5,
        "text": "One click turns those comps into an unyielding offer letter ready for your clipboard. Level the playing field before you bid."
    }
]

def generate_and_combine(voice="am_adam", speed=1.03):
    print("Initializing Kokoro ONNX...")
    kokoro = Kokoro(MODEL_PATH, VOICES_PATH)
    sample_rate = 24000
    
    # 41.93s total duration at 24000Hz
    total_samples = int(41.93 * sample_rate)
    master_audio = np.zeros(total_samples, dtype=np.float32)
    
    print("\nSynthesizing video-synchronized voiceover cues:")
    for cue in CUES:
        start_sec = cue["start"]
        text = cue["text"]
        samples, sr = kokoro.create(text, voice=voice, speed=speed, lang="en-us")
        dur = len(samples) / sr
        start_idx = int(start_sec * sample_rate)
        end_idx = min(start_idx + len(samples), total_samples)
        
        # Place into timeline
        master_audio[start_idx:end_idx] = samples[:end_idx - start_idx]
        print(f"  [{start_sec:.1f}s - {start_sec + dur:.1f}s] ({dur:.2f}s): {text[:60]}...")
    
    # Save master audio
    sf.write(OUT_AUDIO, master_audio, sample_rate)
    
    # Process audio with ffmpeg (highpass, subtle compression, loudness normalization)
    cmd_audio = (
        f"ffmpeg -y -i '{OUT_AUDIO}' "
        f"-af 'highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11' "
        f"-codec:a libmp3lame -b:a 192k '{OUT_AUDIO_MP3}' -loglevel error"
    )
    os.system(cmd_audio)
    print(f"\nVoiceover audio generated: {OUT_AUDIO_MP3}")
    
    # Mux into video
    cmd_mux = (
        f"ffmpeg -y -i '{VIDEO_PATH}' -i '{OUT_AUDIO_MP3}' "
        f"-c:v copy -c:a aac -b:a 192k -map 0:v:0 -map 1:a:0 -shortest '{COMBINED_VIDEO}' -loglevel error"
    )
    os.system(cmd_mux)
    print(f"Combined video saved to: {COMBINED_VIDEO}")
    
    # Check properties
    os.system(f"ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name -of default=noprint_wrappers=1 '{COMBINED_VIDEO}'")
    
    return COMBINED_VIDEO

if __name__ == "__main__":
    generate_and_combine()
