System.config({
  baseURL: "/",
  defaultJSExtensions: true,
  transpiler: "babel",
  babelOptions: {
    "optional": [
      "runtime",
      "optimisation.modules.system"
    ]
  },
  paths: {
    "github:*": "jspm_packages/github/*",
    "npm:*": "jspm_packages/npm/*"
  },
  bundles: {
    "build.js": [
      "app.js",
      "npm:font-awesome@4.7.0.js",
      "npm:font-awesome@4.7.0/css/font-awesome.css!github:systemjs/plugin-css@0.1.32.js",
      "github:izderadicka/asexor_js_client@master.js",
      "github:izderadicka/asexor_js_client@master/lib/index.js",
      "github:izderadicka/asexor_js_client@master/lib/longpoll-client.js",
      "github:izderadicka/asexor_js_client@master/lib/base-client.js",
      "github:izderadicka/asexor_js_client@master/lib/wamp-client.js",
      "npm:autobahn@0.11.2.js",
      "npm:autobahn@0.11.2/index.js",
      "npm:autobahn@0.11.2/lib/autobahn.js",
      "npm:autobahn@0.11.2/lib/auth/cra.js",
      "npm:crypto-js@3.1.9-1.js",
      "npm:crypto-js@3.1.9-1/index.js",
      "npm:crypto-js@3.1.9-1/rabbit-legacy.js",
      "npm:crypto-js@3.1.9-1/cipher-core.js",
      "github:jspm/nodelibs-process@0.1.2.js",
      "github:jspm/nodelibs-process@0.1.2/index.js",
      "npm:process@0.11.9.js",
      "npm:process@0.11.9/browser.js",
      "github:jspm/nodelibs-buffer@0.1.0.js",
      "github:jspm/nodelibs-buffer@0.1.0/index.js",
      "npm:buffer@3.6.0.js",
      "npm:buffer@3.6.0/index.js",
      "npm:isarray@1.0.0.js",
      "npm:isarray@1.0.0/index.js",
      "npm:ieee754@1.1.8.js",
      "npm:ieee754@1.1.8/index.js",
      "npm:base64-js@0.0.8.js",
      "npm:base64-js@0.0.8/lib/b64.js",
      "npm:crypto-js@3.1.9-1/evpkdf.js",
      "npm:crypto-js@3.1.9-1/hmac.js",
      "npm:crypto-js@3.1.9-1/core.js",
      "npm:crypto-js@3.1.9-1/sha1.js",
      "npm:crypto-js@3.1.9-1/md5.js",
      "npm:crypto-js@3.1.9-1/enc-base64.js",
      "npm:crypto-js@3.1.9-1/rabbit.js",
      "npm:crypto-js@3.1.9-1/rc4.js",
      "npm:crypto-js@3.1.9-1/tripledes.js",
      "npm:crypto-js@3.1.9-1/aes.js",
      "npm:crypto-js@3.1.9-1/format-hex.js",
      "npm:crypto-js@3.1.9-1/pad-nopadding.js",
      "npm:crypto-js@3.1.9-1/pad-zeropadding.js",
      "npm:crypto-js@3.1.9-1/pad-iso97971.js",
      "npm:crypto-js@3.1.9-1/pad-iso10126.js",
      "npm:crypto-js@3.1.9-1/pad-ansix923.js",
      "npm:crypto-js@3.1.9-1/mode-ecb.js",
      "npm:crypto-js@3.1.9-1/mode-ofb.js",
      "npm:crypto-js@3.1.9-1/mode-ctr-gladman.js",
      "npm:crypto-js@3.1.9-1/mode-ctr.js",
      "npm:crypto-js@3.1.9-1/mode-cfb.js",
      "npm:crypto-js@3.1.9-1/pbkdf2.js",
      "npm:crypto-js@3.1.9-1/ripemd160.js",
      "npm:crypto-js@3.1.9-1/sha3.js",
      "npm:crypto-js@3.1.9-1/x64-core.js",
      "npm:crypto-js@3.1.9-1/sha384.js",
      "npm:crypto-js@3.1.9-1/sha512.js",
      "npm:crypto-js@3.1.9-1/sha224.js",
      "npm:crypto-js@3.1.9-1/sha256.js",
      "npm:crypto-js@3.1.9-1/enc-utf16.js",
      "npm:crypto-js@3.1.9-1/lib-typedarrays.js",
      "npm:autobahn@0.11.2/lib/auth/persona.js",
      "npm:when@3.7.8/function.js",
      "npm:when@3.7.8/lib/apply.js",
      "npm:when@3.7.8/lib/liftAll.js",
      "npm:when@3.7.8/when.js",
      "npm:when@3.7.8/lib/Promise.js",
      "npm:when@3.7.8/lib/env.js",
      "npm:when@3.7.8/lib/Scheduler.js",
      "npm:when@3.7.8/lib/makePromise.js",
      "npm:when@3.7.8/lib/TimeoutError.js",
      "npm:when@3.7.8/lib/decorators/unhandledRejection.js",
      "npm:when@3.7.8/lib/format.js",
      "npm:when@3.7.8/lib/decorators/with.js",
      "npm:when@3.7.8/lib/decorators/progress.js",
      "npm:when@3.7.8/lib/decorators/iterate.js",
      "npm:when@3.7.8/lib/decorators/inspect.js",
      "npm:when@3.7.8/lib/state.js",
      "npm:when@3.7.8/lib/decorators/fold.js",
      "npm:when@3.7.8/lib/decorators/flow.js",
      "npm:when@3.7.8/lib/decorators/array.js",
      "npm:when@3.7.8/lib/decorators/timed.js",
      "npm:when@3.7.8.js",
      "npm:autobahn@0.11.2/lib/serializer.js",
      "npm:msgpack-lite@0.1.26.js",
      "npm:msgpack-lite@0.1.26/lib/browser.js",
      "npm:msgpack-lite@0.1.26/lib/codec.js",
      "npm:msgpack-lite@0.1.26/lib/codec-base.js",
      "npm:msgpack-lite@0.1.26/lib/bufferish.js",
      "npm:msgpack-lite@0.1.26/lib/bufferish-proto.js",
      "npm:msgpack-lite@0.1.26/lib/buffer-lite.js",
      "npm:msgpack-lite@0.1.26/lib/bufferish-uint8array.js",
      "npm:msgpack-lite@0.1.26/lib/bufferish-buffer.js",
      "npm:msgpack-lite@0.1.26/lib/bufferish-array.js",
      "npm:msgpack-lite@0.1.26/lib/buffer-global.js",
      "npm:msgpack-lite@0.1.26/lib/write-core.js",
      "npm:msgpack-lite@0.1.26/lib/write-type.js",
      "npm:msgpack-lite@0.1.26/lib/ext-buffer.js",
      "npm:msgpack-lite@0.1.26/lib/write-uint8.js",
      "npm:msgpack-lite@0.1.26/lib/write-token.js",
      "npm:int64-buffer@0.1.9.js",
      "npm:int64-buffer@0.1.9/int64-buffer.js",
      "npm:msgpack-lite@0.1.26/lib/ext-packer.js",
      "npm:msgpack-lite@0.1.26/lib/encode.js",
      "npm:msgpack-lite@0.1.26/lib/encode-buffer.js",
      "npm:msgpack-lite@0.1.26/lib/flex-buffer.js",
      "npm:msgpack-lite@0.1.26/lib/read-core.js",
      "npm:msgpack-lite@0.1.26/lib/read-token.js",
      "npm:msgpack-lite@0.1.26/lib/read-format.js",
      "npm:msgpack-lite@0.1.26/lib/ext-unpacker.js",
      "npm:msgpack-lite@0.1.26/lib/decode.js",
      "npm:msgpack-lite@0.1.26/lib/decode-buffer.js",
      "npm:msgpack-lite@0.1.26/lib/ext.js",
      "npm:msgpack-lite@0.1.26/lib/decoder.js",
      "npm:event-lite@0.1.1.js",
      "npm:event-lite@0.1.1/event-lite.js",
      "npm:msgpack-lite@0.1.26/lib/encoder.js",
      "npm:autobahn@0.11.2/lib/log.js",
      "npm:autobahn@0.11.2/lib/configure.js",
      "npm:autobahn@0.11.2/lib/transport/rawsocket.js",
      "github:jspm/nodelibs-net@0.1.2.js",
      "github:jspm/nodelibs-net@0.1.2/index.js",
      "github:jspm/nodelibs-http@1.7.1.js",
      "github:jspm/nodelibs-http@1.7.1/index.js",
      "github:jspm/nodelibs-url@0.1.0.js",
      "github:jspm/nodelibs-url@0.1.0/index.js",
      "npm:url@0.10.3.js",
      "npm:url@0.10.3/url.js",
      "npm:querystring@0.2.0.js",
      "npm:querystring@0.2.0/index.js",
      "npm:querystring@0.2.0/encode.js",
      "npm:querystring@0.2.0/decode.js",
      "npm:punycode@1.3.2.js",
      "npm:punycode@1.3.2/punycode.js",
      "github:jspm/nodelibs-http@1.7.1/lib/request.js",
      "npm:inherits@2.0.1.js",
      "npm:inherits@2.0.1/inherits_browser.js",
      "npm:Base64@0.2.1.js",
      "npm:Base64@0.2.1/base64.js",
      "github:jspm/nodelibs-http@1.7.1/lib/response.js",
      "github:jspm/nodelibs-util@0.1.0.js",
      "github:jspm/nodelibs-util@0.1.0/index.js",
      "npm:util@0.10.3.js",
      "npm:util@0.10.3/util.js",
      "npm:util@0.10.3/support/isBufferBrowser.js",
      "github:jspm/nodelibs-stream@0.1.0.js",
      "github:jspm/nodelibs-stream@0.1.0/index.js",
      "npm:stream-browserify@1.0.0.js",
      "npm:stream-browserify@1.0.0/index.js",
      "npm:readable-stream@1.1.14/passthrough.js",
      "npm:readable-stream@1.1.14/lib/_stream_passthrough.js",
      "npm:core-util-is@1.0.2.js",
      "npm:core-util-is@1.0.2/lib/util.js",
      "npm:readable-stream@1.1.14/lib/_stream_transform.js",
      "npm:readable-stream@1.1.14/lib/_stream_duplex.js",
      "npm:readable-stream@1.1.14/lib/_stream_writable.js",
      "npm:readable-stream@1.1.14/lib/_stream_readable.js",
      "npm:string_decoder@0.10.31.js",
      "npm:string_decoder@0.10.31/index.js",
      "github:jspm/nodelibs-events@0.1.1.js",
      "github:jspm/nodelibs-events@0.1.1/index.js",
      "npm:events@1.0.2.js",
      "npm:events@1.0.2/events.js",
      "npm:isarray@0.0.1.js",
      "npm:isarray@0.0.1/index.js",
      "npm:readable-stream@1.1.14/transform.js",
      "npm:readable-stream@1.1.14/duplex.js",
      "npm:readable-stream@1.1.14/writable.js",
      "npm:readable-stream@1.1.14/readable.js",
      "github:jspm/nodelibs-timers@0.1.0.js",
      "github:jspm/nodelibs-timers@0.1.0/index.js",
      "npm:timers-browserify@1.4.2.js",
      "npm:timers-browserify@1.4.2/main.js",
      "npm:autobahn@0.11.2/lib/util.js",
      "npm:autobahn@0.11.2/lib/transport/longpoll.js",
      "npm:autobahn@0.11.2/lib/transport/websocket.js",
      "npm:autobahn@0.11.2/lib/connection.js",
      "npm:autobahn@0.11.2/lib/session.js",
      "npm:when@3.7.8/monitor/console.js",
      "npm:when@3.7.8/monitor.js",
      "npm:when@3.7.8/monitor/ConsoleReporter.js",
      "npm:when@3.7.8/monitor/error.js",
      "npm:when@3.7.8/monitor/PromiseMonitor.js",
      "npm:autobahn@0.11.2/package.json!github:systemjs/plugin-json@0.1.2.js",
      "npm:autobahn@0.11.2/lib/polyfill.js",
      "npm:autobahn@0.11.2/lib/polyfill/json.js",
      "npm:autobahn@0.11.2/lib/polyfill/typedarray.js",
      "npm:autobahn@0.11.2/lib/polyfill/console.js",
      "npm:autobahn@0.11.2/lib/polyfill/function.js",
      "npm:autobahn@0.11.2/lib/polyfill/string.js",
      "npm:autobahn@0.11.2/lib/polyfill/array.js",
      "npm:autobahn@0.11.2/lib/polyfill/object.js",
      "github:izderadicka/asexor_js_client@master/lib/client.js",
      "npm:jquery@3.1.1.js",
      "npm:jquery@3.1.1/dist/jquery.js",
      "github:twbs/bootstrap@3.3.7/css/bootstrap.css!github:systemjs/plugin-css@0.1.32.js",
      "github:twbs/bootstrap@3.3.7.js",
      "github:twbs/bootstrap@3.3.7/js/bootstrap.js",
      "npm:babel-runtime@5.8.38/core-js/get-iterator.js",
      "npm:core-js@1.2.7/library/fn/get-iterator.js",
      "npm:core-js@1.2.7/library/modules/core.get-iterator.js",
      "npm:core-js@1.2.7/library/modules/$.core.js",
      "npm:core-js@1.2.7/library/modules/core.get-iterator-method.js",
      "npm:core-js@1.2.7/library/modules/$.iterators.js",
      "npm:core-js@1.2.7/library/modules/$.wks.js",
      "npm:core-js@1.2.7/library/modules/$.global.js",
      "npm:core-js@1.2.7/library/modules/$.uid.js",
      "npm:core-js@1.2.7/library/modules/$.shared.js",
      "npm:core-js@1.2.7/library/modules/$.classof.js",
      "npm:core-js@1.2.7/library/modules/$.cof.js",
      "npm:core-js@1.2.7/library/modules/$.an-object.js",
      "npm:core-js@1.2.7/library/modules/$.is-object.js",
      "npm:core-js@1.2.7/library/modules/es6.string.iterator.js",
      "npm:core-js@1.2.7/library/modules/$.iter-define.js",
      "npm:core-js@1.2.7/library/modules/$.js",
      "npm:core-js@1.2.7/library/modules/$.set-to-string-tag.js",
      "npm:core-js@1.2.7/library/modules/$.has.js",
      "npm:core-js@1.2.7/library/modules/$.iter-create.js",
      "npm:core-js@1.2.7/library/modules/$.hide.js",
      "npm:core-js@1.2.7/library/modules/$.descriptors.js",
      "npm:core-js@1.2.7/library/modules/$.fails.js",
      "npm:core-js@1.2.7/library/modules/$.property-desc.js",
      "npm:core-js@1.2.7/library/modules/$.redefine.js",
      "npm:core-js@1.2.7/library/modules/$.export.js",
      "npm:core-js@1.2.7/library/modules/$.ctx.js",
      "npm:core-js@1.2.7/library/modules/$.a-function.js",
      "npm:core-js@1.2.7/library/modules/$.library.js",
      "npm:core-js@1.2.7/library/modules/$.string-at.js",
      "npm:core-js@1.2.7/library/modules/$.defined.js",
      "npm:core-js@1.2.7/library/modules/$.to-integer.js",
      "npm:core-js@1.2.7/library/modules/web.dom.iterable.js",
      "npm:core-js@1.2.7/library/modules/es6.array.iterator.js",
      "npm:core-js@1.2.7/library/modules/$.to-iobject.js",
      "npm:core-js@1.2.7/library/modules/$.iobject.js",
      "npm:core-js@1.2.7/library/modules/$.iter-step.js",
      "npm:core-js@1.2.7/library/modules/$.add-to-unscopables.js",
      "npm:babel-runtime@5.8.38/core-js/object/assign.js",
      "npm:core-js@1.2.7/library/fn/object/assign.js",
      "npm:core-js@1.2.7/library/modules/es6.object.assign.js",
      "npm:core-js@1.2.7/library/modules/$.object-assign.js",
      "npm:core-js@1.2.7/library/modules/$.to-object.js",
      "npm:babel-runtime@5.8.38/core-js/map.js",
      "npm:core-js@1.2.7/library/fn/map.js",
      "npm:core-js@1.2.7/library/modules/es7.map.to-json.js",
      "npm:core-js@1.2.7/library/modules/$.collection-to-json.js",
      "npm:core-js@1.2.7/library/modules/$.for-of.js",
      "npm:core-js@1.2.7/library/modules/$.to-length.js",
      "npm:core-js@1.2.7/library/modules/$.is-array-iter.js",
      "npm:core-js@1.2.7/library/modules/$.iter-call.js",
      "npm:core-js@1.2.7/library/modules/es6.map.js",
      "npm:core-js@1.2.7/library/modules/$.collection.js",
      "npm:core-js@1.2.7/library/modules/$.strict-new.js",
      "npm:core-js@1.2.7/library/modules/$.redefine-all.js",
      "npm:core-js@1.2.7/library/modules/$.collection-strong.js",
      "npm:core-js@1.2.7/library/modules/$.set-species.js",
      "npm:core-js@1.2.7/library/modules/es6.object.to-string.js"
    ]
  },

  map: {
    "autobahn": "npm:autobahn@0.11.2",
    "babel": "npm:babel-core@5.8.38",
    "babel-runtime": "npm:babel-runtime@5.8.38",
    "bootstrap": "github:twbs/bootstrap@3.3.7",
    "core-js": "npm:core-js@1.2.7",
    "css": "github:systemjs/plugin-css@0.1.32",
    "font-awesome": "npm:font-awesome@4.7.0",
    "izderadicka/asexor_js_client": "github:izderadicka/asexor_js_client@master",
    "jquery": "npm:jquery@3.1.1",
    "github:jspm/nodelibs-assert@0.1.0": {
      "assert": "npm:assert@1.4.1"
    },
    "github:jspm/nodelibs-buffer@0.1.0": {
      "buffer": "npm:buffer@3.6.0"
    },
    "github:jspm/nodelibs-constants@0.1.0": {
      "constants-browserify": "npm:constants-browserify@0.0.1"
    },
    "github:jspm/nodelibs-crypto@0.1.0": {
      "crypto-browserify": "npm:crypto-browserify@3.11.0"
    },
    "github:jspm/nodelibs-events@0.1.1": {
      "events": "npm:events@1.0.2"
    },
    "github:jspm/nodelibs-http@1.7.1": {
      "Base64": "npm:Base64@0.2.1",
      "events": "github:jspm/nodelibs-events@0.1.1",
      "inherits": "npm:inherits@2.0.1",
      "stream": "github:jspm/nodelibs-stream@0.1.0",
      "url": "github:jspm/nodelibs-url@0.1.0",
      "util": "github:jspm/nodelibs-util@0.1.0"
    },
    "github:jspm/nodelibs-https@0.1.0": {
      "https-browserify": "npm:https-browserify@0.0.0"
    },
    "github:jspm/nodelibs-net@0.1.2": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "crypto": "github:jspm/nodelibs-crypto@0.1.0",
      "http": "github:jspm/nodelibs-http@1.7.1",
      "net": "github:jspm/nodelibs-net@0.1.2",
      "process": "github:jspm/nodelibs-process@0.1.2",
      "stream": "github:jspm/nodelibs-stream@0.1.0",
      "timers": "github:jspm/nodelibs-timers@0.1.0",
      "util": "github:jspm/nodelibs-util@0.1.0"
    },
    "github:jspm/nodelibs-os@0.1.0": {
      "os-browserify": "npm:os-browserify@0.1.2"
    },
    "github:jspm/nodelibs-path@0.1.0": {
      "path-browserify": "npm:path-browserify@0.0.0"
    },
    "github:jspm/nodelibs-process@0.1.2": {
      "process": "npm:process@0.11.9"
    },
    "github:jspm/nodelibs-stream@0.1.0": {
      "stream-browserify": "npm:stream-browserify@1.0.0"
    },
    "github:jspm/nodelibs-string_decoder@0.1.0": {
      "string_decoder": "npm:string_decoder@0.10.31"
    },
    "github:jspm/nodelibs-timers@0.1.0": {
      "timers-browserify": "npm:timers-browserify@1.4.2"
    },
    "github:jspm/nodelibs-url@0.1.0": {
      "url": "npm:url@0.10.3"
    },
    "github:jspm/nodelibs-util@0.1.0": {
      "util": "npm:util@0.10.3"
    },
    "github:jspm/nodelibs-vm@0.1.0": {
      "vm-browserify": "npm:vm-browserify@0.0.4"
    },
    "github:jspm/nodelibs-zlib@0.1.0": {
      "browserify-zlib": "npm:browserify-zlib@0.1.4"
    },
    "github:twbs/bootstrap@3.3.7": {
      "jquery": "npm:jquery@3.1.1"
    },
    "npm:are-we-there-yet@1.1.2": {
      "delegates": "npm:delegates@1.0.0",
      "events": "github:jspm/nodelibs-events@0.1.1",
      "readable-stream": "npm:readable-stream@1.1.14",
      "util": "github:jspm/nodelibs-util@0.1.0"
    },
    "npm:asn1.js@4.9.1": {
      "bn.js": "npm:bn.js@4.11.6",
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "inherits": "npm:inherits@2.0.1",
      "minimalistic-assert": "npm:minimalistic-assert@1.0.0",
      "vm": "github:jspm/nodelibs-vm@0.1.0"
    },
    "npm:assert@1.4.1": {
      "assert": "github:jspm/nodelibs-assert@0.1.0",
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "process": "github:jspm/nodelibs-process@0.1.2",
      "util": "npm:util@0.10.3"
    },
    "npm:autobahn@0.11.2": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "bufferutil": "npm:bufferutil@2.0.1",
      "crypto-js": "npm:crypto-js@3.1.9-1",
      "events": "github:jspm/nodelibs-events@0.1.1",
      "int64-buffer": "npm:int64-buffer@0.1.9",
      "msgpack-lite": "npm:msgpack-lite@0.1.26",
      "net": "github:jspm/nodelibs-net@0.1.2",
      "process": "github:jspm/nodelibs-process@0.1.2",
      "systemjs-json": "github:systemjs/plugin-json@0.1.2",
      "tweetnacl": "npm:tweetnacl@1.0.0-rc.1",
      "utf-8-validate": "npm:utf-8-validate@3.0.1",
      "when": "npm:when@3.7.8"
    },
    "npm:babel-runtime@5.8.38": {
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:bindings@1.2.1": {
      "fs": "github:jspm/nodelibs-fs@0.1.2",
      "path": "github:jspm/nodelibs-path@0.1.0",
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:bl@1.2.0": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "readable-stream": "npm:readable-stream@2.2.3",
      "util": "github:jspm/nodelibs-util@0.1.0"
    },
    "npm:bn.js@4.11.6": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0"
    },
    "npm:browserify-aes@1.0.6": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "buffer-xor": "npm:buffer-xor@1.0.3",
      "cipher-base": "npm:cipher-base@1.0.3",
      "create-hash": "npm:create-hash@1.1.2",
      "crypto": "github:jspm/nodelibs-crypto@0.1.0",
      "evp_bytestokey": "npm:evp_bytestokey@1.0.0",
      "fs": "github:jspm/nodelibs-fs@0.1.2",
      "inherits": "npm:inherits@2.0.1",
      "systemjs-json": "github:systemjs/plugin-json@0.1.2"
    },
    "npm:browserify-cipher@1.0.0": {
      "browserify-aes": "npm:browserify-aes@1.0.6",
      "browserify-des": "npm:browserify-des@1.0.0",
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "crypto": "github:jspm/nodelibs-crypto@0.1.0",
      "evp_bytestokey": "npm:evp_bytestokey@1.0.0"
    },
    "npm:browserify-des@1.0.0": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "cipher-base": "npm:cipher-base@1.0.3",
      "crypto": "github:jspm/nodelibs-crypto@0.1.0",
      "des.js": "npm:des.js@1.0.0",
      "inherits": "npm:inherits@2.0.1"
    },
    "npm:browserify-rsa@4.0.1": {
      "bn.js": "npm:bn.js@4.11.6",
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "constants": "github:jspm/nodelibs-constants@0.1.0",
      "crypto": "github:jspm/nodelibs-crypto@0.1.0",
      "randombytes": "npm:randombytes@2.0.3"
    },
    "npm:browserify-sign@4.0.0": {
      "bn.js": "npm:bn.js@4.11.6",
      "browserify-rsa": "npm:browserify-rsa@4.0.1",
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "create-hash": "npm:create-hash@1.1.2",
      "create-hmac": "npm:create-hmac@1.1.4",
      "crypto": "github:jspm/nodelibs-crypto@0.1.0",
      "elliptic": "npm:elliptic@6.4.0",
      "inherits": "npm:inherits@2.0.1",
      "parse-asn1": "npm:parse-asn1@5.0.0",
      "stream": "github:jspm/nodelibs-stream@0.1.0"
    },
    "npm:browserify-zlib@0.1.4": {
      "assert": "github:jspm/nodelibs-assert@0.1.0",
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "pako": "npm:pako@0.2.9",
      "process": "github:jspm/nodelibs-process@0.1.2",
      "readable-stream": "npm:readable-stream@2.2.3",
      "util": "github:jspm/nodelibs-util@0.1.0"
    },
    "npm:buffer-shims@1.0.0": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0"
    },
    "npm:buffer-xor@1.0.3": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "systemjs-json": "github:systemjs/plugin-json@0.1.2"
    },
    "npm:buffer@3.6.0": {
      "base64-js": "npm:base64-js@0.0.8",
      "child_process": "github:jspm/nodelibs-child_process@0.1.0",
      "fs": "github:jspm/nodelibs-fs@0.1.2",
      "ieee754": "npm:ieee754@1.1.8",
      "isarray": "npm:isarray@1.0.0",
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:bufferutil@2.0.1": {
      "bindings": "npm:bindings@1.2.1",
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "nan": "npm:nan@2.5.1",
      "prebuild-install": "npm:prebuild-install@2.1.0"
    },
    "npm:chownr@1.0.1": {
      "fs": "github:jspm/nodelibs-fs@0.1.2",
      "path": "github:jspm/nodelibs-path@0.1.0"
    },
    "npm:cipher-base@1.0.3": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "inherits": "npm:inherits@2.0.1",
      "stream": "github:jspm/nodelibs-stream@0.1.0",
      "string_decoder": "github:jspm/nodelibs-string_decoder@0.1.0"
    },
    "npm:constants-browserify@0.0.1": {
      "systemjs-json": "github:systemjs/plugin-json@0.1.2"
    },
    "npm:core-js@1.2.7": {
      "fs": "github:jspm/nodelibs-fs@0.1.2",
      "path": "github:jspm/nodelibs-path@0.1.0",
      "process": "github:jspm/nodelibs-process@0.1.2",
      "systemjs-json": "github:systemjs/plugin-json@0.1.2"
    },
    "npm:core-util-is@1.0.2": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0"
    },
    "npm:create-ecdh@4.0.0": {
      "bn.js": "npm:bn.js@4.11.6",
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "crypto": "github:jspm/nodelibs-crypto@0.1.0",
      "elliptic": "npm:elliptic@6.4.0"
    },
    "npm:create-hash@1.1.2": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "cipher-base": "npm:cipher-base@1.0.3",
      "crypto": "github:jspm/nodelibs-crypto@0.1.0",
      "fs": "github:jspm/nodelibs-fs@0.1.2",
      "inherits": "npm:inherits@2.0.1",
      "ripemd160": "npm:ripemd160@1.0.1",
      "sha.js": "npm:sha.js@2.4.8"
    },
    "npm:create-hmac@1.1.4": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "create-hash": "npm:create-hash@1.1.2",
      "crypto": "github:jspm/nodelibs-crypto@0.1.0",
      "inherits": "npm:inherits@2.0.1",
      "stream": "github:jspm/nodelibs-stream@0.1.0"
    },
    "npm:crypto-browserify@3.11.0": {
      "browserify-cipher": "npm:browserify-cipher@1.0.0",
      "browserify-sign": "npm:browserify-sign@4.0.0",
      "create-ecdh": "npm:create-ecdh@4.0.0",
      "create-hash": "npm:create-hash@1.1.2",
      "create-hmac": "npm:create-hmac@1.1.4",
      "diffie-hellman": "npm:diffie-hellman@5.0.2",
      "inherits": "npm:inherits@2.0.1",
      "pbkdf2": "npm:pbkdf2@3.0.9",
      "public-encrypt": "npm:public-encrypt@4.0.0",
      "randombytes": "npm:randombytes@2.0.3"
    },
    "npm:crypto-js@3.1.9-1": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:deep-extend@0.4.1": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0"
    },
    "npm:des.js@1.0.0": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "inherits": "npm:inherits@2.0.1",
      "minimalistic-assert": "npm:minimalistic-assert@1.0.0"
    },
    "npm:diffie-hellman@5.0.2": {
      "bn.js": "npm:bn.js@4.11.6",
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "crypto": "github:jspm/nodelibs-crypto@0.1.0",
      "miller-rabin": "npm:miller-rabin@4.0.0",
      "randombytes": "npm:randombytes@2.0.3",
      "systemjs-json": "github:systemjs/plugin-json@0.1.2"
    },
    "npm:elliptic@6.4.0": {
      "bn.js": "npm:bn.js@4.11.6",
      "brorand": "npm:brorand@1.1.0",
      "hash.js": "npm:hash.js@1.0.3",
      "hmac-drbg": "npm:hmac-drbg@1.0.0",
      "inherits": "npm:inherits@2.0.1",
      "minimalistic-assert": "npm:minimalistic-assert@1.0.0",
      "minimalistic-crypto-utils": "npm:minimalistic-crypto-utils@1.0.1",
      "systemjs-json": "github:systemjs/plugin-json@0.1.2"
    },
    "npm:end-of-stream@1.1.0": {
      "assert": "github:jspm/nodelibs-assert@0.1.0",
      "child_process": "github:jspm/nodelibs-child_process@0.1.0",
      "fs": "github:jspm/nodelibs-fs@0.1.2",
      "net": "github:jspm/nodelibs-net@0.1.2",
      "once": "npm:once@1.3.3",
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:evp_bytestokey@1.0.0": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "create-hash": "npm:create-hash@1.1.2",
      "crypto": "github:jspm/nodelibs-crypto@0.1.0"
    },
    "npm:font-awesome@4.7.0": {
      "css": "github:systemjs/plugin-css@0.1.32"
    },
    "npm:gauge@2.7.3": {
      "aproba": "npm:aproba@1.1.1",
      "console-control-strings": "npm:console-control-strings@1.1.0",
      "has-unicode": "npm:has-unicode@2.0.1",
      "object-assign": "npm:object-assign@4.1.1",
      "process": "github:jspm/nodelibs-process@0.1.2",
      "signal-exit": "npm:signal-exit@3.0.2",
      "string-width": "npm:string-width@1.0.2",
      "strip-ansi": "npm:strip-ansi@3.0.1",
      "util": "github:jspm/nodelibs-util@0.1.0",
      "wide-align": "npm:wide-align@1.1.0"
    },
    "npm:github-from-package@0.0.0": {
      "systemjs-json": "github:systemjs/plugin-json@0.1.2"
    },
    "npm:has-unicode@2.0.1": {
      "os": "github:jspm/nodelibs-os@0.1.0",
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:hash.js@1.0.3": {
      "inherits": "npm:inherits@2.0.1"
    },
    "npm:hmac-drbg@1.0.0": {
      "hash.js": "npm:hash.js@1.0.3",
      "minimalistic-assert": "npm:minimalistic-assert@1.0.0",
      "minimalistic-crypto-utils": "npm:minimalistic-crypto-utils@1.0.1",
      "systemjs-json": "github:systemjs/plugin-json@0.1.2"
    },
    "npm:https-browserify@0.0.0": {
      "http": "github:jspm/nodelibs-http@1.7.1"
    },
    "npm:inherits@2.0.1": {
      "util": "github:jspm/nodelibs-util@0.1.0"
    },
    "npm:ini@1.3.4": {
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:int64-buffer@0.1.9": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0"
    },
    "npm:is-fullwidth-code-point@1.0.0": {
      "number-is-nan": "npm:number-is-nan@1.0.1"
    },
    "npm:miller-rabin@4.0.0": {
      "bn.js": "npm:bn.js@4.11.6",
      "brorand": "npm:brorand@1.1.0"
    },
    "npm:mkdirp@0.5.1": {
      "fs": "github:jspm/nodelibs-fs@0.1.2",
      "minimist": "npm:minimist@0.0.8",
      "path": "github:jspm/nodelibs-path@0.1.0",
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:msgpack-lite@0.1.26": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "event-lite": "npm:event-lite@0.1.1",
      "fs": "github:jspm/nodelibs-fs@0.1.2",
      "ieee754": "npm:ieee754@1.1.8",
      "int64-buffer": "npm:int64-buffer@0.1.9",
      "isarray": "npm:isarray@1.0.0",
      "process": "github:jspm/nodelibs-process@0.1.2",
      "stream": "github:jspm/nodelibs-stream@0.1.0",
      "systemjs-json": "github:systemjs/plugin-json@0.1.2",
      "util": "github:jspm/nodelibs-util@0.1.0"
    },
    "npm:nan@2.5.1": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "fs": "github:jspm/nodelibs-fs@0.1.2",
      "path": "github:jspm/nodelibs-path@0.1.0",
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:node-abi@1.3.3": {
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:npmlog@4.0.2": {
      "are-we-there-yet": "npm:are-we-there-yet@1.1.2",
      "console-control-strings": "npm:console-control-strings@1.1.0",
      "events": "github:jspm/nodelibs-events@0.1.1",
      "gauge": "npm:gauge@2.7.3",
      "process": "github:jspm/nodelibs-process@0.1.2",
      "set-blocking": "npm:set-blocking@2.0.0",
      "util": "github:jspm/nodelibs-util@0.1.0"
    },
    "npm:once@1.3.3": {
      "wrappy": "npm:wrappy@1.0.2"
    },
    "npm:os-browserify@0.1.2": {
      "os": "github:jspm/nodelibs-os@0.1.0"
    },
    "npm:os-homedir@1.0.2": {
      "os": "github:jspm/nodelibs-os@0.1.0",
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:pako@0.2.9": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:parse-asn1@5.0.0": {
      "asn1.js": "npm:asn1.js@4.9.1",
      "browserify-aes": "npm:browserify-aes@1.0.6",
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "create-hash": "npm:create-hash@1.1.2",
      "evp_bytestokey": "npm:evp_bytestokey@1.0.0",
      "pbkdf2": "npm:pbkdf2@3.0.9",
      "systemjs-json": "github:systemjs/plugin-json@0.1.2"
    },
    "npm:path-browserify@0.0.0": {
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:pbkdf2@3.0.9": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "create-hmac": "npm:create-hmac@1.1.4",
      "crypto": "github:jspm/nodelibs-crypto@0.1.0",
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:prebuild-install@2.1.0": {
      "expand-template": "npm:expand-template@1.0.3",
      "fs": "github:jspm/nodelibs-fs@0.1.2",
      "github-from-package": "npm:github-from-package@0.0.0",
      "minimist": "npm:minimist@1.2.0",
      "node-abi": "npm:node-abi@1.3.3",
      "noop-logger": "npm:noop-logger@0.1.1",
      "npmlog": "npm:npmlog@4.0.2",
      "os-homedir": "npm:os-homedir@1.0.2",
      "path": "github:jspm/nodelibs-path@0.1.0",
      "process": "github:jspm/nodelibs-process@0.1.2",
      "pump": "npm:pump@1.0.2",
      "rc": "npm:rc@1.1.7",
      "simple-get": "npm:simple-get@1.4.3",
      "systemjs-json": "github:systemjs/plugin-json@0.1.2",
      "tar-fs": "npm:tar-fs@1.15.1",
      "tunnel-agent": "npm:tunnel-agent@0.4.3",
      "url": "github:jspm/nodelibs-url@0.1.0",
      "xtend": "npm:xtend@4.0.1",
      "zlib": "github:jspm/nodelibs-zlib@0.1.0"
    },
    "npm:process-nextick-args@1.0.7": {
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:process@0.11.9": {
      "assert": "github:jspm/nodelibs-assert@0.1.0",
      "fs": "github:jspm/nodelibs-fs@0.1.2",
      "vm": "github:jspm/nodelibs-vm@0.1.0"
    },
    "npm:public-encrypt@4.0.0": {
      "bn.js": "npm:bn.js@4.11.6",
      "browserify-rsa": "npm:browserify-rsa@4.0.1",
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "create-hash": "npm:create-hash@1.1.2",
      "crypto": "github:jspm/nodelibs-crypto@0.1.0",
      "parse-asn1": "npm:parse-asn1@5.0.0",
      "randombytes": "npm:randombytes@2.0.3"
    },
    "npm:pump@1.0.2": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "end-of-stream": "npm:end-of-stream@1.1.0",
      "once": "npm:once@1.3.3",
      "process": "github:jspm/nodelibs-process@0.1.2",
      "stream": "github:jspm/nodelibs-stream@0.1.0"
    },
    "npm:punycode@1.3.2": {
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:randombytes@2.0.3": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "crypto": "github:jspm/nodelibs-crypto@0.1.0",
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:rc@1.1.7": {
      "deep-extend": "npm:deep-extend@0.4.1",
      "fs": "github:jspm/nodelibs-fs@0.1.2",
      "ini": "npm:ini@1.3.4",
      "minimist": "npm:minimist@1.2.0",
      "path": "github:jspm/nodelibs-path@0.1.0",
      "process": "github:jspm/nodelibs-process@0.1.2",
      "strip-json-comments": "npm:strip-json-comments@2.0.1"
    },
    "npm:readable-stream@1.1.14": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "core-util-is": "npm:core-util-is@1.0.2",
      "events": "github:jspm/nodelibs-events@0.1.1",
      "inherits": "npm:inherits@2.0.1",
      "isarray": "npm:isarray@0.0.1",
      "process": "github:jspm/nodelibs-process@0.1.2",
      "stream-browserify": "npm:stream-browserify@1.0.0",
      "string_decoder": "npm:string_decoder@0.10.31"
    },
    "npm:readable-stream@2.2.3": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "buffer-shims": "npm:buffer-shims@1.0.0",
      "core-util-is": "npm:core-util-is@1.0.2",
      "events": "github:jspm/nodelibs-events@0.1.1",
      "inherits": "npm:inherits@2.0.1",
      "isarray": "npm:isarray@1.0.0",
      "process": "github:jspm/nodelibs-process@0.1.2",
      "process-nextick-args": "npm:process-nextick-args@1.0.7",
      "string_decoder": "npm:string_decoder@0.10.31",
      "util-deprecate": "npm:util-deprecate@1.0.2"
    },
    "npm:ripemd160@1.0.1": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:set-blocking@2.0.0": {
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:sha.js@2.4.8": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "fs": "github:jspm/nodelibs-fs@0.1.2",
      "inherits": "npm:inherits@2.0.1",
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:signal-exit@3.0.2": {
      "assert": "github:jspm/nodelibs-assert@0.1.0",
      "events": "github:jspm/nodelibs-events@0.1.1",
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:simple-get@1.4.3": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "http": "github:jspm/nodelibs-http@1.7.1",
      "https": "github:jspm/nodelibs-https@0.1.0",
      "once": "npm:once@1.3.3",
      "url": "github:jspm/nodelibs-url@0.1.0",
      "xtend": "npm:xtend@4.0.1"
    },
    "npm:stream-browserify@1.0.0": {
      "events": "github:jspm/nodelibs-events@0.1.1",
      "inherits": "npm:inherits@2.0.1",
      "readable-stream": "npm:readable-stream@1.1.14"
    },
    "npm:string-width@1.0.2": {
      "code-point-at": "npm:code-point-at@1.1.0",
      "is-fullwidth-code-point": "npm:is-fullwidth-code-point@1.0.0",
      "strip-ansi": "npm:strip-ansi@3.0.1"
    },
    "npm:string_decoder@0.10.31": {
      "buffer": "github:jspm/nodelibs-buffer@0.1.0"
    },
    "npm:strip-ansi@3.0.1": {
      "ansi-regex": "npm:ansi-regex@2.1.1"
    },
    "npm:tar-fs@1.15.1": {
      "chownr": "npm:chownr@1.0.1",
      "fs": "github:jspm/nodelibs-fs@0.1.2",
      "mkdirp": "npm:mkdirp@0.5.1",
      "os": "github:jspm/nodelibs-os@0.1.0",
      "path": "github:jspm/nodelibs-path@0.1.0",
      "process": "github:jspm/nodelibs-process@0.1.2",
      "pump": "npm:pump@1.0.2",
      "tar-stream": "npm:tar-stream@1.5.2"
    },
    "npm:tar-stream@1.5.2": {
      "bl": "npm:bl@1.2.0",
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "constants": "github:jspm/nodelibs-constants@0.1.0",
      "end-of-stream": "npm:end-of-stream@1.1.0",
      "process": "github:jspm/nodelibs-process@0.1.2",
      "readable-stream": "npm:readable-stream@2.2.3",
      "string_decoder": "github:jspm/nodelibs-string_decoder@0.1.0",
      "util": "github:jspm/nodelibs-util@0.1.0",
      "xtend": "npm:xtend@4.0.1"
    },
    "npm:timers-browserify@1.4.2": {
      "process": "npm:process@0.11.9"
    },
    "npm:tunnel-agent@0.4.3": {
      "assert": "github:jspm/nodelibs-assert@0.1.0",
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "events": "github:jspm/nodelibs-events@0.1.1",
      "http": "github:jspm/nodelibs-http@1.7.1",
      "https": "github:jspm/nodelibs-https@0.1.0",
      "net": "github:jspm/nodelibs-net@0.1.2",
      "process": "github:jspm/nodelibs-process@0.1.2",
      "tls": "github:jspm/nodelibs-tls@0.1.0",
      "util": "github:jspm/nodelibs-util@0.1.0"
    },
    "npm:url@0.10.3": {
      "assert": "github:jspm/nodelibs-assert@0.1.0",
      "punycode": "npm:punycode@1.3.2",
      "querystring": "npm:querystring@0.2.0",
      "util": "github:jspm/nodelibs-util@0.1.0"
    },
    "npm:utf-8-validate@3.0.1": {
      "bindings": "npm:bindings@1.2.1",
      "buffer": "github:jspm/nodelibs-buffer@0.1.0",
      "nan": "npm:nan@2.5.1",
      "prebuild-install": "npm:prebuild-install@2.1.0"
    },
    "npm:util-deprecate@1.0.2": {
      "util": "github:jspm/nodelibs-util@0.1.0"
    },
    "npm:util@0.10.3": {
      "inherits": "npm:inherits@2.0.1",
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:vm-browserify@0.0.4": {
      "indexof": "npm:indexof@0.0.1"
    },
    "npm:when@3.7.8": {
      "child_process": "github:jspm/nodelibs-child_process@0.1.0",
      "fs": "github:jspm/nodelibs-fs@0.1.2",
      "path": "github:jspm/nodelibs-path@0.1.0",
      "process": "github:jspm/nodelibs-process@0.1.2"
    },
    "npm:wide-align@1.1.0": {
      "string-width": "npm:string-width@1.0.2"
    }
  }
});
