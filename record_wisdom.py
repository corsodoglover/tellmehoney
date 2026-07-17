#!/usr/bin/env python3
import json, os, sys, time, getpass

VOICE_ID   = "xD7uM8nFCPAfVZGo37va"
MODEL_ID   = "eleven_flash_v2_5"
SPEED      = 0.78
VOICE_SETTINGS = {"stability": 0.5, "similarity_boost": 0.75, "style": 0.0, "speed": SPEED}

OUTPUT_DIR = "honey_wisdom_audio"
LINES_FILE = "honey_greatgrandma_wisdom.json"

def main():
    try:
        import requests
    except ImportError:
        print("Install requests first: pip3 install requests")
        sys.exit(1)

    if not os.path.exists(LINES_FILE):
        print("Cannot find " + LINES_FILE + " - put it in the same folder.")
        sys.exit(1)

    api_key = getpass.getpass("Paste your ElevenLabs API key, then press Enter: ").strip()
    if not api_key:
        print("No key entered. Stopping.")
        sys.exit(1)

    with open(LINES_FILE, encoding="utf-8") as f:
        lines = json.load(f)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total = len(lines)
    made = 0
    skipped = 0
    failed = 0
    print("Recording " + str(total) + " clips at speed " + str(SPEED))
    print("Saving into ./" + OUTPUT_DIR + "/ (already-made files are skipped)")

    for i, item in enumerate(lines, 1):
        fid = item["id"]
        text = item["text"]
        out_path = os.path.join(OUTPUT_DIR, fid + ".mp3")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            skipped += 1
            continue
        url = "https://api.elevenlabs.io/v1/text-to-speech/" + VOICE_ID
        headers = {"xi-api-key": api_key, "Content-Type": "application/json", "Accept": "audio/mpeg"}
        body = {"text": text, "model_id": MODEL_ID, "voice_settings": VOICE_SETTINGS}
        try:
            r = requests.post(url, headers=headers, json=body, timeout=60)
            if r.status_code == 200:
                with open(out_path, "wb") as out:
                    out.write(r.content)
                made += 1
                print("[" + str(i) + "/" + str(total) + "] ok " + fid)
            elif r.status_code == 401:
                print("Key not valid (401). Check your API key and run again.")
                sys.exit(1)
            elif r.status_code == 429:
                print("[" + str(i) + "/" + str(total) + "] limit - waiting 20s")
                time.sleep(20)
                r2 = requests.post(url, headers=headers, json=body, timeout=60)
                if r2.status_code == 200:
                    with open(out_path, "wb") as out:
                        out.write(r2.content)
                    made += 1
                    print("[" + str(i) + "/" + str(total) + "] ok " + fid + " (after wait)")
                else:
                    failed += 1
                    print("[" + str(i) + "/" + str(total) + "] fail " + fid)
            else:
                failed += 1
                print("[" + str(i) + "/" + str(total) + "] fail " + fid + " (" + str(r.status_code) + ")")
        except Exception as e:
            failed += 1
            print("[" + str(i) + "/" + str(total) + "] fail " + fid + " - run again to retry")
        time.sleep(0.25)

    print("Done. New: " + str(made) + "  Already had: " + str(skipped) + "  Failed: " + str(failed))
    if failed:
        print("Some failed - just run again; it only retries the missing ones.")
    else:
        print("All clips are in ./" + OUTPUT_DIR + "/  Move them in with honey_voice, then push.")

if __name__ == "__main__":
    main()