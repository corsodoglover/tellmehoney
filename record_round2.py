import os, sys, time, pathlib, requests

KEY      = os.environ.get("ELEVEN_KEY", "").strip()
VOICE_ID = "xD7uM8nFCPAfVZGo37va"
OUT      = pathlib.Path("honey_voice"); OUT.mkdir(exist_ok=True)

MODEL         = "eleven_turbo_v2_5"
SPEED         = 0.92
STABILITY     = 0.75
SIMILARITY    = 0.90
STYLE         = 0.0
SPEAKER_BOOST = True

LINES = [
    "Hey. That's real, and I'm not going anywhere. Want to just talk, or want me to make you laugh out of it?",
    "I hear you. No fixing, no rushing. I'm right here. Say the word and I'll lighten it.",
    "That sounds heavy. You don't have to carry the funny right now — I'll hold it til you're ready.",
    "Oh really? Tell me more about that.",
    "Now that sounds like something we could get into.",
    "Go on — I want to hear the rest.",
    "Mm. What happened next?",
    "That's interesting. What made you think of it?",
    "I'm listening. Keep going.",
    "And how did that sit with you?",
    "Say more about that, would you?",
    "Well now. What else?",
    "I'd like to hear more of that.",
    "What's the story behind it?",
    "Hm. Tell me the rest.",
    "You've got my attention. Go on.",
    "And then what?",
    "What made today the day for that?",
    "That's worth talking about. What else is on it?",
    "Mm-hmm. And how do you feel about it?",
    "Keep going, I'm right here.",
]

def record(name, text):
    dest = OUT / (name + ".mp3")
    if dest.exists() and dest.stat().st_size > 1000:
        print("  skip   " + dest.name); return False
    try:
        r = requests.post(
            "https://api.elevenlabs.io/v1/text-to-speech/" + VOICE_ID,
            headers={"xi-api-key": KEY, "Content-Type": "application/json"},
            json={"text": text, "model_id": MODEL,
                  "voice_settings": {"stability": STABILITY,
                                     "similarity_boost": SIMILARITY,
                                     "style": STYLE,
                                     "use_speaker_boost": SPEAKER_BOOST,
                                     "speed": SPEED}},
            timeout=120)
        if r.status_code == 200 and len(r.content) > 1000:
            dest.write_bytes(r.content)
            print("  wrote  " + dest.name + "   " + text[:52]); return True
        print("  FAILED " + dest.name + "   " + str(r.status_code) + " " + r.text[:100])
    except Exception as e:
        print("  FAILED " + dest.name + "   " + str(e))
    return False

if not KEY:
    sys.exit("\nSet your key first:   export ELEVEN_KEY=\"sk_...\"\n")

made = 0
for i, t in enumerate(LINES, 1):
    made += record("catch_%02d" % i, t); time.sleep(0.4)
print("\n  done - %d new clips in %s\n" % (made, OUT))
