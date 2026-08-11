# Patched speech-recognition plugin

`speech-recognition-Plugin.swift` is a patched copy of
`node_modules/@capacitor-community/speech-recognition/ios/Plugin/Plugin.swift`.

node_modules is gitignored, so this is the only backup.

**After any `npm install`, copy it back:**

    cp patches/speech-recognition-Plugin.swift \
       node_modules/@capacitor-community/speech-recognition/ios/Plugin/Plugin.swift
    npx cap sync ios

Changes: one AVAudioEngine reused rather than rebuilt each turn; `finish()`
instead of `cancel()` so a finalising result is not thrown away; force-unwraps
removed (they crashed the app); late results delivered instead of discarded;
removeTap on stop; NSLog diagnostics.
