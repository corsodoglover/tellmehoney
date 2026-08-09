import Foundation
import Capacitor
import Speech

@objc(SpeechRecognition)
public class SpeechRecognition: CAPPlugin {

    let defaultMatches = 5
    let messageMissingPermission = "Missing permission"
    let messageAccessDenied = "User denied access to speech recognition"
    let messageRestricted = "Speech recognition restricted on this device"
    let messageNotDetermined = "Speech recognition not determined on this device"
    let messageAccessDeniedMicrophone = "User denied access to microphone"
    let messageOngoing = "Ongoing speech recognition"
    let messageUnknown = "Unknown error occured"

    private var speechRecognizer: SFSpeechRecognizer?
    private var audioEngine: AVAudioEngine?
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?

    @objc func available(_ call: CAPPluginCall) {
        guard let recognizer = SFSpeechRecognizer() else {
            call.resolve([
                "available": false
            ])
            return
        }
        call.resolve([
            "available": recognizer.isAvailable
        ])
    }

    @objc func start(_ call: CAPPluginCall) {
        // Safe throughout. A force unwrap anywhere in this file is a crash
        // waiting for the moment the engine has already been torn down.
        if self.audioEngine?.isRunning == true {
            call.reject(self.messageOngoing)
            return
        }

        let status: SFSpeechRecognizerAuthorizationStatus = SFSpeechRecognizer.authorizationStatus()
        if status != SFSpeechRecognizerAuthorizationStatus.authorized {
            call.reject(self.messageMissingPermission)
            return
        }

        AVAudioSession.sharedInstance().requestRecordPermission { (granted) in
            if !granted {
                call.reject(self.messageAccessDeniedMicrophone)
                return
            }

            let language: String = call.getString("language") ?? "en-US"
            let maxResults: Int = call.getInt("maxResults") ?? self.defaultMatches
            let partialResults: Bool = call.getBool("partialResults") ?? false

            // ══════════ finish(), NOT cancel() ═════════════════════════
            // cancel() throws away a result that is still being finalised.
            // When you stop talking, endAudio() asks iOS for the final
            // transcription and that takes a moment to come back. Hands-free
            // reopens the microphone almost immediately — and this line then
            // destroyed the words that were about to arrive. Which is exactly
            // why toggling hands-free off and on by hand worked: the pause was
            // long enough for the result to land before the next start.
            //
            // finish() does the same teardown but lets the pending result
            // through first. Nothing is lost, and the turn completes on its
            // own instead of needing a human to slow it down.
            if self.recognitionTask != nil {
                self.recognitionTask?.finish()
                self.recognitionTask = nil
            }

            // ══════════ ONE ENGINE, REUSED ═════════════════════════════
            // This used to be AVAudioEngine.init() on every single start().
            // Hands-free reopens the microphone after every turn, so a few
            // minutes of conversation manufactured dozens of engines - and
            // only the one that reached a final result was ever stopped. The
            // abandoned ones keep their claim on the input hardware, so
            // eventually a new engine installs its tap on a microphone that
            // something else still owns. The tap attaches, no buffers ever
            // arrive, and the recogniser reports "No speech detected" before
            // the engine has even finished starting. Which is exactly the
            // pattern in the logs: the first turns carry buffers, later ones
            // carry none at all.
            //
            // So keep one engine for the life of the plugin, and take it down
            // properly before each use rather than walking away from it.
            if let existing = self.audioEngine {
                if existing.isRunning { existing.stop() }
                existing.inputNode.removeTap(onBus: 0)
                existing.reset()
            } else {
                self.audioEngine = AVAudioEngine()
            }
            self.speechRecognizer = SFSpeechRecognizer.init(locale: Locale(identifier: language))

            let audioSession: AVAudioSession = AVAudioSession.sharedInstance()
            do {
                try audioSession.setCategory(AVAudioSession.Category.playAndRecord, options: AVAudioSession.CategoryOptions.defaultToSpeaker)
                try audioSession.setMode(AVAudioSession.Mode.default)
                do {
                    try audioSession.setActive(true, options: AVAudioSession.SetActiveOptions.notifyOthersOnDeactivation)
                } catch {
                      call.reject("Microphone is already in use by another application.")
                      return
                }
            } catch {

            }

            // Hold the request locally as well as on the instance. A previous
            // task's handler can fire WHILE this start is still running - the
            // logs show exactly that, an old "No speech detected" arriving
            // mid-start - and that handler sets self.recognitionRequest = nil.
            // Force-unwrapping the property a few lines later then killed the
            // app. A local reference cannot be pulled out from under us.
            let request = SFSpeechAudioBufferRecognitionRequest()
            request.shouldReportPartialResults = partialResults
            self.recognitionRequest = request

            // Last force unwrap in the file, gone. The engine is created or
            // reused a few lines above so it cannot be nil here — but this
            // file has crashed twice already on exactly that kind of "cannot
            // be nil" reasoning, and a crash costs an hour of testing to
            // diagnose. Bail cleanly instead.
            guard let engine = self.audioEngine else {
                call.reject("Audio engine unavailable")
                return
            }
            let inputNode: AVAudioInputNode = engine.inputNode

            // ══════════ THE TAP FORMAT — THIS IS THE FIX ════════════════════
            //
            // The original line was:
            //
            //     let format = inputNode.outputFormat(forBus: 0)
            //
            // outputFormat describes what the node hands DOWNSTREAM inside the
            // engine graph. Before the engine has been started and the hardware
            // engaged, that can come back as a placeholder — sample rate 0,
            // channel count 0. installTap accepts it without complaint, and
            // then never delivers a single buffer. The engine runs, the
            // recogniser waits, and eventually gives up with "No speech
            // detected" — which reads like a microphone that cannot hear you,
            // when in fact nothing was ever plumbed to it.
            //
            // inputFormat is the hardware's actual input format, and it is
            // valid before the engine starts. Take that when it is usable, and
            // only fall back to outputFormat if it is not. Refuse outright if
            // neither is real, because a silent failure here costs hours —
            // better a clear rejection the app can show.
            let hwFormat: AVAudioFormat = inputNode.inputFormat(forBus: 0)
            let outFormat: AVAudioFormat = inputNode.outputFormat(forBus: 0)

            NSLog("TellMeHoney MIC: inputFormat rate=\(hwFormat.sampleRate) ch=\(hwFormat.channelCount) | outputFormat rate=\(outFormat.sampleRate) ch=\(outFormat.channelCount)")

            var format: AVAudioFormat = hwFormat
            if hwFormat.sampleRate <= 0 || hwFormat.channelCount == 0 {
                format = outFormat
                NSLog("TellMeHoney MIC: inputFormat unusable, falling back to outputFormat")
            }
            if format.sampleRate <= 0 || format.channelCount == 0 {
                NSLog("TellMeHoney MIC: BOTH formats unusable — refusing to start")
                call.reject("Microphone format unavailable")
                return
            }

            self.recognitionTask = self.speechRecognizer?.recognitionTask(with: request, resultHandler: { (result, error) in
                // ══════════ STALE, BUT STILL WORTH HEARING ═════════════
                // This used to `return` outright when the request was no
                // longer the current one. That threw away the very words the
                // turn was for: stop() asks iOS to finalise, iOS takes a
                // moment, and hands-free has already opened the next mic by
                // then — so the finished sentence arrived looking "stale" and
                // was discarded. It only worked when a human toggled
                // hands-free, because that left a long enough gap.
                //
                // A stale handler must not touch shared state — that was the
                // real danger, and `isCurrent` still guards it below. But its
                // result belongs to the person who spoke it. Deliver it.
                let isCurrent = (self.recognitionRequest === request)
                if result != nil {
                    let resultArray: NSMutableArray = NSMutableArray()
                    var counter: Int = 0

                    for transcription: SFTranscription in result!.transcriptions {
                        if maxResults > 0 && counter < maxResults {
                            resultArray.add(transcription.formattedString)
                        }
                        counter+=1
                    }

                    if partialResults {
                        self.notifyListeners("partialResults", data: ["matches": resultArray])
                    } else {
                        call.resolve([
                            "matches": resultArray
                        ])
                    }

                    if result!.isFinal {
                        // Only tear down if this is still the live turn. A
                        // late result from a finished turn has already handed
                        // its words over above; it must not stop an engine
                        // that a newer turn is using.
                        if isCurrent {
                            self.audioEngine?.stop()
                            self.audioEngine?.inputNode.removeTap(onBus: 0)
                            self.notifyListeners("listeningState", data: ["status": "stopped"])
                            self.recognitionTask = nil
                            self.recognitionRequest = nil
                        }
                    }
                }

                if error != nil {
                    NSLog("TellMeHoney MIC: recognition error — \(error!.localizedDescription)")
                    // ══════════ THIS LINE WAS CRASHING THE APP ══════════════
                    // It was self.audioEngine!.stop() — a force unwrap. By the
                    // time this handler runs the engine has usually already
                    // been stopped and cleared by the final-result branch or by
                    // stop(), so audioEngine is nil and the force unwrap kills
                    // the process outright. That is the app "glitching out and
                    // going back to the home screen": it heard the words, sent
                    // them to JavaScript, and then died before anything could
                    // answer. Optional chaining does the same work and cannot
                    // crash.
                    if isCurrent {
                        self.audioEngine?.stop()
                        self.audioEngine?.inputNode.removeTap(onBus: 0)
                        self.recognitionRequest = nil
                        self.recognitionTask = nil
                        self.notifyListeners("listeningState", data: ["status": "stopped"])
                    }
                    // "Recognition request was canceled" is what a normal stop
                    // looks like from in here — the turn ended on purpose. It
                    // is not a failure worth showing anybody, and rejecting on
                    // it made every successful turn end in an error toast.
                    let msg = error!.localizedDescription
                    if msg.range(of: "cancel", options: .caseInsensitive) == nil {
                        call.reject(msg)
                    } else {
                        call.resolve(["matches": NSMutableArray()])
                    }
                }
            })

            // Count the buffers. If this stays at zero while the engine is
            // running, the tap is attached to nothing and the format is still
            // wrong — which is a different problem from the microphone hearing
            // silence, and the two are indistinguishable from the outside.
            var bufferCount = 0
            inputNode.installTap(onBus: 0, bufferSize: 1024, format: format) { (buffer: AVAudioPCMBuffer, _: AVAudioTime) in
                bufferCount += 1
                if bufferCount == 1 || bufferCount == 50 {
                    NSLog("TellMeHoney MIC: buffer \(bufferCount) received, frames=\(buffer.frameLength)")
                }
                request.append(buffer)
            }

            self.audioEngine?.prepare()
            do {
                try self.audioEngine?.start()
                NSLog("TellMeHoney MIC: engine started with rate=\(format.sampleRate) ch=\(format.channelCount)")
                self.notifyListeners("listeningState", data: ["status": "started"])
                if partialResults {
                    call.resolve()
                }
            } catch {
                NSLog("TellMeHoney MIC: engine failed to start — \(error.localizedDescription)")
                call.reject(self.messageUnknown)
            }
        }
    }

    @objc func stop(_ call: CAPPluginCall) {
        DispatchQueue.global(qos: DispatchQoS.QoSClass.default).async {
            if let engine = self.audioEngine, engine.isRunning {
                engine.stop()
                // Remove the tap as well. Leaving it attached is what kept
                // isRunning reading true a moment longer than it should and
                // produced "Ongoing speech recognition" on the next open.
                engine.inputNode.removeTap(onBus: 0)
                self.recognitionRequest?.endAudio()
                self.notifyListeners("listeningState", data: ["status": "stopped"])
            }
            call.resolve()
        }
    }

    @objc func isListening(_ call: CAPPluginCall) {
        let isListening = self.audioEngine?.isRunning ?? false
        call.resolve([
            "listening": isListening
        ])
    }

    @objc func getSupportedLanguages(_ call: CAPPluginCall) {
        let supportedLanguages: Set<Locale>! = SFSpeechRecognizer.supportedLocales() as Set<Locale>
        let languagesArr: NSMutableArray = NSMutableArray()

        for lang: Locale in supportedLanguages {
            languagesArr.add(lang.identifier)
        }

        call.resolve([
            "languages": languagesArr
        ])
    }

    @objc override public func checkPermissions(_ call: CAPPluginCall) {
        let status: SFSpeechRecognizerAuthorizationStatus = SFSpeechRecognizer.authorizationStatus()
        let permission: String
        switch status {
        case .authorized:
            permission = "granted"
        case .denied, .restricted:
            permission = "denied"
        case .notDetermined:
            permission = "prompt"
        @unknown default:
            permission = "prompt"
        }
        call.resolve(["speechRecognition": permission])
    }

    @objc override public func requestPermissions(_ call: CAPPluginCall) {
        SFSpeechRecognizer.requestAuthorization { (status: SFSpeechRecognizerAuthorizationStatus) in
            DispatchQueue.main.async {
                switch status {
                case .authorized:
                    AVAudioSession.sharedInstance().requestRecordPermission { (granted: Bool) in
                        if granted {
                            call.resolve(["speechRecognition": "granted"])
                        } else {
                            call.resolve(["speechRecognition": "denied"])
                        }
                    }
                    break
                case .denied, .restricted, .notDetermined:
                    self.checkPermissions(call)
                    break
                @unknown default:
                    self.checkPermissions(call)
                }
            }
        }
    }
}
