#!/usr/bin/env python3
"""
Generate Australian Neural Voiceover for the 2-Minute Pitch Deck using Edge-TTS (en-AU-WilliamNeural).
Outputs:
1. Individual slide audio files (slide_1_au.mp3 ... slide_7_au.mp3)
2. Master contiguous audio track (pitch_voiceover_au.mp3)
3. Durations JSON (durations.json) for video alignment
"""

import os
import json
import asyncio
import edge_tts

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "presentation", "audio"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

SLIDES_SCRIPT = [
    {
        "slide": 1,
        "title": "The Asymmetric Trap",
        "text": "In Sydney real estate, buyers are flying blind. Listing agents routinely underquote price guides by fifteen percent to lure crowds to auction, while hiding strata history, leaving buyers to waste thousands on building inspections for homes they can never afford."
    },
    {
        "slide": 2,
        "title": "In-Situ Reality",
        "text": "We didn't build another localhost dashboard that nobody visits. MicroTruth is a Chrome extension that meets buyers where they actually search: directly on Domain and Real Estate dot com dot au. The moment you view a listing, the truth is injected right beneath the agent's price guide."
    },
    {
        "slide": 3,
        "title": "The Underquote Reality Badge",
        "text": "Here, the agent quotes seven hundred and twenty thousand dollars. MicroTruth queries Microburbs valuation models in real time, exposing an estimated value of eight hundred and five thousand dollars—a twelve percent underquote. We establish a realistic auction clearance corridor so buyers know their true competition before spending a dime on legal review."
    },
    {
        "slide": 4,
        "title": "Inside The Building Ledger",
        "text": "Click 'Inspect', and the side drawer slides in. We indexed over one hundred and twelve thousand leases and eighty-one thousand sales across Sydney in a high-speed SQLite engine. Browsing Unit 105 immediately surfaces the last five sales and leases inside this exact building that the agent chose not to mention."
    },
    {
        "slide": 5,
        "title": "Machine Learning Pricing Rigor",
        "text": "Behind the UI sits serious machine learning. For Task 4, our rental pricing model trained on one hundred and four thousand leases cut the median dollar error to fifty-nine dollars per week—beating the Microburbs baseline by over thirty-one percent. For Task 5, we valued all one hundred and eighty-one thousand properties across the City of Sydney."
    },
    {
        "slide": 6,
        "title": "The Negotiation Weapon",
        "text": "Information without action is useless. MicroTruth turns suburb trends and inside-the-building comps into a formal, unyielding offer letter in one click. Buyers export a data-backed counter-offer directly to their clipboard ready to email the listing agent."
    },
    {
        "slide": 7,
        "title": "Why MicroTruth Wins",
        "text": "Production-grade machine learning, zero fake dashboards, and real human leverage. MicroTruth Sydney levels the playing field before you bid."
    }
]

async def generate_au_audio(voice="en-AU-WilliamNeural", rate="+2%"):
    print(f"Generating Australian Neural audio with voice '{voice}', rate '{rate}'...")
    durations = []
    slide_files = []
    
    for item in SLIDES_SCRIPT:
        slide_num = item["slide"]
        text = item["text"]
        out_mp3 = os.path.join(OUTPUT_DIR, f"slide_{slide_num}_au.mp3")
        
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(out_mp3)
        
        # Get duration using ffprobe
        import subprocess
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", out_mp3],
            capture_output=True, text=True, check=True
        )
        dur = float(probe.stdout.strip())
        durations.append({"slide": slide_num, "title": item["title"], "duration": dur, "file": out_mp3})
        slide_files.append(out_mp3)
        print(f"  Slide {slide_num} ({item['title']}): {dur:.2f}s -> {out_mp3}")
    
    # Create concatenated master track with 0.8s silence pause between slides
    silence_file = os.path.join(OUTPUT_DIR, "silence_08s.mp3")
    os.system(f"ffmpeg -y -f lavfi -i anullsrc=r=48000:cl=stereo -t 0.8 -qscale:a 2 '{silence_file}' -loglevel error")
    
    concat_list = os.path.join(OUTPUT_DIR, "concat_list.txt")
    with open(concat_list, "w") as f:
        for i, s_file in enumerate(slide_files):
            f.write(f"file '{s_file}'\n")
            if i < len(slide_files) - 1:
                f.write(f"file '{silence_file}'\n")
    
    master_au_mp3 = os.path.join(OUTPUT_DIR, "pitch_voiceover_au.mp3")
    master_raw_wav = os.path.join(OUTPUT_DIR, "pitch_voiceover_au_raw.wav")
    
    os.system(f"ffmpeg -y -f concat -safe 0 -i '{concat_list}' -c copy '{master_au_mp3}' -loglevel error")
    
    # Master audio with high-pass 80Hz and EBU R128 loudness normalization
    master_final_mp3 = os.path.join(OUTPUT_DIR, "pitch_voiceover_au_mastered.mp3")
    os.system(
        f"ffmpeg -y -i '{master_au_mp3}' "
        f"-af 'highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11' "
        f"-codec:a libmp3lame -b:a 192k '{master_final_mp3}' -loglevel error"
    )
    
    # Read final master duration
    import subprocess
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", master_final_mp3],
        capture_output=True, text=True, check=True
    )
    total_dur = float(probe.stdout.strip())
    
    durations_json = os.path.join(OUTPUT_DIR, "durations_au.json")
    with open(durations_json, "w") as f:
        json.dump({"total_duration": total_dur, "slides": durations}, f, indent=2)
        
    print(f"\n Master Australian Audio Complete!")
    print(f"Total Duration: {total_dur:.2f}s (~{total_dur/60:.2f} minutes)")
    print(f"Saved to: {master_final_mp3}")
    
    return master_final_mp3, durations_json

if __name__ == "__main__":
    asyncio.run(generate_au_audio())
