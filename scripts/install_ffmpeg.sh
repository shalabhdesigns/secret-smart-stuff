#!/usr/bin/env bash
# Install ffmpeg on the runner without ever hanging the job: apt (time-limited), then static builds from two sources.
# 18 Nov 2026: Ubuntu's mirrors timed out and johnvansickle.com served a non-archive, so two runs died here.
set -u
command -v ffmpeg >/dev/null && exit 0
if timeout 300 sudo apt-get install -y -qq ffmpeg >/dev/null 2>&1; then command -v ffmpeg >/dev/null && exit 0; fi
for i in 1 2; do
  if timeout 240 sudo apt-get update -qq -o Acquire::Retries=2 && timeout 300 sudo apt-get install -y -qq ffmpeg >/dev/null; then
    command -v ffmpeg >/dev/null && exit 0
  fi
  echo "apt attempt $i failed or timed out"
done
echo "falling back to a static ffmpeg build"
cd /tmp
if curl -fsSL --retry 3 -o ff.tar.xz https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz \
   && tar -xf ff.tar.xz && sudo cp ffmpeg-master-latest-linux64-gpl/bin/ffmpeg ffmpeg-master-latest-linux64-gpl/bin/ffprobe /usr/local/bin/; then
  ffmpeg -version | head -1 && exit 0
fi
rm -f ff.tar.xz
curl -fsSL --retry 3 -o ff.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
  && tar -xf ff.tar.xz && sudo cp ffmpeg-*-static/ffmpeg ffmpeg-*-static/ffprobe /usr/local/bin/ && ffmpeg -version | head -1
