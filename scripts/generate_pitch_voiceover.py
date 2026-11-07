#!/usr/bin/env python3
"""
Generate human-like voiceover audio for the 2-minute pitch deck using Kokoro-82M ONNX local TTS.
Generates:
1. Individual slide audio files (for slide-by-slide playback in the web deck)
2. Master continuous 120-second voiceover track with natural pacing
"""

import os
import sys
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

# Paths
CACHE_DIR = os.path.expanduser("~/.cache/kokoro")
MODEL_PATH = os.path.join(CACHE_DIR, "kokoro-v1.0.onnx")
VOICES_PATH = os.path.join(CACHE_DIR, "voices-v1.0.bin")

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "presentation", "audio"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Master 2-Minute Script (7 slides calibrated for ~120s total runtime)
SLIDES_SCRIPT = [
    {
        "slide": 1,
        "title": "The Asymmetric Trap",
        "target_sec": 16.0,
        "text": "In Sydney real estate, buyers are flying blind. Listing agents routinely underquote price guides by fifteen percent to lure crowds to auction, while hiding strata history, leaving buyers to waste thousands on building inspections for homes they can never afford."
    },
    {
        "slide": 2,
        "title": "In-Situ Reality",
        "target_sec": 18.0,
        "text": "We didn't build another localhost dashboard that nobody visits. MicroTruth is a Chrome extension that meets buyers where they actually search: directly on Domain and Real Estate dot com dot au. The moment you view a listing, the truth is injected right beneath the agent's price guide."
    },
    {
        "slide": 3,
        "title": "The Underquote Reality Badge",
        "target_sec": 18.0,
        "text": "Here, the agent quotes seven hundred and twenty thousand dollars. MicroTruth queries Microburbs valuation models in real time, exposing an estimated value of eight hundred and five thousand dollars—a twelve percent underquote. We establish a realistic auction clearance corridor so buyers know their true competition before spending a dime on legal review."
    },
    {
        "slide": 4,
        "title": "Inside The Building Ledger",
        "target_sec": 20.0,
        "text": "Click 'Inspect', and the side drawer slides in. We indexed over one hundred and twelve thousand leases and eighty-one thousand sales across Sydney in a high-speed SQLite engine. Browsing Unit 105 immediately surfaces the last five sales and leases inside this exact building that the agent chose not to mention."
    },
    {
        "slide": 5,
        "title": "Machine Learning Pricing Rigor",
        "target_sec": 20.0,
        "text": "Behind the UI sits serious machine learning. For Task 4, our rental pricing model trained on one hundred and four thousand leases cut the median dollar error to fifty-nine dollars per week—beating the Microburbs baseline by over thirty-one percent. For Task 5, we valued all one hundred and eighty-one thousand properties across the City of Sydney."
    },
    {
        "slide": 6,
        "title": "The Negotiation Weapon",
        "target_sec": 16.0,
        "text": "Information without action is useless. MicroTruth turns suburb trends and inside-the-building comps into a formal, unyielding offer letter in one click. Buyers export a data-backed counter-offer directly to their clipboard ready to email the listing agent."
    },
    {
        "slide": 7,
        "title": "Why MicroTruth Wins",
        "target_sec": 12.0,
        "text": "Production-grade machine learning, zero fake dashboards, and real human leverage. MicroTruth Sydney levels the playing field before you bid."
    }
]

def generate_voiceover(voice="am_adam", speed=1.0):
    print(f"Initializing Kokoro ONNX TTS with voice '{voice}'...")
    kokoro = Kokoro(MODEL_PATH, VOICES_PATH)
    
    sample_rate = 24000
    all_audio_segments = []
    
    print("\nGenerating slide-by-slide audio tracks:")
    total_speech_sec = 0.0
    
    for item in SLIDES_SCRIPT:
        slide_num = item["slide"]
        text = item["text"]
        target = item["target_sec"]
        
        # Synthesize audio
        samples, sr = kokoro.create(text, voice=voice, speed=speed, lang="en-us")
        duration = len(samples) / sr
        total_speech_sec += duration
        
        # Save individual slide audio
        slide_wav = os.path.join(OUTPUT_DIR, f"slide_{slide_num}.wav")
        slide_mp3 = os.path.join(OUTPUT_DIR, f"slide_{slide_num}.mp3")
        sf.write(slide_wav, samples, sr)
        
        # Convert to MP3 using ffmpeg
        os.system(f"ffmpeg -y -i '{slide_wav}' -codec:a libmp3lame -qscale:a 2 '{slide_mp3}' -loglevel error")
        
        print(f"  Slide {slide_num} ({item['title']}): {duration:.2f}s (Target: {target}s) -> saved to slide_{slide_num}.mp3")
        
        # Add samples to master track
        all_audio_segments.append(samples)
        # Add 1.0s natural pause between slides (except after last slide)
        if slide_num < len(SLIDES_SCRIPT):
            pause_samples = np.zeros(int(sr * 1.2), dtype=samples.dtype)
            all_audio_segments.append(pause_samples)

    # Concatenate master track
    master_audio = np.concatenate(all_audio_segments)
    master_duration = len(master_audio) / sample_rate
    
    master_wav = os.path.join(OUTPUT_DIR, "pitch_voiceover.wav")
    master_mp3 = os.path.join(OUTPUT_DIR, "pitch_voiceover.mp3")
    
    sf.write(master_wav, master_audio, sample_rate)
    
    # Mastering with subtle EBU R128 loudness normalization and high-pass filter
    ffmpeg_cmd = (
        f"ffmpeg -y -i '{master_wav}' "
        f"-af 'highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11' "
        f"-codec:a libmp3lame -b:a 192k '{master_mp3}' -loglevel error"
    )
    os.system(ffmpeg_cmd)
    
    print(f"\n Master Voiceover Complete!")
    print(f"Total Spoken Speech: {total_speech_sec:.2f}s")
    print(f"Master Contiguous Audio: {master_duration:.2f}s (~{master_duration/60:.2f} minutes)")
    print(f"Saved to: {master_mp3}")
    
    return master_mp3

if __name__ == "__main__":
    voice = sys.argv[1] if len(sys.argv) > 1 else "am_adam"
    speed = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    generate_voiceover(voice=voice, speed=speed)
