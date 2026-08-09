import UIKit
import Capacitor
import AVFoundation

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?

    // ══════════ AUDIO SESSION WORK IS DISABLED ON PURPOSE ═══════════════════
    //
    // TEST BUILD. Everything this file used to do to the audio session is
    // switched off below, and here is the reasoning.
    //
    // The speech plugin was never actually in the iOS build until the CocoaPods
    // conversion. So every audio-session theory in this file was written to
    // explain the behaviour of a recogniser that was not there — hands-free was
    // silently falling back to webkitSpeechRecognition in the web view. The
    // comments were careful and reasonable and they were describing a ghost.
    //
    // Now the real plugin runs, and the symptom has changed to "No speech
    // detected": the microphone opens, the engine runs, and no audio ever
    // arrives at the recogniser. That points straight back here.
    //
    //   • mode .voiceChat turns on the voice-processing I/O unit. The plugin
    //     builds its tap from inputNode.outputFormat(forBus: 0). With voice
    //     processing active that format can differ from what the tap expects,
    //     and a mismatched tap installs cleanly and then delivers nothing at
    //     all. Engine running, recogniser listening, silence. Exactly this.
    //
    //   • The route observer fires overrideOutputAudioPort 0.2s after any route
    //     change — and starting the recogniser IS a route change. So a fifth of
    //     a second into every listening session, this file reached into a live
    //     recording session and changed its output port, which can restart the
    //     audio unit and detach the input tap underneath.
    //
    //   • applicationDidBecomeActive reconfigured the whole session again on
    //     every return to the foreground.
    //
    // The plugin sets its own session properly — .playAndRecord with
    // .defaultToSpeaker and mode .default — and that is the configuration it
    // was written and tested against. So: let it. If speech is detected with
    // this file quiet, we know what was breaking it, and any speaker routing we
    // still need can be added back one piece at a time, with the microphone
    // working as the thing we protect.
    //
    // Nothing is deleted. If this makes no difference, put it all back.

    private static var isConfiguring = false

    static func configureAudioSession(activate: Bool = true) {
        // DISABLED FOR TEST — see the note above.
        // The original body is kept below so it can be restored in one edit.
        //
        // if isConfiguring { return }
        // isConfiguring = true
        // defer { isConfiguring = false }
        //
        // let session = AVAudioSession.sharedInstance()
        // do {
        //     try session.setCategory(
        //         .playAndRecord,
        //         mode: .voiceChat,
        //         options: [.defaultToSpeaker, .allowBluetoothHFP]
        //     )
        //     if activate { try session.setActive(true, options: []) }
        //     if session.currentRoute.outputs.allSatisfy({ $0.portType == .builtInReceiver }) {
        //         try? session.overrideOutputAudioPort(.speaker)
        //     }
        // } catch {
        //     NSLog("TellMeHoney: audio session setup failed — \(error.localizedDescription)")
        // }
        NSLog("TellMeHoney: configureAudioSession skipped (test build)")
    }

    // Left in place and unused. Nothing calls it while the observer is off.
    static func forceSpeakerIfOnReceiver() {
        let session = AVAudioSession.sharedInstance()
        let onReceiver = session.currentRoute.outputs.contains { $0.portType == .builtInReceiver }
        guard onReceiver else { return }
        try? session.overrideOutputAudioPort(.speaker)
    }

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {

        // DISABLED FOR TEST — the plugin configures the session itself.
        // AppDelegate.configureAudioSession()

        // DISABLED FOR TEST — this fired overrideOutputAudioPort 0.2s after
        // every route change, and opening the microphone is a route change.
        // NotificationCenter.default.addObserver(
        //     self,
        //     selector: #selector(handleRouteChange(_:)),
        //     name: AVAudioSession.routeChangeNotification,
        //     object: nil
        // )

        // Interruptions are left alone too, so that nothing in this file
        // touches the session while we find out whether it was the problem.
        // NotificationCenter.default.addObserver(
        //     self,
        //     selector: #selector(handleInterruption(_:)),
        //     name: AVAudioSession.interruptionNotification,
        //     object: nil
        // )

        return true
    }

    @objc func handleRouteChange(_ notification: Notification) {
        // Not registered in this build.
    }

    @objc func handleInterruption(_ notification: Notification) {
        // Not registered in this build.
    }

    func applicationWillResignActive(_ application: UIApplication) {
    }

    func applicationDidEnterBackground(_ application: UIApplication) {
    }

    func applicationWillEnterForeground(_ application: UIApplication) {
    }

    func applicationDidBecomeActive(_ application: UIApplication) {
        // DISABLED FOR TEST — this reconfigured the session on every return to
        // the foreground, including straight after granting a permission.
        // AppDelegate.configureAudioSession()
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
