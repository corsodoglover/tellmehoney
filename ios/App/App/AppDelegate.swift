import UIKit
import Capacitor
import AVFoundation

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?

    // ══════════ SETTING IT ONCE WAS NOT ENOUGH ══════════════════════════════
    // The old version configured the audio session at launch and again on
    // becomeActive, and assumed it would hold. It does not. The speech
    // recogniser sets its OWN session when it starts listening, and what it
    // leaves behind is a record-oriented route pointed at the earpiece.
    //
    // That is exactly the symptom: Honey and the premium voices play faint,
    // out of the receiver instead of the loudspeaker, and only manage one
    // hands-free turn before the microphone dies. The free phone voice is
    // untouched because speechSynthesis is managed by iOS itself and never
    // competes for the session at all.
    //
    // So the session has to be re-asserted, not just set — after every route
    // change and every interruption, which is precisely when the recogniser
    // has been meddling.
    // Re-entrancy guard. setCategory, setActive and overrideOutputAudioPort
    // each CAUSE a route change — so configuring the session from inside a
    // route-change handler makes it call itself, forever, on the main thread.
    // That is a spinning app that will not take a button press, and a
    // microphone that can never open because the session is yanked out from
    // under the recogniser the instant it sets one up.
    private static var isConfiguring = false

    static func configureAudioSession(activate: Bool = true) {
        if isConfiguring { return }
        isConfiguring = true
        defer { isConfiguring = false }

        let session = AVAudioSession.sharedInstance()
        do {
            // .voiceChat is the change that matters.
            //
            //   • It turns on the voice-processing I/O unit, which is hardware
            //     ECHO CANCELLATION. That is the real fix for the microphone
            //     hearing Honey through the loudspeaker and transcribing her
            //     back at you — a thing no amount of JavaScript timing can do,
            //     because by the time the sound has left the speaker it is a
            //     real sound in a real room.
            //
            //   • It is designed for simultaneous record and playback, which is
            //     what hands-free actually is.
            //
            //   • It routes to the loudspeaker rather than the receiver, which
            //     is the "faint, in the earpiece" problem.
            //
            // .spokenAudio was the wrong tool: a playback mode, on a session
            // that has to record at the same time.
            //
            // .mixWithOthers is gone. It is polite about other people's music,
            // but it competes with the routing we are trying to force, and a
            // companion app that is talking to you should be the thing you
            // hear. Politeness was costing us the speaker.
            try session.setCategory(
                .playAndRecord,
                mode: .voiceChat,
                options: [.defaultToSpeaker, .allowBluetoothHFP]
            )
            // Only claim the session on the way in. Re-activating it later
            // interrupts whatever is already using it — which, during
            // hands-free, is the speech recogniser.
            if activate { try session.setActive(true, options: []) }

            // Belt and braces. .defaultToSpeaker is a default, and a default is
            // something the recogniser can quietly overrule. This says it
            // outright. Only when nothing better is plugged in — headphones and
            // car speakers still win, which is the whole point of hands-free.
            if session.currentRoute.outputs.allSatisfy({ $0.portType == .builtInReceiver }) {
                try? session.overrideOutputAudioPort(.speaker)
            }
        } catch {
            // A session that will not configure is not worth crashing over.
            // The app still works; hands-free may not.
            NSLog("TellMeHoney: audio session setup failed — \(error.localizedDescription)")
        }
    }

    // Nudge the output back to the loudspeaker — and ONLY that. No category
    // change, no setActive, nothing that interrupts whoever holds the session.
    // Deliberately does nothing when headphones or a car speaker are connected:
    // hands-free in the car is the whole point, and forcing the phone's own
    // speaker there would be worse than the bug.
    static func forceSpeakerIfOnReceiver() {
        let session = AVAudioSession.sharedInstance()
        let onReceiver = session.currentRoute.outputs.contains { $0.portType == .builtInReceiver }
        guard onReceiver else { return }
        try? session.overrideOutputAudioPort(.speaker)
    }

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {

        AppDelegate.configureAudioSession()

        // The recogniser changes the route out from under us every time it
        // opens. Listen for that and put it back, rather than finding out the
        // hard way one turn later.
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleRouteChange(_:)),
            name: AVAudioSession.routeChangeNotification,
            object: nil
        )

        // A phone call, a timer, Siri — anything that takes the session hands
        // it back in whatever state it likes. Reclaim it properly.
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleInterruption(_:)),
            name: AVAudioSession.interruptionNotification,
            object: nil
        )

        return true
    }

    @objc func handleRouteChange(_ notification: Notification) {
        guard
            let info = notification.userInfo,
            let raw = info[AVAudioSessionRouteChangeReasonKey] as? UInt,
            let reason = AVAudioSession.RouteChangeReason(rawValue: raw)
        else { return }

        // ══════════ PUT THE ROUTE BACK, NOTHING ELSE ════════════════════════
        // The recogniser sets its own session when it opens, and that session
        // points at the receiver. When it stops, nobody puts the route back —
        // so Honey plays into a record-shaped route: faint, in the earpiece,
        // and holding a session the next mic open cannot take. One turn, then
        // dead. Every time.
        //
        // The trick is to fix ONLY the route, and only when it is actually
        // wrong. overrideOutputAudioPort does not touch the category and does
        // not interrupt the recogniser. It does fire another route change —
        // but by then the output IS the speaker, so the condition below is
        // false and it stops. It cannot loop, because acting on it removes the
        // reason to act.
        //
        // A short delay lets the recogniser finish settling first. Grabbing
        // the route out from under it mid-start is what broke it last time.
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
            AppDelegate.forceSpeakerIfOnReceiver()
        }

        switch reason {
        case .oldDeviceUnavailable:
            // Headphones pulled out. Without this iOS drops to the receiver
            // and she goes quiet mid-sentence. This is a real, physical event
            // that we did not cause, so reacting to it cannot loop.
            //
            // .categoryChange, .override and .routeConfigurationChange are NOT
            // handled, deliberately. Those are the speech recogniser doing its
            // job — and they are also what we ourselves produce every time we
            // touch the session. Answering them meant the app argued with
            // itself and with the microphone at the same time.
            //
            // .voiceChat set once at launch is enough to hold the loudspeaker.
            // The voices proved that. Let the recogniser work.
            AppDelegate.configureAudioSession(activate: false)
        default:
            break
        }
    }

    @objc func handleInterruption(_ notification: Notification) {
        guard
            let info = notification.userInfo,
            let raw = info[AVAudioSessionInterruptionTypeKey] as? UInt,
            let type = AVAudioSession.InterruptionType(rawValue: raw)
        else { return }

        if type == .ended {
            AppDelegate.configureAudioSession()
        }
    }

    func applicationWillResignActive(_ application: UIApplication) {
    }

    func applicationDidEnterBackground(_ application: UIApplication) {
    }

    func applicationWillEnterForeground(_ application: UIApplication) {
    }

    func applicationDidBecomeActive(_ application: UIApplication) {
        // Coming back from a phone call, or from another app that took the
        // session, can leave the category changed. Setting it again on return
        // means hands-free still works after an interruption rather than going
        // quiet until the app is restarted.
        AppDelegate.configureAudioSession()
    }

    func applicationWillTerminate(_ application: UIApplication) {
    }

    func application(_ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey: Any] = [:]) -> Bool {
        return ApplicationDelegateProxy.shared.application(app, open: url, options: options)
    }

    func application(_ application: UIApplication, continue userActivity: NSUserActivity, restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void) -> Bool {
        return ApplicationDelegateProxy.shared.application(application, continue: userActivity, restorationHandler: restorationHandler)
    }

}
