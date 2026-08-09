# Patched native plugin

`speech-recognition-Plugin.swift` is a MODIFIED copy of:

    node_modules/@capacitor-community/speech-recognition/ios/Plugin/Plugin.swift

node_modules is gitignored, so the live file is NOT saved by git.
npm install / npm ci will silently replace it with the stock version
and hands-free will stop working with no obvious cause.

## If hands-free breaks after an npm install

    cp plugin-patches/speech-recognition-Plugin.swift \
       node_modules/@capacitor-community/speech-recognition/ios/Plugin/Plugin.swift
    npx cap sync ios

## What was changed (v285-v291, August 2026)

- audio engine reused rather than recreated each start
- finish() instead of cancel() so the final result is delivered
- force-unwraps removed (crash on repeated sessions)
- late results delivered rather than dropped
- NSLog diagnostics ("TellMeHoney MIC: ...")

The JS side depends on this: index.html uses partialResults:true and ends
a turn on silence, then waits a short flush for stragglers.
