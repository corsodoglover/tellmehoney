#!/usr/bin/env python3
"""
Tell Me Honey - INTRO LINES generator
Records the 7 "before a joke" intro lines in your ElevenLabs cloned voice.
These are the lines like "Alright, here's one for you —" that play right
before a joke. The main app already knows these filenames.

HOW TO RUN (Mac):
  1) Put this file in the SAME folder as your honey_voice folder
     (e.g. ~/Desktop/tellmehoney).
  2) Open Terminal:   cd ~/Desktop/tellmehoney
  3) First time only: pip3 install requests
  4) Run it:          python3 generate_intro_lines.py
  5) Paste your ElevenLabs API key when asked (it is NOT saved or shared).

It saves 7 MP3s straight into your honey_voice folder. Already-made files
are skipped, so running twice never charges you twice.
"""

import os, sys, time, getpass

# Same voice as your other clips:
VOICE_ID = "xD7uM8nFCPAfVZGo37va"
MODEL_ID = "eleven_flash_v2_5"
OUTPUT_DIR = "honey_voice"     # save straight into the folder the app uses

# filename  ->  exact words to say
LINES = {
    "intro_warm":      "Alright, here's one for you —",
    "intro_flirty":    "Okay, just for you —",
    "intro_sarcastic": "Brace yourself, comedy incoming —",
    "intro_chill":     "So, no pressure, but —",
    "intro_hyper":     "OKAY OKAY listen to this one —",
    "intro_wholesome": "Here's a little something —",
    "intro_mysterious":"Lean in for this one…",
}

def main():
    try:
        import requests
    except ImportError:
        print("\nThe 'requests' library isn't installed yet.")
        print("Type this in Terminal, then run the script again:\n")
        print("    pip3 install requests\n")
        sys.exit(1)

    if not os.path.isdir(OUTPUT_DIR):
        print(f"\n⚠️  Can't find a '{OUTPUT_DIR}' folder here.")
        print("Run this from your tellmehoney folder (the one with honey_voice in it).\n")
        sys.exit(1)

    api_key = getpass.getpass("Paste your ElevenLabs API key, then press Enter (it stays private): ").strip()
    if not api_key:
        print("No key entered. Stopping."); sys.exit(1)

    total = len(LINES); made = 0; skipped = 0; failed = 0
    print(f"\nMaking {total} intro clips in voice {VOICE_ID}.")
    print(f"Saving into ./{OUTPUT_DIR}/  (already-made files are skipped)\n")

    for fid, text in LINES.items():
        out_path = os.path.join(OUTPUT_DIR, fid + ".mp3")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            skipped += 1
            print(f"• {fid} already exists — skipping")
            continue
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"}
        body = {"text": text, "model_id": MODEL_ID,
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}
        try:
            r = requests.post(url, headers=headers, json=body, timeout=60)
            if r.status_code == 200:
                with open(out_path, "wb") as out:
                    out.write(r.content)
                made += 1
                print(f"✓ {fid}  «{text}»")
            elif r.status_code == 401:
                print("\n✗ Key not valid (401). Check your API key and run again.\n"); sys.exit(1)
            elif r.status_code == 429:
                print(f"… rate/credit limit on {fid} — waiting 20s then retrying")
                time.sleep(20)
                r2 = requests.post(url, headers=headers, json=body, timeout=60)
                if r2.status_code == 200:
                    with open(out_path, "wb") as out: out.write(r2.content)
                    made += 1; print(f"✓ {fid} (after wait)")
                else:
                    failed += 1; print(f"✗ {fid} (status {r2.status_code}) — run again later")
            else:
                failed += 1; print(f"✗ {fid} (status {r.status_code})")
        except Exception as e:
            failed += 1; print(f"✗ {fid} (error: {e}) — run again later")
        time.sleep(0.25)

    print(f"\nDone. New: {made}   Already had: {skipped}   Failed: {failed}")
    if failed:
        print("Some failed — just run the script again; it only retries the missing ones.")
    else:
        print("All 7 intro lines are in ./honey_voice/  🍯  Push to GitHub and they'll play in your voice.")

if __name__ == "__main__":
    main()
