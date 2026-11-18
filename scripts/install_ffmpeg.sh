#!/usr/bin/env bash
# Install ffmpeg on the runner without ever hanging the job.
# 18 Nov 2026: Ubuntu's mirrors timed out for hours (the step hit its 15-minute limit) and johnvansickle.com served a
# non-archive. Order now: BtbN's static build from GitHub (fast and reliable from Actions), then apt, then johnvansickle.
set -u
command -v ffmpeg >/dev/null && exit 0
cd /tmp
if timeout 180 curl -fsSL --retry 3 -o ff.tar.xz https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz \
   && tar -xf ff.tar.xz && sudo cp ffmpeg-master-latest-linux64-gpl/bin/ffmpeg ffmpeg-master-latest-linux64-gpl/bin/ffprobe /usr/local/bin/; then
  ffmpeg -version | head -1 && exit 0
fi
echo "static build failed; trying apt"
rm -rf ff.tar.xz ffmpeg-master-latest-linux64-gpl
if timeout 120 sudo apt-get install -y -qq ffmpeg >/dev/null 2>&1 \
   || { timeout 150 sudo apt-get update -qq -o Acquire::Retries=1 && timeout 240 sudo apt-get install -y -qq ffmpeg >/dev/null; }; then
  command -v ffmpeg >/dev/null && exit 0
fi
echo "apt failed; trying johnvansickle"
timeout 180 curl -fsSL --retry 3 -o ff.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
  && tar -xf ff.tar.xz && sudo cp ffmpeg-*-static/ffmpeg ffmpeg-*-static/ffprobe /usr/local/bin/ && ffmpeg -version | head -1
