#!/bin/bash
# Workshop Screenshot Capture Script
# Usage: bash ~/development/langfuse-workshop/take_screenshots.sh
# Captures browser screenshots and copies them into the right lab assets/ dirs.

PROJECT_URL="https://us.cloud.langfuse.com/project/cmnsq6jcs000yad07f1j3xi1x"
DELAY=4        # seconds to wait for page to load
TRACE_ID="56dac2b96254b24b97629fb303729f1a"

# Workspace folder (the langfuse-workshop repo root)
WORKSPACE="$HOME/development/langfuse-workshop"

# Temp staging dir on Desktop (always writable by the logged-in user)
STAGING="$HOME/Desktop/langfuse-screenshots"
mkdir -p "$STAGING"

echo "🔍 Workshop Screenshot Capture"
echo "Staging screenshots in: $STAGING"
echo "Will copy into: $WORKSPACE/labs/*/assets/"
echo ""

# Helper: open URL → wait → full-screen capture → save to staging
capture() {
  local url="$1"
  local filename="$2"
  local label="$3"

  echo "📸 $label"
  open -a "Google Chrome" "$url"
  sleep $DELAY
  osascript -e 'tell application "Google Chrome" to activate'
  sleep 0.5
  screencapture -x "$STAGING/$filename"
  echo "   → $STAGING/$filename"
  sleep 0.5
}

# ── LAB 05 ────────────────────────────────────────────────────────────
echo "=== Lab 05: Online Evals ==="
capture "$PROJECT_URL/traces/$TRACE_ID" \
  "langfuse-trace-with-scores.png" \
  "Trace with user-feedback + llm-judge-quality scores"

capture "$PROJECT_URL/scores" \
  "langfuse-scores-list.png" \
  "Scores list page"

capture "$PROJECT_URL/evals" \
  "langfuse-llm-evaluators.png" \
  "LLM-as-a-Judge evaluators"

capture "$PROJECT_URL/settings/llm-connections" \
  "langfuse-llm-connections.png" \
  "LLM Connections settings"

# ── LAB 06 ────────────────────────────────────────────────────────────
echo ""
echo "=== Lab 06: Human Annotation ==="
capture "$PROJECT_URL/settings/scores" \
  "langfuse-score-configs.png" \
  "Score Configs settings"

capture "$PROJECT_URL/annotation-queues" \
  "langfuse-annotation-queues.png" \
  "Annotation Queues list"

capture "$PROJECT_URL/traces/$TRACE_ID" \
  "langfuse-trace-annotate.png" \
  "Trace with Annotate button"

# ── LAB 07 ────────────────────────────────────────────────────────────
echo ""
echo "=== Lab 07: Offline Evals ==="
capture "$PROJECT_URL/datasets" \
  "langfuse-datasets-list.png" \
  "Datasets list"

capture "$PROJECT_URL/datasets/datastream-support-benchmark" \
  "langfuse-dataset-items.png" \
  "Dataset items"

capture "$PROJECT_URL/datasets/datastream-support-benchmark?tab=runs" \
  "langfuse-experiment-runs.png" \
  "Experiment runs comparison"

# ── COPY TO WORKSPACE ─────────────────────────────────────────────────
echo ""
echo "📂 Copying screenshots to workspace..."

copy_if_exists() {
  local src="$STAGING/$1"
  local dest="$2"
  if [ -f "$src" ]; then
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    echo "   ✅ $1 → $dest"
  else
    echo "   ⚠️  Missing: $1 (screencapture may have failed)"
  fi
}

copy_if_exists "langfuse-trace-with-scores.png"  "$WORKSPACE/labs/05-online-evals/assets/langfuse-trace-with-scores.png"
copy_if_exists "langfuse-scores-list.png"         "$WORKSPACE/labs/05-online-evals/assets/langfuse-scores-list.png"
copy_if_exists "langfuse-llm-evaluators.png"      "$WORKSPACE/labs/05-online-evals/assets/langfuse-llm-evaluators.png"
copy_if_exists "langfuse-llm-connections.png"     "$WORKSPACE/labs/05-online-evals/assets/langfuse-llm-connections.png"

copy_if_exists "langfuse-score-configs.png"       "$WORKSPACE/labs/06-human-annotation/assets/langfuse-score-configs.png"
copy_if_exists "langfuse-annotation-queues.png"   "$WORKSPACE/labs/06-human-annotation/assets/langfuse-annotation-queues.png"
copy_if_exists "langfuse-trace-annotate.png"      "$WORKSPACE/labs/06-human-annotation/assets/langfuse-trace-annotate.png"

copy_if_exists "langfuse-datasets-list.png"       "$WORKSPACE/labs/07-offline-evals/assets/langfuse-datasets-list.png"
copy_if_exists "langfuse-dataset-items.png"       "$WORKSPACE/labs/07-offline-evals/assets/langfuse-dataset-items.png"
copy_if_exists "langfuse-experiment-runs.png"     "$WORKSPACE/labs/07-offline-evals/assets/langfuse-experiment-runs.png"

echo ""
echo "✅ Done! Screenshots in $WORKSPACE/labs/*/assets/"
echo "   Staging files kept at $STAGING (delete when done)"
