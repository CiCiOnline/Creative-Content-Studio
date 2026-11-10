#!/usr/bin/env bash
# Reinstall the studio toolchain on a fresh machine / cloud session.
set -e
cd "$(dirname "$0")"
apt-get install -y -qq libegl1 libgles2 >/dev/null 2>&1 || (apt-get update -qq && apt-get install -y -qq libegl1 libgles2)
pip install -q faster-whisper mediapipe opencv-python-headless "av>=14" fal-client
[ -f models/selfie_multiclass.tflite ] || curl -sSL -o models/selfie_multiclass.tflite \
  https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite
(cd engine && npm install --silent)
echo "studio ready"
