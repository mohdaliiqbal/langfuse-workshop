#!/bin/bash
# Run this from your Mac terminal to capture real Langfuse screenshots
# Usage: bash ~/development/langfuse-workshop/take_lab_screenshots.sh

PROJECT_ID="cmnsq6jcs000yad07f1j3xi1x"
BASE="https://us.cloud.langfuse.com/project/${PROJECT_ID}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Ensure assets dirs exist and are owned by you
for dir in \
  "${SCRIPT_DIR}/labs/05-online-evals/assets" \
  "${SCRIPT_DIR}/labs/06-human-annotation/assets" \
  "${SCRIPT_DIR}/labs/07-offline-evals/assets"; do
  mkdir -p "$dir"
done

capture() {
  local url="$1"
  local output="$2"
  local wait_sec="${3:-5}"

  echo "→ $(basename "$output")"
  open -a "Google Chrome" "$url"
  sleep "$wait_sec"

  # Get Chrome window bounds via osascript
  local bounds
  bounds=$(osascript <<'APPLESCRIPT'
tell application "System Events"
  tell process "Google Chrome"
    set frontWin to first window
    set {x, y} to position of frontWin
    set {w, h} to size of frontWin
    return (x as string) & " " & (y as string) & " " & (w as string) & " " & (h as string)
  end tell
end tell
APPLESCRIPT
)

  if [ -n "$bounds" ]; then
    read -r x y w h <<< "$bounds"
    screencapture -R "${x},${y},${w},${h}" "$output"
  else
    # Fallback: full screen
    screencapture -x "$output"
  fi
}

# Get dataset name for lab 07 URLs
DATASET_NAME=$(curl -s \
  -u "pk-lf-1f2d078b-c184-440d-ae8e-283cb211569d:sk-lf-1c989c1a-150d-4dc9-81b8-59cac31583be" \
  "https://us.cloud.langfuse.com/api/public/datasets?limit=1" 2>/dev/null | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data'][0]['name'])" 2>/dev/null)
DATASET_NAME="${DATASET_NAME:-datastream-support-benchmark}"

echo "=== Lab 05: Online Evaluations ==="
capture "${BASE}/traces/56dac2b96254b24b97629fb303729f1a?traceTab=scores" \
  "${SCRIPT_DIR}/labs/05-online-evals/assets/langfuse-trace-with-scores.png"

capture "${BASE}/scores" \
  "${SCRIPT_DIR}/labs/05-online-evals/assets/langfuse-scores-list.png"

capture "${BASE}/settings/llm-connections" \
  "${SCRIPT_DIR}/labs/05-online-evals/assets/langfuse-llm-connections.png"

capture "${BASE}/evals/configs" \
  "${SCRIPT_DIR}/labs/05-online-evals/assets/langfuse-llm-evaluators.png"

echo ""
echo "=== Lab 06: Human Annotation ==="
capture "${BASE}/settings/scores" \
  "${SCRIPT_DIR}/labs/06-human-annotation/assets/langfuse-score-configs.png"

capture "${BASE}/traces/56dac2b96254b24b97629fb303729f1a" \
  "${SCRIPT_DIR}/labs/06-human-annotation/assets/langfuse-trace-annotate.png"

capture "${BASE}/annotation-queues" \
  "${SCRIPT_DIR}/labs/06-human-annotation/assets/langfuse-annotation-queues.png"

echo ""
echo "=== Lab 07: Offline Evaluations ==="
capture "${BASE}/datasets" \
  "${SCRIPT_DIR}/labs/07-offline-evals/assets/langfuse-datasets-list.png"

capture "${BASE}/datasets/${DATASET_NAME}" \
  "${SCRIPT_DIR}/labs/07-offline-evals/assets/langfuse-dataset-items.png"

capture "${BASE}/datasets/${DATASET_NAME}/compare" \
  "${SCRIPT_DIR}/labs/07-offline-evals/assets/langfuse-experiment-runs.png"

echo ""
echo "✅ Done! All 10 screenshots saved."
