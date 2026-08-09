#import <Foundation/Foundation.h>
#import <Capacitor/Capacitor.h>

CAP_PLUGIN(AudioSessionPlugin, "AudioSession",
           CAP_PLUGIN_METHOD(toSpeaker, CAPPluginReturnPromise);
)
