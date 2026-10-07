#!/bin/sh
# v2 uses exactly the same narration (cloned voice) and timing as ../adaptive-diagnosis.
# After changing the script there (tools/make_audio.py → timeline.js, audio/mix.wav), copy both here:
cd "$(dirname "$0")/.." && cp ../adaptive-diagnosis/timeline.js . && mkdir -p audio && cp ../adaptive-diagnosis/audio/mix.wav audio/ && echo "synced narration + timeline from ../adaptive-diagnosis"
