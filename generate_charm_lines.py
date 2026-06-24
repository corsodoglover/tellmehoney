#!/usr/bin/env python3
"""
Tell Me Honey - CHARM LINES generator
Records the new greeting + calendar/list/call lines in your ElevenLabs voice.
The app already knows these filenames. Saves straight into honey_voice.

HOW TO RUN (Mac):
  1) Put this file in your tellmehoney folder (next to honey_voice).
  2) Terminal:  cd ~/Desktop/tellmehoney
  3) First time only:  pip3 install requests
  4) Run:  python3 generate_charm_lines.py
  5) Paste your ElevenLabs API key when asked (stays private).
Already-made files are skipped, so re-running never double-charges.
"""
import os, sys, time, getpass

VOICE_ID = "xD7uM8nFCPAfVZGo37va"
MODEL_ID = "eleven_flash_v2_5"
OUTPUT_DIR = "honey_voice"

LINES = {
    'line_aw_thats_already_on_your_list': "Aw, that's already on your list.",
    'line_aw_you_came_back_that_made_my_whole_day_thank_you': 'Aw, you came back. That made my whole day, thank you.',
    'line_calling_me_bold_i_respect_it': 'Calling me? Bold. I respect it.',
    'line_good_to_see_your_name_pop_up_how_are_you_really': 'Good to see your name pop up. How are you, really?',
    'line_got_it_thank_you_ill_remember_that_number_tap_to_c': "Got it, thank you — I'll remember that number. Tap to call",
    'line_got_it_thank_you_tap_to_add_it_to_your_calendar': 'Got it, thank you. Tap to add it to your calendar',
    'line_heres_your_list': "Here's your list",
    'line_hi_friend_thank_you_for_coming_to_see_me_today': 'Hi, friend. Thank you for coming to see me today.',
    'line_i_saved_it_to_your_list_too_say_whats_on_my_calend': 'I saved it to your list too —\x80\x94 say "what\'s on my calendar" anytime.',
    'line_look_who_it_is_come_on_in_sit_down_tell_me_everyth': 'Look who it is — come on in, sit down, tell me everything.',
    'line_now_what_can_i_add_for_you_and_to_which_list': 'Now what can I add for you, and to which list?',
    'line_saved_thank_you_tap_to_give_them_a_call': 'Saved, thank you. Tap to give them a call',
    'line_there_you_are_darlin_pull_up_a_chair_im_all_yours': "There you are, darlin'. Pull up a chair — I'm all yours.",
    'line_welcome_back_glad_you_woke_me_up_thank_you': 'Welcome back. Glad you woke me up, thank you.',
    'line_well_hello_there_took_you_long_enough': 'Well hello there. Took you long enough.',
    'line_well_hey_there_i_was_hoping_youd_come_see_me': "Well, hey there. I was hoping you'd come see me.",
    'line_your_lists_empty_for_now_just_tell_me_what_you_nee': "Your list's empty for now — just tell me what you need."
}

def main():
    try:
        import requests
    except ImportError:
        print("\nInstall the helper first:  pip3 install requests\n"); sys.exit(1)
    if not os.path.isdir(OUTPUT_DIR):
        print(f"\n⚠️  Run this from your tellmehoney folder (the one with {OUTPUT_DIR} in it).\n"); sys.exit(1)
    api_key = getpass.getpass("Paste your ElevenLabs API key, then Enter (stays private): ").strip()
    if not api_key:
        print("No key entered. Stopping."); sys.exit(1)
    total=len(LINES); made=skipped=failed=0
    print(f"\nMaking {total} charm clips in voice {VOICE_ID}.\nSaving into ./{OUTPUT_DIR}/\n")
    for fid,text in LINES.items():
        out=os.path.join(OUTPUT_DIR, fid+".mp3")
        if os.path.exists(out) and os.path.getsize(out)>0:
            skipped+=1; print(f"• {fid} already exists — skipping"); continue
        url=f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers={"xi-api-key":api_key,"Content-Type":"application/json","Accept":"audio/mpeg"}
        body={"text":text,"model_id":MODEL_ID,"voice_settings":{"stability":0.5,"similarity_boost":0.8}}
        try:
            r=requests.post(url,headers=headers,json=body,timeout=60)
            if r.status_code==200:
                open(out,"wb").write(r.content); made+=1; print(f"✓ {fid}  «{text}»")
            elif r.status_code==401:
                print("\n✗ Key not valid (401). Check it and run again.\n"); sys.exit(1)
            elif r.status_code==429:
                print(f"… limit on {fid}; waiting 20s"); time.sleep(20)
                r2=requests.post(url,headers=headers,json=body,timeout=60)
                if r2.status_code==200: open(out,"wb").write(r2.content); made+=1; print(f"✓ {fid} (after wait)")
                else: failed+=1; print(f"✗ {fid} ({r2.status_code}) — run again later")
            else:
                failed+=1; print(f"✗ {fid} (status {r.status_code})")
        except Exception as e:
            failed+=1; print(f"✗ {fid} (error: {e})")
        time.sleep(0.25)
    print(f"\nDone. New: {made}   Already had: {skipped}   Failed: {failed}")
    if not failed: print("All set — push to GitHub and they play in your voice. 🍯")

if __name__=="__main__":
    main()
