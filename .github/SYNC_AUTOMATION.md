# Complete Sync Automation

This document explains the automated workflow that keeps all branches synchronized.

## Overview

The `sync-google-assistant-branches.yml` workflow automates the complete sync pipeline:

```
upstream/dev (Home Assistant)
    ↓ (1. sync)
fork/dev
    ↓ (2. rebase)
feature/require-acknowledgment  +  feature/location-restriction
    ↓ (3. rebuild by merging features)
integration/google-assistant-unleashed
    ↓ (4. sync files)
google-assistant-unleashed (custom component)
```

## The Pipeline

### Step 1: Sync Dev Branch
- **Action**: `git reset --hard upstream/dev`
- **Purpose**: Keep fork's dev branch identical to Home Assistant's dev
- **Result**: Fork's dev is always up-to-date, PRs show correct commit counts

### Step 2: Rebase Feature Branches
- **Branches**: `feature/require-acknowledgment` and `feature/location-restriction`
- **Action**: `git rebase upstream/dev` for each feature
- **Purpose**: Keep PRs clean, showing only feature commits
- **Result**: PR #1 shows 1 commit, PR #2 shows 3 commits (no upstream merge commits)

### Step 3: Rebuild Integration Branch
- **Action**:
  1. Reset integration branch to `upstream/dev`
  2. Merge `feature/require-acknowledgment` (no-ff)
  3. Merge `feature/location-restriction` (no-ff, auto-resolve conflicts)
- **Purpose**: Combine both features on top of latest Home Assistant
- **Result**: PR #6 shows ~6 commits (2 merges + 4 features)

### Step 4: Sync to Custom Component
- **Action**: Copy files from integration branch to custom component repo
- **Purpose**: Distribute combined features to users via HACS
- **Result**: Custom component has latest code with single commit timestamp

## Running the Workflow

### Via GitHub Actions UI

1. Go to: https://github.com/GuiPoM/homeassistant_core/actions/workflows/sync-google-assistant-branches.yml
2. Click "Run workflow"
3. Options:
   - **Sync to custom component**: ✅ (default: yes)
4. Click "Run workflow"
5. Wait 2-3 minutes
6. Check summary for results

### What Gets Updated

When you run this workflow, it updates:

- ✅ `dev` branch (matches upstream)
- ✅ `feature/require-acknowledgment` (rebased on upstream)
- ✅ `feature/location-restriction` (rebased on upstream)
- ✅ `integration/google-assistant-unleashed` (rebuilt from features)
- ✅ `google-assistant-unleashed` custom component (synced from integration)

All with **force pushes** (safe because you're the only one working on these branches).

## When to Run

Run this workflow:

1. **Weekly**: To stay current with Home Assistant development
2. **Before making changes**: To ensure you're working on latest code
3. **After updating features**: When you add commits to feature branches
4. **When monitoring detects changes**: If upstream modifies `google_assistant` component

## What the Workflow Does Automatically

### Conflict Resolution

**Integration Branch Conflicts**: When merging feature branches together, conflicts are auto-resolved by:
- Including both `CONF_REQUIRE_ACK` and `CONF_REQUIRE_PRESENCE` imports
- Including both `check_ack()` and `check_presence()` methods
- Calling both checks in execute methods:
  ```python
  self.check_presence(data)  # Check location first
  self.check_ack(challenge)  # Check acknowledgment second
  ```

**Feature Branch Conflicts**: If a feature branch has conflicts during rebase, the workflow **fails** and requires manual intervention.

### Force Push Safety

All force pushes use `--force-with-lease` which:
- ✅ Prevents overwriting others' work
- ✅ Fails if remote has unexpected changes
- ✅ Safe for solo development

## Verification After Sync

After workflow completes, verify:

1. **PR #1**: Should show **1 commit** ✅
2. **PR #2**: Should show **3 commits** ✅
3. **PR #6**: Should show **~6 commits** ✅
4. **All PRs**: Should show correct file count (~7-15 files)
5. **Custom component**: Should have new commit timestamp

## Manual Sync (Alternative)

If you prefer manual control:

```bash
# 1. Sync dev
git checkout dev
git fetch upstream dev
git reset --hard upstream/dev
git push origin dev --force-with-lease

# 2. Rebase feature branches
git checkout feature/require-acknowledgment
git rebase upstream/dev
git push origin feature/require-acknowledgment --force-with-lease

git checkout feature/location-restriction
git rebase upstream/dev
git push origin feature/location-restriction --force-with-lease

# 3. Rebuild integration
git checkout integration/google-assistant-unleashed
git reset --hard upstream/dev
git merge --no-ff feature/require-acknowledgment -m "Merge feature/require-acknowledgment"
git merge --no-ff feature/location-restriction -m "Merge feature/location-restriction"
# Resolve conflicts manually
git push origin integration/google-assistant-unleashed --force-with-lease

# 4. Sync custom component (see INTEGRATION_WORKFLOW.md)
```

## Troubleshooting

### Workflow Fails on Feature Rebase

**Cause**: Feature branch has conflicts with upstream changes

**Fix**:
1. Rebase manually:
   ```bash
   git checkout feature/location-restriction
   git fetch upstream dev
   git rebase upstream/dev
   # Resolve conflicts
   git push origin feature/location-restriction --force-with-lease
   ```
2. Re-run workflow

### Integration Branch Shows Wrong Commit Count

**Cause**: Dev branch not in sync with upstream

**Solution**: Workflow automatically fixes this in Step 1

### Custom Component Not Updated

**Possible causes**:
- `PAT_CUSTOM_COMPONENT` secret not configured
- No changes detected (files already in sync)

**Check**: Workflow summary shows reason

## Comparison: Old vs New Workflow

### Before (Manual)

```bash
# Update dev
git checkout dev && git pull upstream dev && git push origin dev

# Update feature 1
git checkout feature/require-acknowledgment
git merge upstream/dev  # Creates merge commits ❌
git push origin feature/require-acknowledgment

# Update feature 2
git checkout feature/location-restriction
git merge upstream/dev  # Creates merge commits ❌
git push origin feature/location-restriction

# Update integration (rebase method)
git checkout integration/google-assistant-unleashed
git rebase upstream/dev
# Conflicts ❌ - hard to resolve
git push origin integration/google-assistant-unleashed --force-with-lease

# Result: PRs show 1,000+ commits ❌
```

### After (Automated)

```bash
# One click in GitHub Actions UI ✅
# All branches updated in correct order ✅
# PRs show only feature commits ✅
# Auto-conflict resolution ✅
# Custom component synced ✅
```

## Related Documentation

- [Integration Workflow](INTEGRATION_WORKFLOW.md) - Detailed workflow explanation
- [GitHub Action Setup](GITHUB_ACTION_SETUP.md) - One-time setup for PAT
- [Monitoring](MONITORING.md) - Upstream change detection
