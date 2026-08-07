#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────────────────────
#  record_stories_slow.py
#
#  All seven bedtime stories, slower and with more silence written into them.
#
#  WHAT THE FIRST THREE GOT RIGHT, AND HOW
#  The original three — Porch, Little Boat, House Settling — were recorded with
#  NO speed setting at all. Default 1.0. They sound unhurried because of the
#  writing: ellipses everywhere, short sentences, room between thoughts.
#
#  Do the arithmetic and it is stark:
#      story_01   1,450 characters over 120 seconds   12.0 chars/second
#      story_05   1,225 characters over  84 seconds   14.6 chars/second
#
#  So the rewrites were running FASTER than the originals despite being cut at
#  0.78, because the text had length but not enough silence. Speed alone was
#  never going to fix it.
#
#  THIS PASS DOES BOTH
#      speed      0.72   slower again
#      stability  0.88   steadier — the model reads rather than performs
#      style      0.06   performance pulled right back
#      and pauses written into the text itself, the way the good three have them
#
#  Stories 01, 02 and 03 are never touched.
#
#  RUN IT, from the tellmehoney folder:
#     export ELEVEN_KEY="sk_your_key_here"
#     python3 record_stories_slow.py
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
    "stability": 0.88, "similarity_boost": 0.85,
    "style": 0.06, "use_speaker_boost": True, "speed": 0.72,
}

STORIES = {
"story_04": (
 "There's a quilt folded over the back of the chair, the one that's been there so long nobody remembers folding it. Every square came from somewhere \u2014 a dress, a shirt, a curtain from a kitchen long gone. That blue one was somebody's Sunday best, worn soft at the elbows before it ever got cut up. The little yellow one with the flowers was an apron, and before that it was a bolt of cloth on a shelf in a store that isn't there any more\u2026 Run your hand across it. \u2026 You can feel where the stitches go small and careful, and where they go long and quick, and that's somebody getting tired near the end of an evening. Somebody stitched it slow, on evenings just like this one, with the lamp on and the radio low, thinking about the people who'd be warm under it someday. She didn't know your name. \u2026 She didn't know your face. She just knew there'd be somebody, some winter, needing to be warm\u2026 That someday is tonight. The quilt is heavier than you'd think. \u2026 That's all those years in it. Pull it up to your chin. Let it press you down into the bed the way a hand rests on a shoulder. \u2026 There is nothing left to do tonight. Nothing at all. Breathe in slow. \u2026 Breathe out slower. You are covered\u2026 You are cared for\u2026 You are loved by hands you never met\u2026 \u2026  Sleep now."
),

"story_05": (
 "It started soft, the way it does \u2014 one drop, then another, then the whole roof singing at once. There's no better sound in this world than rain on tin when you're dry underneath it. It doesn't come down even. It comes in waves, gathering up and letting go, loud for a while and then easing off to almost nothing\u2026 and then here it comes again. \u2026 The gutter runs full and steady, a low note under all the rest. Somewhere off the corner of the porch there's a drip landing in a bucket somebody left out, slow and regular. Plink\u2026 plink\u2026 like a clock that doesn't mind what time it is. \u2026 The air coming through the window is cool and clean and smells like the whole world got washed. Nothing out there needs you tonight. The garden's getting watered without your help. \u2026 The road's getting rinsed. The dust is being put back where it came from. The rain will do the work till morning\u2026 Let it. \u2026 You don't have to listen for anything in it. There's nothing in it to listen for. It's only water, doing what it's always done, on a roof that's held up under it a thousand nights before this one. \u2026 Close your eyes. Let the sound come over you in waves the way it wants to. You are dry\u2026 You are warm\u2026 You are exactly where you belong\u2026 \u2026  Rest easy. \u2026"
),

"story_06": (
 "The headlights find the road one piece at a time, and that's all they ever need to do. Fifty feet of white line, then fifty more. The dark closes up behind you and opens up ahead, and the car goes on through the middle of it, steady. Fields on both sides, dark and sleeping. \u2026 A fence post, a fence post, a mailbox\u2026 and then fields again. Somewhere out there the corn is standing quiet in rows nobody can see. The tires make that long soft sound on the blacktop, the one that never changes. \u2026 A porch light way off, somebody waiting up. It sits out there in the dark for the longest time, not getting closer, and then all at once it's beside you and gone\u2026 and then it's just dark again, and that's alright too. You don't have to see the whole way to get there. \u2026 Just the next little stretch. Just the piece the lights can reach. The road knows where it's going. \u2026 It's been going there since long before tonight. Your hands can loosen on the wheel now. Your shoulders can come down. \u2026 Ease off. Let it carry you. There's a light on at the end of this. \u2026 There always was. You are almost there. You are nearly home. \u2026 \u2026  Rest now."
),

"story_07": (
 "Everything out there is done working for the day. The tomatoes have quit growing till morning. The bees went home hours ago, every one of them, back down into the dark of the hive to wait it out. The beans have stopped climbing. \u2026 The squash has stopped spreading. Even the weeds have knocked off\u2026 The ground is letting go of the day's heat, slow, giving it back to the air. You can feel it if you stand out there \u2014 warm at your ankles, cool at your face. \u2026 A moth goes by on its way to somewhere. Something small moves in the mulch and then thinks better of it. The sprinkler's been off for an hour and the leaves are still holding water, one bright drop at the end of each one, waiting for morning to take it. \u2026 Even the good things stop and rest \u2014 that's how they keep growing. Nothing in that garden is worried about tomorrow. Nothing needs to be. \u2026 Nothing out there is behind. Nothing out there has a list\u2026 You've done your growing today too. More than you'd give yourself credit for. \u2026 Set it down. Set all of it down, right there between the rows, and let the dark keep it till morning. You are finished. \u2026 You are enough. \u2026  Sleep well."
),

"story_08": (
 "They come in one after another, the way they always have \u2014 long before you were here, long after. Each one gathers itself out in the dark, takes its time, and lays down on the sand like it's setting down something heavy. Then it goes back for another\u2026 You can hear it coming before you hear it arrive. A long gathering hush out where you can't see, and then the break, and then the whole thing sliding up the sand and thinning out and stopping, and going quiet before it slips away again. \u2026 Then nothing for a moment. Just the wind, and the sand, and the dark\u2026 And then here comes the next one. It has been doing this all day, while you were busy. \u2026 It was doing this last night while you slept. It'll be doing it tomorrow whether anybody's watching or not. Nothing out there is in a rush. \u2026 Nothing out there has ever once been late. You don't have to keep count. You don't have to do anything at all. \u2026 Let your breathing find the same time as the water. In on the gathering. Out on the letting go. \u2026 In\u2026 and out. You are held\u2026 You are rocked\u2026 You are far from everything that wanted you today\u2026 \u2026  Sleep now."
),

"story_09": (
 "The rope creaks soft when you shift, and then it's quiet again. The whole hammock swings a little, the way it does, side to side and slower each time, till it forgets it was swinging at all. Below you the river goes on about its business, the same as it has all day and will all night. It isn't going anywhere in particular. \u2026 It's just going\u2026 Water over stone, over and over, wearing everything smooth without ever seeming to try. There's a place near the bank where it runs over a shelf of rock and talks a little louder, and if you listen long enough it stops being water and starts sounding like people, far off, having a good conversation you're not part of and don't need to be. The leaves overhead move without any wind you can feel. \u2026 Something drops from a branch into the water and the river takes it and doesn't mention it again\u2026 You don't have to try either. Not tonight. Not one more thing. \u2026 Let the rope hold you. It's held heavier than you and never once complained. Let the river do the talking. \u2026 You are swaying\u2026 You are cool\u2026 You are carried\u2026 \u2026  Rest easy."
),

"story_10": (
 "The boards are still warm from the afternoon and the water's gone glassy, the way it does when the wind finally quits. There's a blanket over your knees \u2014 the thick soft one that smells like outside. Down at the end of the dock the light is doing that thing it does, laying itself out flat across the whole inlet in one long unbroken line\u2026 Somewhere off in the dark a boat knocks gentle against a piling. Knock\u2026 and quiet\u2026 and knock. \u2026 The rope holding it creaks once and settles. A fish turns over out past the end of the dock and the rings go out from it, wider and wider, until the water forgets it happened. The tide is coming in slow, taking all night about it, filling the whole inlet without a sound. \u2026 It doesn't hurry and it doesn't stop, and by morning everything will be a little higher and nobody will have watched it happen\u2026 Nothing needs deciding tonight. Not one thing on that list needs deciding tonight. The dock will keep holding you up. \u2026 It's good at that. Pull the blanket a little higher. You are wrapped up\u2026 You are warm\u2026 You are as still as the water\u2026 \u2026  Sleep now. \u2026"
),
}


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

    print("\nRe-recording all seven at 0.72 with pauses written in.")
    print("Stories 01, 02 and 03 are untouched.")
    if input("\nGo ahead? (y/n) ").strip().lower() != "y":
        print("Stopped. Nothing changed.")
        return

    url = "https://api.elevenlabs.io/v1/text-to-speech/" + VOICE_ID
    headers = {"xi-api-key": API_KEY, "Content-Type": "application/json"}
    made = failed = 0

    for name in sorted(STORIES):
        out = ROOT_DIR / (name + ".m4a")
        try:
            print("\n  " + name + " — recording…")
            r = requests.post(url, headers=headers,
                              json={"text": STORIES[name], "model_id": MODEL,
                                    "voice_settings": SETTINGS}, timeout=240)
            if r.status_code != 200 or len(r.content) < 1000:
                print("     x error " + str(r.status_code) + ": " + r.text[:140])
                failed += 1; continue
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
                tf.write(r.content); tmp = pathlib.Path(tf.name)
            ok = to_m4a(tmp, out)
            try: tmp.unlink()
            except Exception: pass
            if not ok:
                print("     x conversion to .m4a failed"); failed += 1; continue
            try:
                (WWW_DIR / out.name).write_bytes(out.read_bytes())
            except Exception as e:
                print("     ! root only, not www/: " + str(e))
            info = subprocess.run(["afinfo", str(out)], capture_output=True, text=True).stdout
            secs = ""
            for ln in info.splitlines():
                if "estimated duration" in ln.lower():
                    secs = ln.split(":")[1].strip().split()[0]
            if secs:
                cps = round(len(STORIES[name]) / float(secs), 1)
                print("     ok  " + str(round(float(secs))) + " seconds   "
                      + str(cps) + " chars/sec   (story_01 is 12.0)")
            made += 1
        except Exception as e:
            print("     x " + str(e)); failed += 1
        time.sleep(1.0)

    print("\nRe-recorded " + str(made) + ", failed " + str(failed) + ".")
    if made:
        print("\nThe chars/sec figure above is the one that matters. Anything near")
        print("12.0 is in the same country as the three that already work.")
        print("\n   afplay honey_voice/story_04.m4a")
        print("   afplay honey_voice/story_02.m4a      (one of the good originals)")


if __name__ == "__main__":
    main()
