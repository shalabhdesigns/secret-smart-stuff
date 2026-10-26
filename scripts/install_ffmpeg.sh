#!/usr/bin/env bash
# Install ffmpeg on the runner without ever hanging the job: apt with a time limit (twice), then a static build.
set -u
command -v ffmpeg >/dev/null && exit 0
for i in 1 2; do
  if timeout 240 sudo apt-get update -qq -o Acquire::Retries=2 && timeout 300 sudo apt-get install -y -qq ffmpeg >/dev/null; then
    command -v ffmpeg >/dev/null && exit 0
  fi
  echo "apt attempt $i failed or timed out"
done
echo "falling back to a static ffmpeg build"
cd /tmp && curl -fsSL --retry 3 -o ff.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
  && tar -xf ff.tar.xz && sudo cp ffmpeg-*-static/ffmpeg ffmpeg-*-static/ffprobe /usr/local/bin/ && ffmpeg -version | head -1
