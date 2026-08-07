#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  record_calm_batch.py
#
#  Two jobs in one pass, both at the slow calm settings the bedtime stories use.
#
#  1. THE 60 PUZZLE LINES — re-recorded
#     These already exist and every one of the 1,500 word slots across 150
#     puzzle days resolves to one of them. Nothing is missing. The problem is
#     that they were cut loud and bright, so "Great, you spotted that" arrives
#     like a shout in the middle of a quiet game.
#
#  2. THE 12 JOURNAL PROMPTS — recorded for the first time
#     DJ_PROMPTS has twelve gentle questions and not one of them has ever had a
#     clip. They were on the old recording sheet as dj_prompt_001 to 012 and
#     were never made. Honey has been silent on every one.
#
#     These also need map entries adding to index.html — without them the
#     lookup never finds the files. Those lines are printed at the end.
#
#  SETTINGS
#      speed          0.72    same as the bedtime stories
#      stability      0.95    the model reads, it does not perform
#      style          0.0     no performance at all
#      speaker boost  OFF     this is what made the first pass loud
#
#  A note on the speed: 0.72 on a four-word line like "Joy — the good kind."
#  is already very slow. Going below that tends to sound laboured rather than
#  calm. Listen to a couple before deciding to go further down.
#
#  RUN IT, from the tellmehoney folder:
#     export ELEVEN_KEY="sk_your_key_here"
#     python3 record_calm_batch.py
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

#  SPEAKER BOOST OFF. That is what made these loud.
#  It lifts perceived volume, which barely shows on a two-minute story but
#  lands like a shout on a four-word line such as "Joy — the good kind."
#  Stability up to 0.95 and style to 0 as well: on short text the model has
#  no room to settle, so it needs to be told not to perform at all.
SETTINGS = {
    "stability": 0.72, "similarity_boost": 0.85,
    "style": 0.32, "use_speaker_boost": False, "speed": 0.72,
}

#  The puzzle lines are four or five words long and 0.72 still runs them
#  together. A shorter line gives the model no room to settle, so it needs
#  slower again — and a leading ellipsis, which reads as a pause and lets her
#  arrive calm instead of starting mid-breath.
#
#  Padding the recorded text is safe: the lookup matches the app's text to a
#  CLIP NAME, and the file only has to carry the right name. What gets spoken
#  into it is ours to choose.
PUZZLE_SETTINGS = dict(SETTINGS); PUZZLE_SETTINGS["speed"] = 0.74
PUZZLE_LEAD = ""

PUZZLE_LINES = [
    ("puzzle_line_01", "A blessing, counted."),
    ("puzzle_line_02", "Blessings, more than we can count."),
    ("puzzle_line_03", "A giggle! I heard that."),
    ("puzzle_line_04", "A hug! Consider yourself squeezed."),
    ("puzzle_line_05", "A joke! Want one after this?"),
    ("puzzle_line_06", "A little verse to carry with you."),
    ("puzzle_line_07", "A nap sounds just right."),
    ("puzzle_line_08", "A smile looks good on you."),
    ("puzzle_line_09", "Calm as a Sunday morning."),
    ("puzzle_line_10", "Comfort. Come sit a while."),
    ("puzzle_line_11", "Friendship \u2014 the whole point, isn't it?"),
    ("puzzle_line_12", "Grace \u2014 enough for today."),
    ("puzzle_line_13", "Gratitude. It changes everything."),
    ("puzzle_line_14", "Joy \u2014 the good kind."),
    ("puzzle_line_15", "Kindness. Never goes out of style."),
    ("puzzle_line_16", "Laughter. Best medicine there is."),
    ("puzzle_line_17", "Memories \u2014 the ones worth keeping."),
    ("puzzle_line_18", "Merry and bright, that's you."),
    ("puzzle_line_19", "Out on the porch where the good talks happen."),
    ("puzzle_line_20", "Peace. Hold onto that one."),
    ("puzzle_line_21", "Pie! Now you're talking."),
    ("puzzle_line_22", "Rest. You've earned it."),
    ("puzzle_line_23", "Sunday \u2014 a day to slow down."),
    ("puzzle_line_24", "Sunshine, even on a gray day."),
    ("puzzle_line_25", "Sweet. Just like you."),
    ("puzzle_line_26", "The grandkids! Light of your life."),
    ("puzzle_line_27", "There I am, sweet as ever."),
    ("puzzle_line_28", "Time for a cup of tea, I'd say."),
    ("puzzle_line_29", "Warmth \u2014 that's what we're about."),
    ("puzzle_line_30", "Morning \u2014 the best part of the day."),
    ("puzzle_line_31", "Evening, when the day goes soft."),
    ("puzzle_line_32", "Afternoon. The slow, easy stretch."),
    ("puzzle_line_33", "Moonlight \u2014 the world in its quiet clothes."),
    ("puzzle_line_34", "A quilt. Somebody's hours, keeping you warm."),
    ("puzzle_line_35", "The garden's getting on fine without us."),
    ("puzzle_line_36", "A neighbor \u2014 the kind who knocks."),
    ("puzzle_line_37", "The kitchen. Where everybody ends up anyway."),
    ("puzzle_line_38", "A story. Those are worth slowing down for."),
    ("puzzle_line_39", "The rocking chair knows what it's doing."),
    ("puzzle_line_40", "A whisper. The quietest kind of company."),
    ("puzzle_line_41", "A chuckle. That's the good stuff."),
    ("puzzle_line_42", "A butterfly. Somebody's having a nice day."),
    ("puzzle_line_43", "The breeze is doing the work today."),
    ("puzzle_line_44", "Rain on the roof \u2014 best sound there is."),
    ("puzzle_line_45", "Shade. The good chair's already in it."),
    ("puzzle_line_46", "Cozy \u2014 the whole point of a house."),
    ("puzzle_line_47", "Cookies. There's always one more."),
    ("puzzle_line_48", "Lemonade weather, if you ask me."),
    ("puzzle_line_49", "An apple, straight off the tree if you're lucky."),
    ("puzzle_line_50", "A swing. Back and forth, no hurry."),
    ("puzzle_line_51", "The dog's already at the door."),
    ("puzzle_line_52", "The cat has claimed that spot."),
    ("puzzle_line_53", "A bird, singing at nobody in particular."),
    ("puzzle_line_54", "Flowers. Somebody planted those on purpose."),
    ("puzzle_line_55", "A treasure \u2014 the kind you don't put down."),
    ("puzzle_line_56", "Wonderful. And I don't say that lightly."),
    ("puzzle_line_57", "Tender \u2014 that's a whole way of being."),
    ("puzzle_line_58", "A lullaby. Somebody's getting sleepy."),
    ("puzzle_line_59", "Home. That word does a lot of work."),
    ("puzzle_line_60", "Heart \u2014 the whole business, really."),
]

JOURNAL_PROMPTS = [
    ("dj_prompt_001", "What made you smile today?"),
    ("dj_prompt_002", "Who are you grateful for right now \u2014 and why?"),
    ("dj_prompt_003", "What's something small that went right today?"),
    ("dj_prompt_004", "If today had a title, what would it be?"),
    ("dj_prompt_005", "What do you want to remember about this day a year from now?"),
    ("dj_prompt_006", "What's on your heart this evening?"),
    ("dj_prompt_007", "Describe a moment today you'd like to keep."),
    ("dj_prompt_008", "What did you learn about yourself lately?"),
    ("dj_prompt_009", "Who did you talk to today, and how are they?"),
    ("dj_prompt_010", "What are you looking forward to tomorrow?"),
    ("dj_prompt_011", "What's a little thing that made you laugh?"),
    ("dj_prompt_012", "Where did you feel most like yourself today?"),
]


def to_m4a(mp3_path, out_path):
    r = subprocess.run(
        ["afconvert", "-f", "m4af", "-d", "aac", "-b", "64000",
         "--mix", "-c", "1", str(mp3_path), str(out_path)],
        capture_output=True, text=True)
    return r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 500


def record(name, text, url, headers):
    out = ROOT_DIR / (name + ".m4a")
    settings = SETTINGS
    if name.startswith("puzzle_line") or name.startswith("pz_"):
        settings = PUZZLE_SETTINGS
        text = PUZZLE_LEAD + text.replace("\u2014", "\u2026")
    r = requests.post(url, headers=headers,
                      json={"text": text, "model_id": MODEL,
                            "voice_settings": settings}, timeout=90)
    if r.status_code != 200 or len(r.content) < 1000:
        return False, "error " + str(r.status_code) + ": " + r.text[:100]
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
        tf.write(r.content); tmp = pathlib.Path(tf.name)
    ok = to_m4a(tmp, out)
    try: tmp.unlink()
    except Exception: pass
    if not ok:
        return False, "conversion to .m4a failed"
    try:
        (WWW_DIR / out.name).write_bytes(out.read_bytes())
    except Exception as e:
        return True, "root only, not www/: " + str(e)
    return True, ""


def main():
    if not API_KEY:
        print('\nNo ElevenLabs key. Set it first:')
        print('   export ELEVEN_KEY="sk_your_key_here"')
        sys.exit(1)
    if not ROOT_DIR.exists():
        print("\nCan't find honey_voice/. Run this from the tellmehoney folder.")
        sys.exit(1)
    WWW_DIR.mkdir(parents=True, exist_ok=True)

    total = len(PUZZLE_LINES) + len(JOURNAL_PROMPTS)
    print("\n" + str(len(PUZZLE_LINES)) + " puzzle lines re-recorded calm")
    print(str(len(JOURNAL_PROMPTS)) + " journal prompts recorded for the first time")
    print("all at speed 0.72, the bedtime story pace")
    if input("\nGo ahead? (y/n) ").strip().lower() != "y":
        print("Stopped. Nothing changed.")
        return

    url = "https://api.elevenlabs.io/v1/text-to-speech/" + VOICE_ID
    headers = {"xi-api-key": API_KEY, "Content-Type": "application/json"}
    made = failed = 0
    n = 0

    for label, rows in [("puzzle", PUZZLE_LINES), ("prompt", JOURNAL_PROMPTS)]:
        print("\n--- " + label + " ---")
        for name, text in rows:
            n += 1
            tag = "[" + str(n).rjust(2) + "/" + str(total) + "]"
            try:
                ok, note = record(name, text, url, headers)
                if ok:
                    print("  " + tag + "  " + name.ljust(18) + text[:44])
                    if note: print("            ! " + note)
                    made += 1
                else:
                    print("  " + tag + "  " + name + "   x " + note)
                    failed += 1
            except Exception as e:
                print("  " + tag + "  " + name + "   x " + str(e))
                failed += 1
            time.sleep(0.5)

    print("\nRecorded " + str(made) + ", failed " + str(failed) + ".")

    if made:
        print("\nListen to one of each:")
        print("   afplay honey_voice/puzzle_line_14.m4a")
        print("   afplay honey_voice/dj_prompt_001.m4a")
        print("\n" + "=" * 70)
        print("THE JOURNAL PROMPTS NEED MAP ENTRIES OR THEY WILL NEVER PLAY.")
        print("Paste these into index.html beside the other HONEY_AUDIO_MAP lines:")
        print("=" * 70)
        for name, text in JOURNAL_PROMPTS:
            key = " ".join(text.strip().lower().split())
            print('HONEY_AUDIO_MAP["' + key.replace('"', '\\"') + '"]=\'' + name + "';")
        print("=" * 70)


if __name__ == "__main__":
    main()
