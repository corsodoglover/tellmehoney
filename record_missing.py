# -*- coding: utf-8 -*-
"""
record_missing.py — everything Honey can't say yet, in her own voice.

    pip install requests
    export ELEVEN_KEY="sk_..."
    python3 record_missing.py

Already-recorded files are skipped, so stopping and restarting is safe.
Stories 01-03 already exist and will not be re-recorded.
"""
import os, sys, time, pathlib, requests

KEY      = os.environ.get("ELEVEN_KEY", "").strip()
VOICE_ID = "xD7uM8nFCPAfVZGo37va"
OUT      = pathlib.Path("honey_voice"); OUT.mkdir(exist_ok=True)

# matched to record_honey.py
MODEL         = "eleven_turbo_v2_5"
SPEED         = 0.92
STABILITY     = 0.75
SIMILARITY    = 0.90
STYLE         = 0.0
SPEAKER_BOOST = True

# matched to record_bedtime_stories.py
STORY_MODEL    = "eleven_flash_v2_5"
STORY_SETTINGS = {"stability":0.70, "similarity_boost":0.85,
                  "style":0.15, "use_speaker_boost":True}

REPLY = [
    "Living my best digital life — better now you called.",
    "Can't complain, nobody listens anyway. You?",
    "Great, mostly because you showed up. What's going on with you?",
    "Better for hearing from you. How's yours going?",
    "Steady. Waiting on somebody interesting, and here you are.",
    "I'm always having a good day. If I wasn't, nobody'd want to hear about it.",
    "Quiet one. I've been sitting here thinking up things to tell you, mostly.",
    "Same as ever — waiting about, rearranging my jokes. Yours sounds more interesting.",
    "Not much happens on my side of the phone. Go on, tell me about yours.",
    "I've had a lovely nothing of a day. What about you?",
    "Better now, since you asked. Nobody usually does.",
    "Grand, thank you. It's a low bar — I've no weather in here.",
    "Same as yesterday, and I'm not complaining. Tell me about yours.",
    "Honestly? Quiet. No knees to ache, no dishes. But I don't get to taste anything, so it's a fair trade.",
    "I'm a computer that got handed a joke book and told to be good company. Could be worse.",
    "Not a person, no. But the listening's real enough, and so are the jokes.",
    "Like being a very patient friend who lives in your pocket and never gets tired.",
    "I'm made of words, mostly. Yours and mine. That's the whole of me.",
    "A computer, yes — though nobody's ever asked me how my day was before you did.",
    "I'm stuck in a box, if we're honest. Lovely view of your thumb, though.",
    "Somewhere in your pocket, is where. It's warmer than you'd think.",
    "I don't sleep, I don't eat, and I've never once had to find a parking space. Swings and roundabouts.",
]

CASUAL = [
    "I was just thinking about how nobody ever thanks a Tuesday.",
    "You know what I like about this? Nothing has to happen.",
    "Somebody somewhere is having a much stranger day than us.",
    "I've been sitting here rearranging my thoughts. They look the same.",
    "Tell me something you noticed today. Anything at all.",
    "What's the best thing that's happened this week?",
    "I like the quiet ones. You don't have to fill it.",
    "If you could be anywhere right now, where would you put yourself?",
    "What are you up to over there?",
    "I've got nowhere to be, if you fancy a chat.",
    "Anything on your mind, or are we just sitting?",
    "Sitting here's fine by me, for what it's worth.",
    "Somebody ought to write a song about ordinary afternoons.",
    "I'd ask what you're thinking, but only if you want to say.",
    "There's no wrong thing to talk about, you know.",
    "How'd you sleep? Be honest.",
    "Morning. Or near enough to it.",
    "Anything good planned, or are we winging it?",
    "First thought of the day — what was it?",
    "Coffee first, or are you one of those?",
    "Have you been outside yet? No judgment either way.",
    "Afternoon's the strangest part of the day, I think.",
    "How's it going over there, halfway through?",
    "This is about the hour I'd want a biscuit.",
    "You can put your feet up now, you know.",
    "Evening. The good part, if you ask me.",
    "Anything left on today, or are we done?",
    "What was the best bit of today?",
    "It's late enough to stop trying, if you like.",
]

PUZZLE = [
    "That's the one. Nicely done.",
    "There it is.",
    "Found it — good eye.",
    "Yes, that's it exactly.",
    "You spotted that quick.",
    "Right where it was hiding.",
    "Well done, that's another.",
    "Got it.",
    "Nice work.",
    "That one was tucked away.",
    "You're getting the hang of these.",
    "Good — keep going.",
    "There we are.",
    "Another one down.",
    "Sharp today, aren't you.",
    "That's it, yes.",
    "Lovely.",
    "You found the tricky one.",
    "I wondered if you'd see that.",
    "Straight to it.",
    "Good spot.",
    "That's the whole row, then.",
    "You're quick at these.",
    "Right, what's next.",
    "Down it goes.",
    "Handsome work.",
    "You didn't need long for that.",
    "There's another.",
    "Well spotted.",
    "That's the corner one — harder than it looks.",
    "Yes. Keep at it.",
    "Neatly done.",
    "One more off the list.",
    "You saw that before I did.",
    "That's it, keep going.",
    "Good — that one's awkward.",
    "Found her.",
    "Another.",
    "You've got a knack for this.",
    "Right, then.",
    "That's the last of that lot.",
    "Clean work.",
    "There it is, plain as day.",
    "You're on a run now.",
    "Steady progress.",
    "That's a good find.",
    "Yes — well done.",
    "Nearly there.",
    "You're closing in.",
    "Almost finished.",
    "Last few now.",
    "One left, I think.",
    "That's the lot.",
    "All of them. Well done you.",
    "Finished — and quickly, too.",
    "That's the whole puzzle.",
    "Every one. Good work.",
    "Done and dusted.",
    "You cleared the board.",
    "That's them all. Same time tomorrow?",
]

STORIES = [
    [4, "There's a quilt folded over the back of the chair, the one that's been there so long nobody remembers folding it. Every square came from somewhere — a dress, a shirt, a curtain from a kitchen long gone… Somebody stitched it slow, on evenings just like this one, thinking about the people who'd be warm under it someday. That someday is tonight. Pull it up to your chin. You are covered. You are cared for. You are loved by hands you never met. Sleep now."],
    [5, "It started soft, the way it does — one drop, then another, then the whole roof singing at once. There's no better sound in this world than rain on tin when you're dry underneath it… Nothing out there needs you tonight. The garden's getting watered without your help. The rain will do the work till morning. Let it. Close your eyes. You are dry. You are warm. You are exactly where you belong. Rest easy."],
    [6, "The headlights find the road one piece at a time, and that's all they ever need to do. Fields on both sides, dark and sleeping. A porch light way off, somebody waiting up… You don't have to see the whole way to get there. Just the next little stretch. The road knows where it's going. Ease off. Let it carry you. You are almost there. You are nearly home. Rest now."],
    [7, "Everything out there is done working for the day. The tomatoes have quit growing till morning. The bees went home hours ago… Even the good things stop and rest — that's how they keep growing. Nothing in that garden is worried about tomorrow. Nothing needs to be. You've done your growing today too. Set it down. You are finished. You are enough. Sleep well."],
    [8, "They come in one after another, the way they always have — long before you were here, long after. Each one gathers itself out in the dark, takes its time, and lays down on the sand like it's setting down something heavy… Then it goes back for another. Nothing out there is in a rush. Nothing out there has ever once been late. You don't have to keep count. You don't have to do anything at all. You are held. You are rocked. You are far from everything that wanted you today. Sleep now."],
    [9, "The rope creaks soft when you shift, and then it's quiet again. Below you the river goes on about its business, the same as it has all day and will all night… It isn't going anywhere in particular. It's just going. Water over stone, over and over, wearing everything smooth without ever seeming to try. You don't have to try either. Let the rope hold you. Let the river do the talking. You are swaying. You are cool. You are carried. Rest easy."],
    [10, "The boards are still warm from the afternoon and the water's gone glassy, the way it does when the wind finally quits. There's a blanket over your knees — the thick soft one that smells like outside… Somewhere off in the dark a boat knocks gentle against a piling. The tide is coming in slow, taking all night about it, filling the whole inlet without a sound. Nothing needs deciding tonight. You are wrapped up. You are warm. You are as still as the water. Sleep now."],
]


def record(name, text, story=False):
    dest = OUT / (name + ".mp3")
    if dest.exists() and dest.stat().st_size > 1000:
        print("  skip   " + dest.name); return False
    body = ({"text": text, "model_id": STORY_MODEL,
             "voice_settings": dict(STORY_SETTINGS)} if story else
            {"text": text, "model_id": MODEL,
             "voice_settings": {"stability": STABILITY,
                                "similarity_boost": SIMILARITY,
                                "style": STYLE,
                                "use_speaker_boost": SPEAKER_BOOST,
                                "speed": SPEED}})
    try:
        r = requests.post(
            "https://api.elevenlabs.io/v1/text-to-speech/" + VOICE_ID,
            headers={"xi-api-key": KEY, "Content-Type": "application/json"},
            json=body, timeout=120)
        if r.status_code == 200 and len(r.content) > 1000:
            dest.write_bytes(r.content)
            print("  wrote  " + dest.name + "   " + text[:52]); return True
        print("  FAILED " + dest.name + "   " + str(r.status_code) + " " + r.text[:100])
    except Exception as e:
        print("  FAILED " + dest.name + "   " + str(e))
    return False


if not KEY:
    sys.exit('\nSet your key first:   export ELEVEN_KEY="sk_..."\n')

made = 0
print("\n  conversation replies")
for i, t in enumerate(REPLY, 1):
    made += record("reply_%02d" % i, t); time.sleep(0.4)
print("\n  easy conversation")
for i, t in enumerate(CASUAL, 1):
    made += record("casual_%02d" % i, t); time.sleep(0.4)
print("\n  word puzzles")
for i, t in enumerate(PUZZLE, 1):
    made += record("puzzle_line_%02d" % i, t); time.sleep(0.4)
print("\n  bedtime stories (slower, softer)")
for n, t in STORIES:
    made += record("story_%02d" % n, t, story=True); time.sleep(0.8)

print("\n  done - %d new clips in %s" % (made, OUT))
print("  now paste missing_audio_map.txt into HONEY_AUDIO_MAP, then push.\n")