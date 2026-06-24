#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  record_bedtime_stories.py
#
#  Records the three sample bedtime/comfort stories in Honey's (Sally's) cloned
#  voice, saving them as story_01.mp3, story_02.mp3, story_03.mp3 into your
#  honey_voice/ folder — right where the app expects them.
#
#  These are LONGER than the facts (a couple minutes each), so they use more
#  ElevenLabs credit per clip. Three samples first; record more once you see
#  which ones users engage with.
#
#  HOW TO RUN (Terminal, from your tellmehoney folder):
#     1.  pip install requests          (first time only)
#     2.  export ELEVEN_KEY="sk_your_key_here"
#     3.  python3 record_bedtime_stories.py
#
#  Already-recorded files are skipped, so re-running is safe.
# ─────────────────────────────────────────────────────────────────────────────

import os, sys, time, pathlib, requests

VOICE_ID = "xD7uM8nFCPAfVZGo37va"
MODEL    = "eleven_flash_v2_5"
OUT_DIR  = pathlib.Path("honey_voice")
API_KEY  = os.environ.get("ELEVEN_KEY", "").strip()

# Softer, slower settings suit a bedtime read (lower style = calmer delivery).
VOICE_SETTINGS = {"stability":0.70, "similarity_boost":0.85, "style":0.15, "use_speaker_boost":True}

# Full story text (slow, soothing). Ellipses (…) help ElevenLabs pause gently.
STORIES = [
    # story_01 — The Porch at the End of the Day
    ("The sun is going down slow tonight, the way it does in summer when it's in no hurry at all. "
     "Out on the porch, the boards are still warm from the afternoon. A glass of sweet tea sits sweating on the rail, the ice gone soft. "
     "Somewhere down the road a screen door taps shut, gentle, and then everything is quiet again. "
     "The crickets start up, one at a time… first just one, then another answering, and another, until the whole yard is humming low and easy, like the earth itself is breathing. "
     "A lightning bug blinks on near the steps. Then another, out over the grass. They drift up slow… here and gone… here and gone… little lanterns carried by nobody. "
     "The rocking chair creaks soft, back and forth, back and forth. There's nothing that needs doing now. The dishes are done. The day is done. "
     "The list that felt so long this morning has gone quiet, same as the road. "
     "A warm breeze comes through and stirs the chimes by the door… two notes, soft… and then still. "
     "The sky goes from gold to rose to a deep soft blue, and the first star shows up, patient, like it's been waiting all day for its turn. "
     "You don't have to hold anything now. Not the worries. Not the hurry. Let them set down on the porch boards beside you, and rest there till morning. "
     "Breathe in the cool of the evening. Breathe out the long day. "
     "You did enough today. You are enough tonight. "
     "Rest easy now. The porch will hold you. The night will keep you. And morning will come gentle, when it's time."),

    # story_02 — The Little Boat That Drifted Home
    ("Far out on a calm dark sea, under a sky full of soft stars, there is a little wooden boat. "
     "It isn't going anywhere in a hurry. It doesn't need to. The water is smooth as a held breath, and the boat just drifts, slow and easy, rocking the gentlest rock there ever was. "
     "The moon lays a long silver path across the water, and the little boat floats right down the middle of it, glowing pale in the quiet light. "
     "Tiny waves lap at the sides… lap… lap… lap… soft as a lullaby, soft as a heartbeat. The sail is down. The rope is coiled. There is nothing to steer, and nowhere to be. "
     "A single seabird drifts overhead, wings spread wide, not even flapping, just gliding home on the warm night air. It calls once, far away and gentle, and then it's gone into the dark. "
     "The stars come out thicker now, more and more of them, until the whole sky is dusted silver. One of them slips loose and falls, slow and bright, and the little boat rocks on. "
     "The water holds the boat the way a hand holds something precious. Easy. Sure. "
     "You are in the little boat now. Lying back against the smooth warm wood, looking up at all those patient stars. You don't have to row. You don't have to watch the sky. The sea knows the way. "
     "It's carrying you home, slow and safe, down the silver path, under the gentle moon. "
     "Let your hands go loose. Let your shoulders go soft. Let the rocking carry you. "
     "Lap… lap… lap… "
     "Drift now. You are held. You are carried. You are almost home."),

    # story_03 — The House Settling In for the Night
    ("The house is getting quiet now. "
     "In the kitchen, the last warm light is off. The faucet drips once, slow… and then is still. The refrigerator hums its low steady hum, the sound it's made every night for years, faithful and easy. "
     "Down the hall, the heat ticks on soft in the walls, warming the rooms while everyone sleeps. Tick… tick… The house knows how to take care of itself at night. It's done it so many times. "
     "The clock on the wall keeps its slow soft time. Not rushing. Just keeping the minutes safe, one after another, while you rest. "
     "Outside the window, the wind moves through the branches, a long soft hush, like the whole street is exhaling. A car passes far away and its light slides across the ceiling, slow… and then it's gone, and the dark comes back, soft and complete. "
     "The blankets are warm. The pillow is just right. Your body is heavy in the good way now, sinking down, held by the bed the way the bed has held you every single night of your life. "
     "There is nothing left to do tonight. The doors are locked. The lights are out. Everyone you love is resting somewhere under the same wide dark sky. "
     "You can let go of today. All of it. The hard parts, and the small good parts. Set them down. They'll keep till morning. "
     "The house hums and ticks and settles, taking care of the night, so you don't have to. "
     "Breathe in soft. Breathe out slow. "
     "You are home. You are safe. You are warm. "
     "Rest now. The morning will be there when you wake, gentle and new. But that's a long way off. For now… just rest."),
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
    for i, text in enumerate(STORIES, start=1):
        name = f"story_{i:02d}.mp3"
        path = OUT_DIR / name
        if path.exists() and path.stat().st_size > 1000:
            print(f"  {name}  — already there, skipping"); skipped += 1; continue
        body = {"text": text, "model_id": MODEL, "voice_settings": VOICE_SETTINGS}
        try:
            print(f"  recording {name} … (this one's longer, give it a moment)")
            r = requests.post(url, headers=headers, json=body, timeout=120)
            if r.status_code == 200 and len(r.content) > 1000:
                path.write_bytes(r.content); print(f"  {name}  ✓"); made += 1
            else:
                print(f"  {name}  ✗ error {r.status_code}: {r.text[:120]}"); failed += 1
        except Exception as e:
            print(f"  {name}  ✗ {e}"); failed += 1
        time.sleep(0.6)
    print(f"\nDone. recorded {made}, skipped {skipped}, failed {failed}.")
    print("Push with:  git add -A && git commit -m 'bedtime story clips' && git push")

if __name__ == "__main__":
    main()
