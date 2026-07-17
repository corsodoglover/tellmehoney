import os, json, time, getpass, requests

VOICE_ID = "xD7uM8nFCPAfVZGo37va"
OUT_DIR  = "honey_voice"
MODEL    = "eleven_multilingual_v2"
SPEED    = 0.78
SRC      = "honey_pet_jokes_2part.json"

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    if not os.path.exists(SRC):
        print("Can't find " + SRC + " in this folder."); return
    lines = json.load(open(SRC))
    print(str(len(lines)) + " clips to record (skipping any that exist)\n")
    key = os.environ.get("ELEVENLABS_KEY", "").strip()
    if not key:
        key = getpass.getpass("Paste your ElevenLabs API key (hidden), then Enter: ").strip()
    if not key:
        print("No key given."); return
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + VOICE_ID
    headers = {"xi-api-key": key, "Content-Type": "application/json"}
    total = len(lines); done = 0; skipped = 0; failed = 0
    for e in lines:
        fname = e["id"]; text = e["text"]
        out = os.path.join(OUT_DIR, fname + ".mp3")
        if os.path.exists(out):
            skipped += 1; done += 1; print("skip (exists): " + fname); continue
        payload = {"text": text, "model_id": MODEL,
                   "voice_settings": {"stability":0.5,"similarity_boost":0.75,"style":0.0,"speed":SPEED}}
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=60)
            if r.status_code == 200:
                with open(out,"wb") as f: f.write(r.content)
                done += 1; print("[" + str(done) + "/" + str(total) + "] saved " + fname + ".mp3")
            else:
                failed += 1; print("ERROR " + fname + ": " + str(r.status_code) + " " + r.text[:120])
        except Exception as ex:
            failed += 1; print("ERROR " + fname + ": " + str(ex))
        time.sleep(0.4)
    print("\n" + "="*46)
    print("  recorded : " + str(done - skipped))
    print("  skipped  : " + str(skipped))
    print("  failed   : " + str(failed))
    print("="*46)

main()
