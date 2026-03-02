# Quick Reference - Branch Sync

## One-Command Sync

**GitHub Actions UI**: https://github.com/GuiPoM/homeassistant_core/actions/workflows/sync-all-branches.yml

Click "Run workflow" → "Run workflow" → Done ✅

## What It Does

```
1. Dev → Sync with upstream/dev
2. Features → Rebase on dev
3. Integration → Rebuild from features
4. Custom Component → Sync from integration
```

## Expected Results

- **PR #1**: 1 commit
- **PR #2**: 3 commits
- **PR #6**: ~6 commits
- **Files changed**: ~15-20 files

## When to Run

- ✅ Weekly (stay current)
- ✅ After updating feature branches
- ✅ When monitoring detects upstream changes

## Manual Commands

```bash
# Full sync (if automation fails)
cd $FORK_REPO_PATH

# 1. Sync dev
git checkout dev
git reset --hard upstream/dev
git push origin dev --force-with-lease

# 2. Rebase features
git checkout feature/require-acknowledgment
git rebase upstream/dev
git push origin feature/require-acknowledgment --force-with-lease

git checkout feature/location-restriction
git rebase upstream/dev
git push origin feature/location-restriction --force-with-lease

# 3. Rebuild integration
git checkout integration/google-assistant-unleashed
git reset --hard upstream/dev
git merge --no-ff feature/require-acknowledgment -m "Merge ack"
git merge --no-ff feature/location-restriction -m "Merge presence"
# Fix conflicts if needed
git push origin integration/google-assistant-unleashed --force-with-lease
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| PAT error | Add `PAT_CUSTOM_COMPONENT` secret |
| Rebase failed | Resolve conflicts manually, re-run |
| Wrong commit count | Wait for PR to update (takes 1-2 min) |

## Documentation

- **Setup**: [GITHUB_ACTION_SETUP.md](GITHUB_ACTION_SETUP.md)
- **Details**: [SYNC_AUTOMATION.md](SYNC_AUTOMATION.md)
- **Manual**: [INTEGRATION_WORKFLOW.md](INTEGRATION_WORKFLOW.md)
