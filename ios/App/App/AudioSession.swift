import Foundation
import Capacitor
import AVFoundation

// ══════════ WHY THIS EXISTS ══════════════════════════════════════════════════
//
// Setting the audio session in AppDelegate is correct, and it is not enough.
// @capacitor-community/speech-recognition sets its OWN category every time
// start() is called — record mode, without .defaultToSpeaker. So the launch
// setting holds until the first time the microphone runs and is then replaced.
//
// Which is exactly the symptom: Honey speaks once at full volume, the mic runs,
// and from then on she comes out of the earpiece. The free phone voice escapes
// it because speechSynthesis is managed by iOS itself and does not go through
// the same session.
//
// A setting made once cannot win against something that resets it on every
// turn. So this exposes one method the app can call whenever it needs the
// session put back — after the recogniser stops, and before a clip plays.
//
// Nothing here is clever. It just says the thing again, at the moment it
// stopped being true.
//
@objc(AudioSessionPlugin)
public class AudioSessionPlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "AudioSessionPlugin"
    public let jsName = "AudioSession"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "toSpeaker", returnType: CAPPluginReturnPromise)
    ]

    @objc func toSpeaker(_ call: CAPPluginCall) {
        DispatchQueue.main.async {
            let session = AVAudioSession.sharedInstance()
            do {
                // ── .voiceChat, not .spokenAudio ─────────────────────────────
                // .spokenAudio is a playback mode on a session that has to
                // record at the same time. .voiceChat is built for exactly
                // this, routes to the loudspeaker, and — the part that matters
                // most — turns on the voice-processing unit, which is hardware
                // echo cancellation. That is what stops the microphone hearing
                // Honey through the speaker and transcribing her back at you.
                // No amount of JavaScript can do that; once her voice is out of
                // the speaker it is a real sound in a real room.
                //
                // ── .mixWithOthers removed ───────────────────────────────────
                // It is polite about other people's music, and it competes with
                // the routing we are trying to force. Politeness was costing us
                // the loudspeaker.
                try session.setCategory(
                    .playAndRecord,
                    mode: .voiceChat,
                    options: [.defaultToSpeaker, .allowBluetoothHFP]
                )
                try session.setActive(true, options: [])

                // ── Only override when it is actually wrong ──────────────────
                // Forcing .speaker unconditionally would drag the sound out of
                // headphones and car speakers and onto the phone — which is
                // worse than the bug it fixes, and hands-free in the car is
                // half the point of the feature. So: only when the output has
                // genuinely fallen back to the earpiece.
                let onReceiver = session.currentRoute.outputs.contains {
                    $0.portType == .builtInReceiver
                }
                if onReceiver {
                    try session.overrideOutputAudioPort(.speaker)
                }

                call.resolve(["ok": true, "forced": onReceiver])
            } catch {
                call.resolve(["ok": false, "error": error.localizedDescription])
            }
        }
    }
}
