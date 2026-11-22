#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUTPUT_DIR="$ROOT_DIR/assets/downloads"
API_KEY=${COVERR_API_KEY:-}

if [ -z "$API_KEY" ] && [ -f "$ROOT_DIR/.env" ]; then
  API_KEY=$(sed -n 's/^COVERR_API_KEY=//p' "$ROOT_DIR/.env" | head -n 1)
fi

API_KEY=${API_KEY#\"}
API_KEY=${API_KEY%\"}

if [ -z "$API_KEY" ]; then
  echo "COVERR_API_KEY is not configured." >&2
  exit 1
fi

KEYWORD=${1:-}
if [ -z "$KEYWORD" ]; then
  printf '영상 키워드: ' >&2
  IFS= read -r KEYWORD
fi

if [ -z "$KEYWORD" ]; then
  echo "A search keyword is required." >&2
  exit 1
fi

RESPONSE_FILE=$(mktemp)
trap 'rm -f "$RESPONSE_FILE"' EXIT

curl -fsS -H "x-api-key: $API_KEY" --get \
  --data-urlencode "query=$KEYWORD" \
  --data "page_size=20" \
  --data "urls=true" \
  "https://api.coverr.co/videos" > "$RESPONSE_FILE"

SELECTION=$(python3 - "$RESPONSE_FILE" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as response:
    hits = json.load(response).get("hits", [])

vertical = [
    video for video in hits
    if video.get("is_vertical") and video.get("urls", {}).get("mp4_download")
]
video = next((item for item in vertical if 15 <= item.get("duration", 0) <= 20), None)
video = video or next(iter(vertical), None)

if not video:
    raise SystemExit("No downloadable vertical Coverr video found.")

print(video["id"])
print(video["urls"]["mp4_download"])
PY
)

VIDEO_ID=$(printf '%s\n' "$SELECTION" | sed -n '1p')
DOWNLOAD_URL=$(printf '%s\n' "$SELECTION" | sed -n '2p')
mkdir -p "$OUTPUT_DIR"
OUTPUT_PATH=$(mktemp "$OUTPUT_DIR/coverr-${VIDEO_ID}.XXXXXX.mp4")

if ! curl -fL --retry 2 "$DOWNLOAD_URL" -o "$OUTPUT_PATH"; then
  rm -f "$OUTPUT_PATH"
  exit 1
fi

if [ ! -s "$OUTPUT_PATH" ]; then
  rm -f "$OUTPUT_PATH"
  echo "Coverr returned an empty video file." >&2
  exit 1
fi

printf '%s\n' "$OUTPUT_PATH"
