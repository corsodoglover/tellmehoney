#!/usr/bin/env python3
"""
Tell Me Honey - WEATHER REACTION generator
Records the new greeting + calendar/list/call lines in your ElevenLabs voice.
The app already knows these filenames. Saves straight into honey_voice.

HOW TO RUN (Mac):
  1) Put this file in your tellmehoney folder (next to honey_voice).
  2) Terminal:  cd ~/Desktop/tellmehoney
  3) First time only:  pip3 install requests
  4) Run:  python3 generate_weather_lines.py
  5) Paste your ElevenLabs API key when asked (stays private).
Already-made files are skipped, so re-running never double-charges.
"""
import os, sys, time, getpass

VOICE_ID = "xD7uM8nFCPAfVZGo37va"
MODEL_ID = "eleven_flash_v2_5"
OUTPUT_DIR = "honey_voice"

LINES = {
    'wx_oh_its_just_beautiful_out_there_today': "Oh, it's just beautiful out there today.",
    'wx_gorgeous_out_dont_let_me_keep_you_darlin_unless_you_': "Gorgeous out. Don't let me keep you, darlin' — unless you want one more joke.",
    'wx_its_fabulous_outside_go_soak_up_a_little_of_it_for_m': "It's fabulous outside. Go soak up a little of it for me.",
    'wx_what_a_lovely_day_the_kind_thats_good_for_the_soul': "What a lovely day. The kind that's good for the soul.",
    'wx_whew_its_a_hot_one_stay_cool_out_there': "Whew, it's a hot one. Stay cool out there.",
    'wx_hot_as_blazes_today_drink_your_water_please': 'Hot as blazes today. Drink your water, please.',
    'wx_brr_bundle_up_out_there_today': 'Brr, bundle up out there today.',
    'wx_its_cold_darlin_coat_and_a_hot_drink_doctors_orders': "It's cold, darlin'. Coat and a hot drink, doctor's orders.",
    'wx_grab_an_umbrella_or_just_stay_in_and_let_me_entertai': 'Grab an umbrella — or just stay in and let me entertain you.',
    'wx_rainy_one_today_perfect_excuse_to_sit_a_while_with_m': 'Rainy one today. Perfect excuse to sit a while with me.',
    'wx_snow_day_energy_hot_drink_and_a_few_jokes': 'Snow day energy. Hot drink and a few jokes?',
    'wx_its_snowin_out_there_cozy_up_ill_keep_you_company': "It's snowin' out there. Cozy up, I'll keep you company.",
    'wx_maybe_save_the_porch_sittin_for_another_night_its_wi': "Maybe save the porch sittin' for another night — it's wild out there.",
    'wx_storms_rolling_through_stay_safe_and_stay_in_please': "Storm's rolling through. Stay safe and stay in, please.",
    'wx_bit_gray_out_today_good_thing_im_sunny_enough_for_bo': "Bit gray out today. Good thing I'm sunny enough for both of us.",
    'wx_foggy_one_take_it_slow_out_there_darlin': "Foggy one. Take it slow out there, darlin'."
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
