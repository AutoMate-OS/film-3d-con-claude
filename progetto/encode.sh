#!/usr/bin/env bash
# Cuce i 360 fotogrammi di Blender e la colonna sonora nel film finale.
cd "$(dirname "$0")"
ffmpeg -y -v error -framerate 30 -i renders/full/f_%04d.png -i sound.wav \
  -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p -c:a aac -b:a 256k -shortest -movflags +faststart film.mp4
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 film.mp4)
s=$(du -m film.mp4 | cut -f1)
printf '✓ film.mp4 · %.1f s · 1080x1920 · %s MB\n' "$d" "$s"
