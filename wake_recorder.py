#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  record_wake_lines.py
#
#  Fifteen new lines for coming back to the app.
#
#  WHY
#  There were three. This fires every single time somebody returns, which for
#  most people is many times a day, so three on rotation stopped being variety
#  and started being a tic — "Awake again. Pick up right where we left off?"
#  became the only thing she seemed to know how to say.
#
#  With these there are eighteen. The three originals are already recorded as
#  phrase_058, phrase_008 and phrase_088 and are not touched.
#
#  HOW THEY ARE READ
#  Short and low. She is speaking without being asked, and somebody coming back
#  to a phone in a quiet room does not want a performance. Several are three
#  words. The job is to acknowledge, not to announce.
#
#      speed          0.76    unhurried, but these are short
#      stability      0.72    steady without going flat
#      style          0.22    a little warmth, no performance
#      speaker boost  OFF     these play unasked; they must not startle
#
#  Em dashes are swapped for ellipses in the recorded text only. ElevenLabs
#  runs a dash into the next word — "Right — I'm" came out as "righttt" on the
#  puzzle lines. The lookup matches the app's text to a CLIP NAME, so what gets
#  spoken into the file is ours to choose.
#
#  RUN IT, from the tellmehoney folder:
#     export ELEVEN_KEY="sk_your_key_here"
#     python3 record_wake_lines.py
# ─────────────────────────────────────────────────────────────────────────────

import os, sys, time, pathlib, subprocess, tempfile

try:
    import requests
except ImportError:
    print("\nNeed the requests library first:  pip3 install requests")
    sys.exit(1)

VOICE_ID = "xD7uM8nFCPAfVZGo37va"
MODEL    = "eleven_flash_v2_5"
API_KEY  = os.environ.get("ELEVEN_KEY", "").strip()

ROOT_DIR = pathlib.Path("honey_voice")
WWW_DIR  = pathlib.Path("www/honey_voice")

SETTINGS = {
    "stability": 0.72, "similarity_boost": 0.85,
    "style": 0.22, "use_speaker_boost": False, "speed": 0.76,
}

LINES = [
    ("phrase_wake_01", "Back with you."),
    ("phrase_wake_02", "Still here. Go on."),
    ("phrase_wake_03", "That's better. Where'd we get to?"),
    ("phrase_wake_04", "Right \u2014 I'm with you again."),
    ("phrase_wake_05", "Good, you're still about."),
    ("phrase_wake_06", "I didn't go anywhere."),
    ("phrase_wake_07", "Picking it back up."),
    ("phrase_wake_08", "There now. Carry on."),
    ("phrase_wake_09", "Still listening."),
    ("phrase_wake_10", "Ready when you are."),
    ("phrase_wake_11", "I kept your place."),
    ("phrase_wake_12", "Where were we, then?"),
    ("phrase_wake_13", "Back in the room."),
    ("phrase_wake_14", "Go on, I'm here."),
    ("phrase_wake_15", "That's us, then. Carry on."),
]


def to_m4a(mp3_path, out_path):
    r = subprocess.run(
        ["afconvert", "-f", "m4af", "-d", "aac", "-b", "64000",
         "--mix", "-c", "1", str(mp3_path), str(out_path)],
        capture_output=True, text=True)
    return r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 500


def main():
    if not API_KEY:
        print('\nNo ElevenLabs key. Set it first:')
        print('   export ELEVEN_KEY="sk_your_key_here"')
        sys.exit(1)
    if not ROOT_DIR.exists():
        print("\nCan't find honey_voice/. Run this from the tellmehoney folder.")
        sys.exit(1)
    WWW_DIR.mkdir(parents=True, exist_ok=True)

    url = "https://api.elevenlabs.io/v1/text-to-speech/" + VOICE_ID
    headers = {"xi-api-key": API_KEY, "Content-Type": "application/json"}
    made = skipped = failed = 0
    total = len(LINES)

    print("\nRecording " + str(total) + " coming-back lines.\n")

    for idx, (name, text) in enumerate(LINES, start=1):
        out = ROOT_DIR / (name + ".m4a")
        tag = "[" + str(idx).rjust(2) + "/" + str(total) + "]"

        if out.exists() and out.stat().st_size > 500:
            print("  " + tag + "  " + name + "  — already there")
            skipped += 1
            continue

        spoken = text.replace("\u2014", "\u2026")   # dash reads as a syllable

        try:
            print("  " + tag + "  " + name.ljust(16) + text)
            r = requests.post(url, headers=headers,
                              json={"text": spoken, "model_id": MODEL,
                                    "voice_settings": SETTINGS}, timeout=90)
            if r.status_code != 200 or len(r.content) < 1000:
                print("            x error " + str(r.status_code) + ": " + r.text[:110])
                failed += 1
                continue
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
                tf.write(r.content); tmp = pathlib.Path(tf.name)
            ok = to_m4a(tmp, out)
            try: tmp.unlink()
            except Exception: pass
            if not ok:
                print("            x conversion to .m4a failed"); failed += 1; continue
            try:
                (WWW_DIR / out.name).write_bytes(out.read_bytes())
            except Exception as e:
                print("            ! root only, not www/: " + str(e))
            made += 1
        except Exception as e:
            print("            x " + str(e)); failed += 1
        time.sleep(0.5)

    print("\nRecorded " + str(made) + ", skipped " + str(skipped) + ", failed " + str(failed) + ".")
    if made:
        print("\nListen to a few — they should sound like somebody glancing up,")
        print("not like somebody making an announcement:")
        print("   afplay honey_voice/phrase_wake_01.m4a")
        print("   afplay honey_voice/phrase_wake_09.m4a")
        print("   afplay honey_voice/phrase_wake_13.m4a")


if __name__ == "__main__":
    main()
