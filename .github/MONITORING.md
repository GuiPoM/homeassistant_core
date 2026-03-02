# Upstream Monitoring System

This directory contains tools to monitor the official Home Assistant `google_assistant` component for changes that may affect the custom component.

## Overview

The monitoring system helps you stay informed about upstream changes so you can:
- Keep the custom component in sync with official updates
- Identify breaking changes early
- Maintain compatibility with the latest Home Assistant version
- Update custom features when the base component changes

## Components

### 1. GitHub Action (`.github/workflows/monitor-google-assistant.yml`)

**What it does:**
- Runs daily at 6 AM UTC (can also be triggered manually)
- Fetches the latest upstream changes from `home-assistant/core`
- Compares `upstream/dev` with your `integration/google-assistant-unleashed` branch
- Detects changes to `homeassistant/components/google_assistant/`
- Creates a GitHub issue when changes are detected

**Features:**
- Automatic daily checks
- Only creates one issue (won't spam if already open)
- Shows commit list, file changes, and test changes
- Provides action items and review instructions
- Labels issues for easy filtering

**Manual trigger:**
```bash
# Via GitHub UI: Actions tab → Monitor Google Assistant Component Changes → Run workflow
# Or use GitHub CLI:
gh workflow run monitor-google-assistant.yml
```

### 2. Local Check Script (`scripts/check_upstream_changes.sh`)

**What it does:**
- Manually check for upstream changes anytime
- Shows detailed diff and statistics
- Offers to display full diff for immediate review

**Usage:**
```bash
cd /c/SAPDevelop/git/perso/homeassistant_core
./scripts/check_upstream_changes.sh
```

**Output includes:**
- List of commits affecting google_assistant
- Files changed with statistics
- Test file changes
- Action items for review

## Workflow

### When Changes Are Detected

1. **GitHub Action creates an issue** with:
   - List of upstream commits
   - Files changed
   - Test changes
   - Action items checklist

2. **Review the changes:**
   ```bash
   cd /c/SAPDevelop/git/perso/homeassistant_core
   git fetch upstream dev
   BASE_COMMIT=$(git merge-base HEAD upstream/dev)
   git diff $BASE_COMMIT..upstream/dev -- homeassistant/components/google_assistant/
   ```

3. **Assess impact on custom features:**
   - Does it affect `require_acknowledgment` implementation?
   - Does it affect `require_presence` implementation?
   - Are there breaking changes to trait system?
   - Are there new features we should integrate?

4. **Update if needed:**
   - Merge/cherry-pick upstream changes to feature branches
   - Update custom component code
   - Run tests: `pytest tests/components/google_assistant/`
   - Update integration branch
   - Sync to google-assistant-unleashed repository

5. **Close the issue** when sync is complete

### Regular Maintenance

**Weekly:**
- Review any open upstream-changes issues
- Check GitHub Action runs for failures

**Monthly:**
- Manually run the check script
- Review closed issues to track what was synced

**Before Release:**
- Always check for upstream changes
- Verify tests pass with latest base code
- Update version numbers if significant changes

## Customization

### Change Check Frequency

Edit `.github/workflows/monitor-google-assistant.yml`:
```yaml
on:
  schedule:
    - cron: '0 6 * * *'  # Currently daily at 6 AM UTC
    # Change to '0 6 * * 1' for weekly (Monday)
    # Change to '0 6 1 * *' for monthly
```

### Watch Additional Files

Add paths to the workflow:
```bash
git log $BASE_COMMIT..upstream/dev -- \
  homeassistant/components/google_assistant/ \
  homeassistant/helpers/trait.py \
  homeassistant/components/webhook/
```

### Notification Channels

To get notified:
- **GitHub**: Watch the repository and enable issue notifications
- **Email**: Configure GitHub notification settings
- **Slack/Discord**: Use GitHub webhooks or integrations

## Troubleshooting

### Action fails with "remote upstream not found"
The workflow adds the remote automatically, but if it fails:
```bash
git remote add upstream https://github.com/home-assistant/core.git
git fetch upstream
```

### No changes detected but you know there are changes
Check if your base branch is up to date:
```bash
git fetch upstream dev
git log HEAD..upstream/dev -- homeassistant/components/google_assistant/
```

### Issue not created
- Check if an issue with labels `upstream-changes` and `google-assistant` is already open
- Check GitHub Actions logs for errors
- Verify repository has Issues enabled

## Testing the Workflow

Test locally before pushing:
```bash
# Simulate the workflow logic
cd /c/SAPDevelop/git/perso/homeassistant_core
git fetch upstream dev
BASE_COMMIT=$(git merge-base HEAD upstream/dev)
CHANGES=$(git log --oneline $BASE_COMMIT..upstream/dev -- homeassistant/components/google_assistant/)

if [ -n "$CHANGES" ]; then
  echo "Changes detected:"
  echo "$CHANGES"
else
  echo "No changes"
fi
```

## Integration with Development Workflow

This monitoring system complements your existing workflow:
```
upstream/dev (home-assistant/core)
    ↓ [monitor daily]
    ↓
integration/google-assistant-unleashed (your fork)
    ↓ [sync when needed]
    ↓
google-assistant-unleashed (custom component repo)
    ↓ [release]
    ↓
HACS (user installations)
```

## Links

- **Upstream Repository**: https://github.com/home-assistant/core
- **Your Fork**: https://github.com/GuiPoM/homeassistant_core
- **Custom Component**: https://github.com/GuiPoM/google-assistant-unleashed
- **Component Path**: `homeassistant/components/google_assistant/`
- **Test Path**: `tests/components/google_assistant/`
