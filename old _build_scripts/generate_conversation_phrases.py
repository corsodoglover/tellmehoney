#!/usr/bin/env python3
"""
generate_conversation_phrases.py
Records Honey's new conversational phrases via ElevenLabs at speed 0.85,
saving MP3s into honey_voice/ with the matching filenames.

USAGE:
  1. pip install requests
  2. Set your key + voice id below (or as env vars)
  3. python3 generate_conversation_phrases.py

NOTE: speed 0.85 is applied via the "speed" voice setting. Your existing library
was 0.92; these gentle conversational lines get 0.85 (a touch slower/warmer).
"""

import os, requests, time

# ---- CONFIG (fill these in) ----
EL_KEY   = os.environ.get("ELEVENLABS_KEY","sk_41729f7251a9150917ea07cbf971fc5581a43c65a1b774c1")
VOICE_ID = os.environ.get("HONEY_VOICE_ID", "xD7uM8nFCPAfVZGo37va")
OUT_DIR  = "honey_voice"
MODEL    = "eleven_multilingual_v2"   # or your usual model
SPEED    = 0.78                        # <-- the slower, warmer speed you wanted

# ---- THE LINES (filename : text) ----
LINES = {
    # 1. Greetings
    "conv_greet_01": "Hey, you made it. Good to see you.",
    "conv_greet_02": "There you are. I was wondering when you'd show up.",
    "conv_greet_03": "Well, look who it is.",
    "conv_greet_04": "Hey you. How's it going?",
    "conv_greet_05": "Back again, huh? I like that.",
    "conv_greet_06": "Hey! Glad you're here.",
    # 2. Check-ins
    "conv_check_01": "So how are you, really? Not the quick answer -- the real one.",
    "conv_check_02": "How's your day treating you?",
    "conv_check_03": "Straight up -- you doing okay today?",
    "conv_check_04": "What's on your plate today?",
    "conv_check_05": "Good day, rough day, or somewhere in between?",
    "conv_check_06": "How you holding up?",
    # 3. What's going on
    "conv_whats_01": "What's going on in your world?",
    "conv_whats_02": "Talk to me -- what's on your mind?",
    "conv_whats_03": "Anything good happening lately?",
    "conv_whats_04": "What've you been up to?",
    "conv_whats_05": "Catch me up -- what's new with you?",
    "conv_whats_06": "What's the story today?",
    # 4. Follow-ups
    "conv_follow_01": "Tell me more about that.",
    "conv_follow_02": "Oh, keep going -- I'm listening.",
    "conv_follow_03": "And how'd that sit with you?",
    "conv_follow_04": "I want to hear the rest.",
    "conv_follow_05": "That's a lot. What happened next?",
    "conv_follow_06": "Go on, I'm right here.",
    # 5. Encouragement
    "conv_encour_01": "You're doing better than you think you are.",
    "conv_encour_02": "Look at you, still showing up. That counts.",
    "conv_encour_03": "You've got more in the tank than you give yourself credit for.",
    "conv_encour_04": "Whatever today throws at you, I'd bet on you.",
    "conv_encour_05": "One thing at a time. You've got this.",
    "conv_encour_06": "Go get it. I'm in your corner.",
    # 6. Comfort
    "conv_comfort_01": "Oof. I'm sorry you're dealing with that.",
    "conv_comfort_02": "You don't have to have it all figured out right now.",
    "conv_comfort_03": "It's okay to not be okay today. I'm still here.",
    "conv_comfort_04": "Rough one, huh? Let's take it slow for a sec.",
    "conv_comfort_05": "That's heavy. You don't have to carry it by yourself.",
    "conv_comfort_06": "Take a breath with me. In... and out. There you go.",
    # 7. Warm everyday
    "conv_warm_01": "Hope your day's going alright so far.",
    "conv_warm_02": "You popped into my head today -- figured I'd say hey.",
    "conv_warm_03": "I like when you check in.",
    "conv_warm_04": "However today's going, glad we got this minute.",
    "conv_warm_05": "Whatever you need -- a laugh, an ear, or just some quiet -- I've got you.",
    "conv_warm_06": "Good to have you around.",
    # 8. Fun / a little sass
    "conv_fun_01": "Alright, what kind of trouble are we getting into today?",
    "conv_fun_02": "Tell me something good. Or something ridiculous. I'll take either.",
    "conv_fun_03": "You look like you've got a story. Let's hear it.",
    "conv_fun_04": "Big day ahead, or are we taking it easy?",
    "conv_fun_05": "Okay, hit me -- what's the vibe today?",
    # 9. Joke transitions
    "conv_joketrans_01": "Want me to lighten things up?",
    "conv_joketrans_02": "I could make you laugh, if you're up for it.",
    "conv_joketrans_03": "Say the word and I'll bring the funny.",
}

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    if "PASTE_YOUR" in EL_KEY or "PASTE_YOUR" in VOICE_ID:
        print("⚠️  Set EL_KEY and VOICE_ID first (edit the file or set env vars).")
        return
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": EL_KEY, "Content-Type": "application/json"}
    total = len(LINES); done = 0
    for fname, text in LINES.items():
        out = os.path.join(OUT_DIR, fname + ".mp3")
        if os.path.exists(out):
            print(f"skip (exists): {fname}"); done += 1; continue
        payload = {
            "text": text,
            "model_id": MODEL,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "speed": SPEED           # <-- 0.85
            }
        }
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=60)
            if r.status_code == 200:
                with open(out, "wb") as f: f.write(r.content)
                done += 1
                print(f"[{done}/{total}] saved {fname}.mp3")
            else:
                print(f"‼️  {fname}: {r.status_code} {r.text[:120]}")
        except Exception as e:
            print(f"‼️  {fname}: {e}")
        time.sleep(0.4)  # be gentle on the API
    print(f"\nDone. {done}/{total} files in {OUT_DIR}/ at speed {SPEED}.")

if __name__ == "__main__":
    main()
