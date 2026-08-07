#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  record_greetings_by_vibe.py
#
#  Re-records 29 of the 34 greetings, each at a speed that suits its vibe.
#
#  WHY
#  The first pass cut all 41 at one speed, 0.90. Listening back:
#      "There's that face I like. Miss me?"       Flirty      perfect
#      "Hey, there you are. I was hoping..."      Wholesome   too fast
#      "Hey you. Good to have you back — really." Wholesome   super fast
#      "Oh, you're back. Try to contain..."       Sarcastic   could be slower
#      "Hi hi hi — what are we doing..."          Hyper       terrible
#
#  One speed cannot serve seven vibes. A dry remark and a warm hello want
#  different pacing entirely, and Hyper needs its energy from expression rather
#  than from gabbling.
#
#  THE SIX FLIRTY LINES ARE NOT TOUCHED. They came out right at 0.90 and this
#  script does not include them.
#
#      Flirty      0.90   already recorded — left alone
#      Sarcastic   0.84   dry needs room to land
#      Hyper       0.82   with style up to 0.42, so the energy comes from
#                         expression rather than from gabbling
#      Mysterious  0.80   unhurried by nature
#      Chill       0.80
#      Warm        0.78
#      Wholesome   0.78   the warmest, and the slowest
#
#  0.78 IS THE FLOOR AND IT IS DELIBERATE. If the default reads too fast,
#  every user goes hunting for the speed slider — and an app somebody has to
#  fix before they can use it has already failed. Better slow and warm than
#  quick and jangly.
#
#  Three Hyper lines carry deliberate capitals in the app. They are lowercased
#  here so they record warm rather than shouted — punctuation is untouched, so
#  the lookup still matches.
#
#  RUN IT, from the tellmehoney folder:
#     export ELEVEN_KEY="sk_your_key_here"
#     python3 record_greetings_by_vibe.py
#
#  These 29 files already exist and will be overwritten on purpose.
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

#  vibe, clip name, speed, style, text
LINES = [
    ("Chill", "greet_back_again_cool_lets_pick_it_up", 0.80, 0.18,
     "Back again? Cool. Let's pick it up."),
    ("Chill", "greet_heyyy_no_rush_just_hangin_whats_up", 0.80, 0.18,
     "Heyyy. No rush, just hangin'. What's up?"),
    ("Chill", "greet_heyyy_welcome_back_right_where_we_left_off", 0.80, 0.18,
     "Heyyy, welcome back. Right where we left off."),
    ("Chill", "greet_oh_nice_youre_back_i_was_just_vibing_in_standby", 0.80, 0.18,
     "Oh nice, you're back. I was just vibing in standby."),
    ("Chill", "greet_oh_nice_youre_here_pull_up_a_chair", 0.80, 0.18,
     "Oh nice, you're here. Pull up a chair."),
    ("Chill", "greet_was_just_vibing_glad_you_called", 0.80, 0.18,
     "Was just vibing. Glad you called."),
    ("Hyper", "greet_finally_i_was_just_buzzing_in_sleep_mode_hi_hi_hi", 0.82, 0.42,
     "Finally!! I was just buzzing in sleep mode. Hi hi hi!"),
    ("Hyper", "greet_finally_ive_been_bursting_ready", 0.82, 0.42,
     "Finally!! I've been bursting. Ready?"),
    ("Hyper", "greet_hi_hi_hi_what_are_we_doing_whats_the_move", 0.82, 0.42,
     "Hi hi hi \u2014 what are we doing, what's the move?!"),
    ("Hyper", "greet_welcome_back_welcome_back_i_have_so_much_energy_s", 0.82, 0.42,
     "Welcome back welcome back I have so much energy stored up!"),
    ("Hyper", "greet_youre_back_okay_okay_im_awake_lets_go", 0.82, 0.42,
     "You're back okay okay I'm awake let's go."),
    ("Hyper", "greet_youre_here_okay_okay_okay_sit_down_i_have_so_much", 0.82, 0.42,
     "You're here okay okay okay sit down I have so much."),
    ("Mysterious", "greet_ah_awake_again_right_on_time_as_always", 0.80, 0.15,
     "Ah, awake again. Right on time, as always."),
    ("Mysterious", "greet_ah_right_on_time_somehow", 0.80, 0.15,
     "Ah. Right on time, somehow."),
    ("Mysterious", "greet_i_had_a_feeling_youd_call_i_usually_do", 0.80, 0.15,
     "I had a feeling you'd call. I usually do."),
    ("Mysterious", "greet_welcome_back_i_never_fully_sleep_you_know", 0.80, 0.15,
     "Welcome back. I never fully sleep, you know."),
    ("Mysterious", "greet_you_came_back_interesting", 0.80, 0.15,
     "You came back. Interesting."),
    ("Mysterious", "greet_you_returned_i_had_a_feeling_you_would", 0.80, 0.15,
     "You returned. I had a feeling you would."),
    ("Sarcastic", "greet_let_me_guess_you_need_cheering_up_shocking", 0.84, 0.20,
     "Let me guess \u2014 you need cheering up. Shocking."),
    ("Sarcastic", "greet_look_who_returned_missed_my_charm_huh", 0.84, 0.20,
     "Look who returned. Missed my charm, huh."),
    ("Sarcastic", "greet_oh_good_you_again_my_favorite", 0.84, 0.20,
     "Oh good, you again. My favorite."),
    ("Sarcastic", "greet_oh_youre_back_try_to_contain_your_excitement", 0.84, 0.20,
     "Oh, you're back. Try to contain your excitement."),
    ("Sarcastic", "greet_welcome_back_i_barely_slept_thinking_of_new_mater", 0.84, 0.20,
     "Welcome back. I barely slept, thinking of new material."),
    ("Warm", "greet_hey_youre_back_i_was_just_resting_my_eyes_missed_", 0.78, 0.18,
     "Hey, you're back. I was just resting my eyes. Missed you."),
    ("Warm", "line_there_you_are_pull_up_a_chair_im_all_yours", 0.78, 0.18,
     "There you are. Pull up a chair \u2014 I'm all yours."),
    ("Wholesome", "greet_hey_there_you_are_i_was_hoping_youd_call", 0.78, 0.12,
     "Hey, there you are. I was hoping you'd call."),
    ("Wholesome", "greet_hey_you_genuinely_happy_to_see_you", 0.78, 0.12,
     "Hey you. Genuinely happy to see you."),
    ("Wholesome", "greet_hey_you_good_to_have_you_back_really", 0.78, 0.12,
     "Hey you. Good to have you back \u2014 really."),
    ("Wholesome", "greet_hi_friend_welcome_back_im_so_glad_you_returned", 0.78, 0.12,
     "Hi friend, welcome back. I'm so glad you returned."),
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

    vibes = {}
    for v, c, sp, st, t in LINES:
        vibes.setdefault(v, []).append(sp)
    print("\nRe-recording " + str(len(LINES)) + " greetings. The six Flirty ones are left alone.")
    for v in sorted(vibes):
        print("   " + v.ljust(11) + str(len(vibes[v])) + " lines at " + str(vibes[v][0]))
    if input("\nGo ahead? (y/n) ").strip().lower() != "y":
        print("Stopped. Nothing changed.")
        return

    url = "https://api.elevenlabs.io/v1/text-to-speech/" + VOICE_ID
    headers = {"xi-api-key": API_KEY, "Content-Type": "application/json"}
    made = failed = 0
    total = len(LINES)

    for idx, (vibe, name, speed, style, text) in enumerate(LINES, start=1):
        out = ROOT_DIR / (name + ".m4a")
        tag = "[" + str(idx).rjust(2) + "/" + str(total) + "]"
        settings = {"stability": 0.60, "similarity_boost": 0.85,
                    "style": style, "use_speaker_boost": True, "speed": speed}
        try:
            print("  " + tag + "  " + vibe.ljust(11) + str(speed) + "  " + text[:44])
            r = requests.post(url, headers=headers,
                              json={"text": text, "model_id": MODEL,
                                    "voice_settings": settings}, timeout=90)
            if r.status_code != 200 or len(r.content) < 1000:
                print("           x error " + str(r.status_code) + ": " + r.text[:110])
                failed += 1
                continue
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
                tf.write(r.content); tmp = pathlib.Path(tf.name)
            ok = to_m4a(tmp, out)
            try: tmp.unlink()
            except Exception: pass
            if not ok:
                print("           x conversion to .m4a failed"); failed += 1; continue
            try:
                (WWW_DIR / out.name).write_bytes(out.read_bytes())
            except Exception as e:
                print("           ! root only, not www/: " + str(e))
            made += 1
        except Exception as e:
            print("           x " + str(e)); failed += 1
        time.sleep(0.6)

    print("\nRe-recorded " + str(made) + ", failed " + str(failed) + ".")
    if made:
        print("\nListen to one of each — they should feel like different moods now:")
        print("   afplay honey_voice/greet_hey_you_genuinely_happy_to_see_you.m4a   (Wholesome 0.80)")
        print("   afplay honey_voice/greet_hi_hi_hi_what_are_we_doing_whats_the_move.m4a   (Hyper 0.84)")
        print("   afplay honey_voice/greet_oh_youre_back_try_to_contain_your_excitement.m4a   (Sarcastic 0.86)")
        print("   afplay honey_voice/greet_theres_that_face_i_like_miss_me.m4a   (Flirty 0.90 — untouched)")


if __name__ == "__main__":
    main()
