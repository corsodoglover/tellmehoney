#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  record_replies.py
#
#  Twenty-eight lines written on 3 August that have never had a voice.
#
#      goodbyes        "Night. Sleep well."
#      compliments     "That's kind of you to say."
#      kind wishes     "That's a nice thing to say. Same to you."
#      daytime byes    "See you later, then."
#
#  All of them appeared on screen and said nothing, because a line with no clip
#  is silent on Honey's own voice — which is the right way round, but it means
#  the whole of the new conversational warmth was mute.
#
#  HOW THEY ARE READ
#  These are answers to somebody being kind, or leaving. Quiet, unhurried, no
#  performance. The same treatment as the coming-back lines.
#
#      speed          0.78
#      stability      0.72
#      style          0.22
#      speaker boost  OFF
#
#  Em dashes become ellipses in the recorded text only — ElevenLabs runs a dash
#  into the next word. The lookup matches the app's text to a CLIP NAME, so what
#  is spoken into the file is ours to choose.
#
#  RUN IT, from the tellmehoney folder:
#     export ELEVEN_KEY="sk_your_key_here"
#     python3 record_replies.py
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
    "style": 0.22, "use_speaker_boost": False, "speed": 0.78,
}

LINES = [
    ("kindwish_01",
     "That's kind of you. I am, thank you."),
    ("kindwish_02",
     "Thank you \u2014 nobody usually asks."),
    ("kindwish_03",
     "I am, now that you're here."),
    ("kindwish_04",
     "That's a nice thing to say. Same to you."),
    ("kindwish_05",
     "Thank you. It's a good one so far."),
    ("kindwish_06",
     "Well aren't you sweet. I am, thank you."),
    ("kindwish_07",
     "Better now you've stopped by."),
    ("compliment_01",
     "That's kind of you to say."),
    ("compliment_02",
     "Well now. Thank you."),
    ("compliment_03",
     "Thank you. That means something."),
    ("compliment_04",
     "I'll take that. Thank you."),
    ("compliment_05",
     "That's a nice thing to hear."),
    ("compliment_06",
     "Thank you \u2014 I like our talks too."),
    ("compliment_07",
     "You're kind to say so."),
    ("bye_01",
     "Night. Sleep well."),
    ("bye_02",
     "Goodnight. I'll be here tomorrow."),
    ("bye_03",
     "Sleep well. Nothing else needs doing tonight."),
    ("bye_04",
     "Night then. Rest easy."),
    ("bye_05",
     "Off you go. I'll keep your place."),
    ("bye_06",
     "Goodnight. It was good talking to you."),
    ("bye_07",
     "Rest well. See you when you're back."),
    ("bye_08",
     "Take care. I'm not going anywhere."),
    ("byeday_01",
     "See you later, then."),
    ("byeday_02",
     "Off you go. I'll be here."),
    ("byeday_03",
     "Take care of yourself out there."),
    ("byeday_04",
     "Right you are. Come back when you like."),
    ("byeday_05",
     "Bye for now."),
    ("byeday_06",
     "Go on then. I'll keep your place."),
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

    print("\nRecording " + str(total) + " replies.\n")

    for idx, (name, text) in enumerate(LINES, start=1):
        out = ROOT_DIR / (name + ".m4a")
        tag = "[" + str(idx).rjust(2) + "/" + str(total) + "]"

        if out.exists() and out.stat().st_size > 500:
            print("  " + tag + "  " + name + "  — already there")
            skipped += 1
            continue

        spoken = text.replace("\u2014", "\u2026")

        try:
            print("  " + tag + "  " + name.ljust(15) + text)
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
        print("\nListen to one of each kind:")
        print("   afplay honey_voice/bye_01.m4a")
        print("   afplay honey_voice/compliment_01.m4a")
        print("   afplay honey_voice/kindwish_04.m4a")


if __name__ == "__main__":
    main()
