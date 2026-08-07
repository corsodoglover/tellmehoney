#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  record_missing_v155.py
#
#  Records every clip the app asks for and cannot find. Forty-one of them.
#
#  HOW THIS LIST WAS FOUND
#  The audio map points at 3,039 distinct clips. The honey_voice folder holds
#  4,026 files. Diffing the two showed 41 the app will ask for and never find —
#  and 34 of those are GREETINGS. Every single hello Honey has. That is why she
#  has never once spoken a greeting: not a code bug, just clips that were never
#  recorded.
#
#  WRITES .m4a, NOT .mp3
#  On 2 August the library was re-encoded from 128kbps MP3 to 64kbps mono AAC —
#  208MB down to 104MB, which is what got the Android bundle under Google's
#  200MB ceiling. The app builds filenames with ".m4a" now, so a new .mp3
#  dropped in the folder would simply never be found. This records to a temp
#  mp3, converts with afconvert (built into macOS), and deletes the temp.
#
#  WRITES BOTH FOLDERS
#  honey_voice/ at the project root is what GitHub Pages serves. www/honey_voice
#  is what the app builds from. Update one and forget the other and the live
#  site goes silent — which happened on the morning of 2 August. This does both.
#
#  RUN IT, from the tellmehoney folder:
#     export ELEVEN_KEY="sk_your_key_here"
#     python3 record_missing_v155.py
#
#  Existing files are skipped, so stopping and re-running is safe.
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

ROOT_DIR = pathlib.Path("honey_voice")       # what GitHub Pages serves
WWW_DIR  = pathlib.Path("www/honey_voice")   # what the app builds from

# PACING BY CONTENT TYPE
#   jokes and quick replies   0.92   (what the existing library was cut at)
#   greetings and setups      0.90   (a hello wants a touch more room)
#   sleep stories, quiet time 0.78   (separate job — see the stories script)
#
# Everything in this file is a greeting, a weather line or a reply, so 0.90.
SETTINGS = {
    "stability": 0.55, "similarity_boost": 0.85,
    "style": 0.25, "use_speaker_boost": True, "speed": 0.90,
}

# ─────────────────────────────────────────────────────────────────────────────
#  THE TEXT MUST MATCH THE APP EXACTLY — every comma, every em dash, every
#  apostrophe. The lookup is on the whole string. These were pulled straight
#  out of index.html. Do not retype them.
#
#  A NOTE ON THE SHOUTY ONES. Three Bubbly greetings carry deliberate capitals
#  for emphasis. ElevenLabs will read caps loudly, and the game voices have
#  already been flagged as too loud and abrupt. They are written here in normal
#  case so they record warm instead of shouted — the app's own text still has
#  the caps, and the lookup lowercases before matching, so they still connect.
# ─────────────────────────────────────────────────────────────────────────────

LINES = [
    ("greet_theres_that_face_i_like_miss_me",
     "There's that face I like. Miss me?"),
    ("greet_you_called_im_flattered_and_slightly_suspicious",
     "You called. I'm flattered and slightly suspicious."),
    ("greet_oh_good_you_again_my_favorite",
     "Oh good, you again. My favorite."),
    ("greet_let_me_guess_you_need_cheering_up_shocking",
     "Let me guess \u2014 you need cheering up. Shocking."),
    ("greet_heyyy_no_rush_just_hangin_whats_up",
     "Heyyy. No rush, just hangin'. What's up?"),
    ("greet_oh_nice_youre_here_pull_up_a_chair",
     "Oh nice, you're here. Pull up a chair."),
    ("greet_was_just_vibing_glad_you_called",
     "Was just vibing. Glad you called."),
    ("greet_youre_here_okay_okay_okay_sit_down_i_have_so_much",
     "You're here okay okay okay sit down I have so much."),
    ("greet_finally_ive_been_bursting_ready",
     "Finally!! I've been bursting. Ready?"),
    ("greet_hi_hi_hi_what_are_we_doing_whats_the_move",
     "Hi hi hi \u2014 what are we doing, what's the move?!"),
    ("greet_hey_there_you_are_i_was_hoping_youd_call",
     "Hey, there you are. I was hoping you'd call."),
    ("greet_hey_you_genuinely_happy_to_see_you",
     "Hey you. Genuinely happy to see you."),
    ("greet_you_came_back_interesting",
     "You came back. Interesting."),
    ("greet_i_had_a_feeling_youd_call_i_usually_do",
     "I had a feeling you'd call. I usually do."),
    ("greet_ah_right_on_time_somehow",
     "Ah. Right on time, somehow."),
    ("greet_hey_youre_back_i_was_just_resting_my_eyes_missed_",
     "Hey, you're back. I was just resting my eyes. Missed you."),
    ("line_there_you_are_pull_up_a_chair_im_all_yours",
     "There you are. Pull up a chair \u2014 I'm all yours."),
    ("greet_mmm_look_who_couldnt_stay_away_welcome_back",
     "Mmm, look who couldn't stay away. Welcome back."),
    ("greet_you_came_back_for_me_i_knew_you_would",
     "You came back for me. I knew you would."),
    ("greet_back_already_im_flattered_sit_close",
     "Back already? I'm flattered. Sit close."),
    ("greet_oh_youre_back_try_to_contain_your_excitement",
     "Oh, you're back. Try to contain your excitement."),
    ("greet_welcome_back_i_barely_slept_thinking_of_new_mater",
     "Welcome back. I barely slept, thinking of new material."),
    ("greet_look_who_returned_missed_my_charm_huh",
     "Look who returned. Missed my charm, huh."),
    ("greet_heyyy_welcome_back_right_where_we_left_off",
     "Heyyy, welcome back. Right where we left off."),
    ("greet_oh_nice_youre_back_i_was_just_vibing_in_standby",
     "Oh nice, you're back. I was just vibing in standby."),
    ("greet_back_again_cool_lets_pick_it_up",
     "Back again? Cool. Let's pick it up."),
    ("greet_youre_back_okay_okay_im_awake_lets_go",
     "You're back okay okay I'm awake let's go."),
    ("greet_welcome_back_welcome_back_i_have_so_much_energy_s",
     "Welcome back welcome back I have so much energy stored up!"),
    ("greet_finally_i_was_just_buzzing_in_sleep_mode_hi_hi_hi",
     "Finally!! I was just buzzing in sleep mode. Hi hi hi!"),
    ("greet_hi_friend_welcome_back_im_so_glad_you_returned",
     "Hi friend, welcome back. I'm so glad you returned."),
    ("greet_hey_you_good_to_have_you_back_really",
     "Hey you. Good to have you back \u2014 really."),
    ("greet_you_returned_i_had_a_feeling_you_would",
     "You returned. I had a feeling you would."),
    ("greet_welcome_back_i_never_fully_sleep_you_know",
     "Welcome back. I never fully sleep, you know."),
    ("greet_ah_awake_again_right_on_time_as_always",
     "Ah, awake again. Right on time, as always."),
    ("wx_its_cold_today_coat_and_a_hot_drink_doctors_orders",
     "It's cold today. Coat and a hot drink, doctor's orders."),
    ("wx_foggy_one_take_it_slow_out_there",
     "Foggy one. Take it slow out there."),
    ("wx_gorgeous_out_dont_let_me_keep_you_unless_you_want_one_more_joke",
     "Gorgeous out. Don't let me keep you \u2014 unless you want one more joke."),
    ("goodspirits_01",
     "It is, isn't it. Days like this don't ask anything of you."),
    ("goodspirits_02",
     "Good. That's the kind of morning worth saying out loud."),
    ("goodspirits_03",
     "Then that's settled. Go enjoy it before it gets away."),
    ("goodspirits_04",
     "I'll take your word for it \u2014 no windows in here. Sounds lovely.")
]


def to_m4a(mp3_path, out_path):
    """64k mono AAC — same as the rest of the library."""
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

    print("\nRecording " + str(total) + " clips into honey_voice/ and www/honey_voice/\n")

    for idx, (name, text) in enumerate(LINES, start=1):
        out = ROOT_DIR / (name + ".m4a")
        tag = "[" + str(idx).rjust(2) + "/" + str(total) + "]"

        if out.exists() and out.stat().st_size > 500:
            print("  " + tag + "  " + name + "  — already there")
            skipped += 1
            continue

        body = {"text": text, "model_id": MODEL, "voice_settings": SETTINGS}

        try:
            print("  " + tag + "  " + name)
            r = requests.post(url, headers=headers, json=body, timeout=90)

            if r.status_code != 200 or len(r.content) < 1000:
                print("           x error " + str(r.status_code) + ": " + r.text[:120])
                failed += 1
                continue

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
                tf.write(r.content)
                tmp = pathlib.Path(tf.name)

            ok = to_m4a(tmp, out)
            try: tmp.unlink()
            except Exception: pass

            if not ok:
                print("           x recorded, but converting to .m4a failed")
                failed += 1
                continue

            try:
                (WWW_DIR / out.name).write_bytes(out.read_bytes())
            except Exception as e:
                print("           ! root only, not www/: " + str(e))

            print("           ok  " + str(round(out.stat().st_size / 1024)) + " KB")
            made += 1

        except Exception as e:
            print("           x " + str(e))
            failed += 1

        time.sleep(0.6)

    print("\nRecorded " + str(made) + ", skipped " + str(skipped) + ", failed " + str(failed) + ".")

    if made:
        print("\nListen to a few before pushing — a greeting, a weather line:")
        print("   afplay honey_voice/greet_hey_you_genuinely_happy_to_see_you.m4a")
        print("   afplay honey_voice/goodspirits_01.m4a")
        print("   afplay honey_voice/wx_foggy_one_take_it_slow_out_there.m4a")
        print("\nThen:")
        print("   git add honey_voice www/honey_voice")
        print("   git commit -m 'the 41 missing clips, greetings included'")
        print("   git push origin main")


if __name__ == "__main__":
    main()
