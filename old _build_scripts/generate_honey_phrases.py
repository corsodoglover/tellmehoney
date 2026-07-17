#!/usr/bin/env python3
"""
Tell Me Honey - voice library generator
Generates all 769 jokes + verses as MP3s in your ElevenLabs cloned voice (Flash model).

HOW TO RUN (Mac):
  1) Put this file AND honey_phrases.json in the SAME folder (e.g. a folder on your Desktop).
  2) Open Terminal, then type:  cd ~/Desktop/honey         (or wherever you put them)
  3) First time only, install the one library:  pip3 install requests
  4) Run it:  python3 generate_honey_voice.py
  5) When it asks, paste your ElevenLabs API key and press Enter. (It is NOT saved or shared.)

It saves MP3s into a folder called  honey_phrases_audio  next to this script.
If it stops for any reason, just run it again - it SKIPS files it already made,
so you never pay twice for the same clip.
"""

import json, os, sys, time, getpass

# ============================================================
#  >>> PASTE YOUR VOICE ID BELOW (between the quotes) <<<
#  Find it on ElevenLabs: Voices -> click your cloned voice -> copy the Voice ID.
VOICE_ID = "xD7uM8nFCPAfVZGo37va"
# ============================================================

MODEL_ID = "eleven_flash_v2_5"     # Flash = half the credits, great quality
OUTPUT_DIR = "honey_phrases_audio"
LINES_FILE = "honey_phrases.json"

def main():
    try:
        import requests
    except ImportError:
        print("\nThe 'requests' library isn't installed yet.")
        print("Type this in Terminal, then run the script again:\n")
        print("    pip3 install requests\n")
        sys.exit(1)

    if VOICE_ID == "PASTE_YOUR_VOICE_ID_HERE" or not VOICE_ID.strip():
        print("\n⚠️  You need to paste your Voice ID into the script first.")
        print("Open generate_honey_voice.py, find the VOICE_ID line near the top,")
        print("and put your ElevenLabs Voice ID between the quotes. Then run again.\n")
        sys.exit(1)

    if not os.path.exists(LINES_FILE):
        print(f"\n⚠️  Can't find {LINES_FILE}. Make sure it's in the SAME folder as this script.\n")
        sys.exit(1)

    api_key = getpass.getpass("Paste your ElevenLabs API key, then press Enter (it stays private): ").strip()
    if not api_key:
        print("No key entered. Stopping."); sys.exit(1)

    with open(LINES_FILE, encoding="utf-8") as f:
        lines = json.load(f)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total = len(lines)
    made = 0; skipped = 0; failed = 0
    print(f"\nGenerating {total} clips in voice {VOICE_ID} using {MODEL_ID}.")
    print(f"Saving into ./{OUTPUT_DIR}/  (already-made files are skipped)\n")

    for i, item in enumerate(lines, 1):
        fid = item["id"]; text = item["text"]
        out_path = os.path.join(OUTPUT_DIR, fid + ".mp3")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            skipped += 1
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
                print(f"[{i}/{total}] ✓ {fid}")
            elif r.status_code == 401:
                print("\n✗ Key not valid (401). Check your API key and run again.\n"); sys.exit(1)
            elif r.status_code == 429:
                print(f"[{i}/{total}] rate/credit limit — waiting 20s then retrying…")
                time.sleep(20)
                r2 = requests.post(url, headers=headers, json=body, timeout=60)
                if r2.status_code == 200:
                    with open(out_path, "wb") as out: out.write(r2.content)
                    made += 1; print(f"[{i}/{total}] ✓ {fid} (after wait)")
                else:
                    failed += 1; print(f"[{i}/{total}] ✗ {fid} (status {r2.status_code}) — run again later to retry")
            else:
                failed += 1
                print(f"[{i}/{total}] ✗ {fid} (status {r.status_code})")
        except Exception as e:
            failed += 1
            print(f"[{i}/{total}] ✗ {fid} (error: {e}) — run again later to retry")
        time.sleep(0.25)  # gentle pacing

    print(f"\nDone. New: {made}   Already had: {skipped}   Failed: {failed}")
    if failed:
        print("Some failed — just run the script again; it will only retry the missing ones.")
    else:
        print(f"All {total} clips are in ./{OUTPUT_DIR}/  🍯  Zip that folder and send it back.")

if __name__ == "__main__":
    main()
