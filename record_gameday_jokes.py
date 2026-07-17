#!/usr/bin/env python3
"""
Tell Me Honey - GAME DAY + NOW WHERE WAS I + ANIMAL FARM recorder
Records the 196 trimmed jokes (392 clips) in Honey's cloned voice, matching
your existing library exactly (SPEED 0.78 - the proven settings).

HOW TO RUN (Mac):
  1) Put THIS file AND honey_jokes_2part_GAMEDAY.json in the SAME folder
     (your ~/Desktop/tellmehoney folder is perfect).
  2) Open Terminal and go to that folder, e.g.:
        cd ~/Desktop/tellmehoney
  3) First time only:   pip3 install requests
  4) Run it:            python3 record_gameday_jokes.py
  5) Paste your ElevenLabs API key when asked (it is NOT saved).

Saves MP3s into  honey_jokes_audio/  next to this script.
Already-made files are skipped, so re-running never charges twice.
When done, move/copy them in with your existing honey_voice clips, then push.

** Nothing to edit in this file - it already points at the Game Day JSON. **
"""

import json, os, sys, time, getpass

# --- your voice + the PROVEN joke settings (do not change) ---
VOICE_ID   = "xD7uM8nFCPAfVZGo37va"
MODEL_ID   = "eleven_flash_v2_5"
SPEED      = 0.78
VOICE_SETTINGS = {"stability": 0.5, "similarity_boost": 0.75, "style": 0.0, "speed": SPEED}

OUTPUT_DIR = "honey_jokes_audio"
LINES_FILE = "honey_jokes_2part_GAMEDAY.json"   # <-- already set for you

def main():
    try:
        import requests
    except ImportError:
        print("\nInstall the one library first, then run again:\n    pip3 install requests\n")
        sys.exit(1)

    if not os.path.exists(LINES_FILE):
        print(f"\n!!  Can't find {LINES_FILE}. Put it in the SAME folder as this script.\n")
        sys.exit(1)

    api_key = getpass.getpass("Paste your ElevenLabs API key, then press Enter (stays private): ").strip()
    if not api_key:
        print("No key entered. Stopping."); sys.exit(1)

    with open(LINES_FILE, encoding="utf-8") as f:
        lines = json.load(f)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total = len(lines); made = skipped = failed = 0
    print(f"\nRecording {total} clips in voice {VOICE_ID} at speed {SPEED}.")
    print(f"Saving into ./{OUTPUT_DIR}/  (already-made files are skipped)\n")

    for i, item in enumerate(lines, 1):
        fid = item["id"]; text = item["text"]
        out_path = os.path.join(OUTPUT_DIR, fid + ".mp3")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            skipped += 1; continue
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"}
        body = {"text": text, "model_id": MODEL_ID, "voice_settings": VOICE_SETTINGS}
        try:
            r = requests.post(url, headers=headers, json=body, timeout=60)
            if r.status_code == 200:
                with open(out_path, "wb") as out: out.write(r.content)
                made += 1; print(f"[{i}/{total}] ok  {fid}")
            elif r.status_code == 401:
                print("\nX  Key not valid (401). Check your API key and run again.\n"); sys.exit(1)
            elif r.status_code == 429:
                print(f"[{i}/{total}] rate limit - waiting 20s then retrying...");  time.sleep(20)
                r2 = requests.post(url, headers=headers, json=body, timeout=60)
                if r2.status_code == 200:
                    with open(out_path, "wb") as out: out.write(r2.content)
                    made += 1; print(f"[{i}/{total}] ok  {fid} (after wait)")
                else:
                    failed += 1; print(f"[{i}/{total}] X  {fid} ({r2.status_code}) - run again to retry")
            else:
                failed += 1; print(f"[{i}/{total}] X  {fid} ({r.status_code})")
        except Exception as e:
            failed += 1; print(f"[{i}/{total}] X  {fid} (error: {e}) - run again to retry")
        time.sleep(0.2)

    print(f"\nDone. Made {made}, skipped {skipped} (already existed), failed {failed}.")
    if failed:
        print("Some failed - just run the script again; it skips finished ones and retries the rest.")
    print(f"\nYour clips are in ./{OUTPUT_DIR}/  -  move them in with your honey_voice clips, then push.\n")

if __name__ == "__main__":
    main()