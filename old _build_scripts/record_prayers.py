#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  record_prayers.py
#
#  Records the four prayers in Honey's (Sally's) cloned voice, saving them as
#  prayer_01.mp3 … prayer_04.mp3 into your honey_voice/ folder.
#
#  prayer_01 = The Lord's Prayer (Sally's version)
#  prayer_02 = The Lord's Prayer (traditional)
#  prayer_03 = Now I Lay Me Down to Sleep
#  prayer_04 = The Serenity Prayer
#
#  HOW TO RUN (Terminal, from your tellmehoney folder):
#     1.  export ELEVEN_KEY="sk_your_key_here"
#     2.  python3 record_prayers.py
#
#  Already-recorded files are skipped, so re-running is safe.
# ─────────────────────────────────────────────────────────────────────────────

import os, sys, time, pathlib, requests

VOICE_ID = "xD7uM8nFCPAfVZGo37va"
MODEL    = "eleven_flash_v2_5"
OUT_DIR  = pathlib.Path("honey_voice")
API_KEY  = os.environ.get("ELEVEN_KEY", "").strip()

# Gentle, slow, reverent — like saying it at the bedside.
VOICE_SETTINGS = {"stability":0.72, "similarity_boost":0.85, "style":0.12, "use_speaker_boost":True}

PRAYERS = [
    # prayer_01 — Sally's Lord's Prayer (ellipses pace the gentle delivery)
    ("Our Father, who art in Heaven… hallowed be thy name. "
     "Thy kingdom come, thy will be done… on Earth as it is in Heaven. "
     "Give us this day our daily bread… and forgive us of our trespasses, "
     "as we forgive those who trespass against us. "
     "And lead us not into temptation… but deliver us far, far away from evil. "
     "For thine is the kingdom, and the power, and the glory… forever and ever. Amen."),

    # prayer_02 — traditional Lord's Prayer
    ("Our Father, who art in heaven… hallowed be thy name. "
     "Thy kingdom come, thy will be done… on earth as it is in heaven. "
     "Give us this day our daily bread… and forgive us our trespasses, "
     "as we forgive those who trespass against us. "
     "And lead us not into temptation… but deliver us from evil. "
     "For thine is the kingdom, and the power, and the glory… forever and ever. Amen."),

    # prayer_03 — Now I Lay Me Down to Sleep (gentle modern wording)
    ("Now I lay me down to sleep… I pray the Lord my soul to keep. "
     "Watch and guard me through the night… and wake me with the morning light. Amen."),

    # prayer_04 — Serenity Prayer
    ("God, grant me the serenity… to accept the things I cannot change, "
     "the courage to change the things I can… and the wisdom to know the difference. Amen."),
]

def main():
    if not API_KEY:
        print("\nERROR: no ElevenLabs key found.")
        print('Set it first:   export ELEVEN_KEY="sk_your_key_here"')
        sys.exit(1)
    OUT_DIR.mkdir(exist_ok=True)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": API_KEY, "Content-Type": "application/json"}
    made = skipped = failed = 0
    for i, text in enumerate(PRAYERS, start=1):
        name = f"prayer_{i:02d}.mp3"
        path = OUT_DIR / name
        if path.exists() and path.stat().st_size > 1000:
            print(f"  {name}  — already there, skipping"); skipped += 1; continue
        body = {"text": text, "model_id": MODEL, "voice_settings": VOICE_SETTINGS}
        try:
            print(f"  recording {name} …")
            r = requests.post(url, headers=headers, json=body, timeout=120)
            if r.status_code == 200 and len(r.content) > 1000:
                path.write_bytes(r.content); print(f"  {name}  ✓"); made += 1
            else:
                print(f"  {name}  ✗ error {r.status_code}: {r.text[:120]}"); failed += 1
        except Exception as e:
            print(f"  {name}  ✗ {e}"); failed += 1
        time.sleep(0.6)
    print(f"\nDone. recorded {made}, skipped {skipped}, failed {failed}.")
    print("Push with:  git add -A && git commit -m 'prayer voice clips' && git push")

if __name__ == "__main__":
    main()
