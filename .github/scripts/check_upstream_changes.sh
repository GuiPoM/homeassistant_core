#!/bin/bash
# Manual script to check for upstream changes in google_assistant component

set -e

echo "🔍 Checking for upstream changes in google_assistant component..."
echo ""

# Ensure we're in the right directory
cd "$(dirname "$0")/.." || exit 1

# Fetch latest upstream
echo "📥 Fetching upstream/dev..."
git fetch upstream dev

# Get base commit
BASE_COMMIT=$(git merge-base HEAD upstream/dev)
echo "📌 Base commit: $BASE_COMMIT"
echo ""

# Check for changes
CHANGES=$(git log --oneline "$BASE_COMMIT..upstream/dev" -- homeassistant/components/google_assistant/)

if [ -z "$CHANGES" ]; then
    echo "✅ No changes detected in upstream google_assistant component"
    echo "   Custom component is up to date!"
    exit 0
fi

echo "⚠️  Changes detected in upstream google_assistant component!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Commits:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$CHANGES"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Files changed:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git diff --stat "$BASE_COMMIT..upstream/dev" -- homeassistant/components/google_assistant/
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test changes:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
TEST_CHANGES=$(git log --oneline "$BASE_COMMIT..upstream/dev" -- tests/components/google_assistant/ || echo "No test changes")
echo "$TEST_CHANGES"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Action Required:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Review the detailed diff:"
echo "   git diff $BASE_COMMIT..upstream/dev -- homeassistant/components/google_assistant/"
echo ""
echo "2. Check if changes affect custom features:"
echo "   - require_acknowledgment"
echo "   - require_presence"
echo ""
echo "3. Update custom component if needed"
echo ""
echo "4. Run tests:"
echo "   ./scripts/run_tests.sh"
echo ""
echo "5. Sync to google-assistant-unleashed repository"
echo ""

# Offer to show detailed diff
read -p "Show detailed diff now? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git diff "$BASE_COMMIT..upstream/dev" -- homeassistant/components/google_assistant/ | less
fi
