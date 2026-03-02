# Setting Up the GitHub Action for Complete Branch Sync

## Prerequisites

The automated sync workflow requires a Personal Access Token (PAT) to push to your custom component repository.

## One-Time Setup

### Step 1: Create Personal Access Token (PAT)

1. Go to: https://github.com/settings/tokens/new
2. Fill in:
   - **Note**: `homeassistant_core sync to google-assistant-unleashed`
   - **Expiration**: Choose appropriate duration (90 days, 1 year, or no expiration)
   - **Select scopes**:
     - ✅ `repo` (Full control of private repositories)
3. Click "Generate token"
4. **⚠️ IMPORTANT**: Copy the token immediately (you won't see it again!)

### Step 2: Add Secret to Repository

1. Go to: https://github.com/GuiPoM/homeassistant_core/settings/secrets/actions
2. Click "New repository secret"
3. Fill in:
   - **Name**: `PAT_CUSTOM_COMPONENT`
   - **Secret**: Paste the PAT you just created
4. Click "Add secret"

### Step 3: Verify Workflow is Available

1. Go to: https://github.com/GuiPoM/homeassistant_core/actions
2. You should see "Sync All Branches" in the left sidebar
3. Click on it to see the workflow

✅ **Setup Complete!**

## Usage

### Running the Workflow

1. Go to: https://github.com/GuiPoM/homeassistant_core/actions/workflows/sync-all-branches.yml
2. Click the "Run workflow" dropdown button (top right)
3. Configure options:
   - **Branch**: Leave as default (`dev`)
   - **Sync to custom component**: ✅ (recommended)
4. Click green "Run workflow" button
5. Wait 2-3 minutes for completion
6. Check the summary for results

### Understanding the Results

The workflow will show you:

#### Step 1: Dev Branch
- ✅ **Updated**: Fork's dev synced with upstream (shows commit count)
- ℹ️ **Already in sync**: No upstream changes

#### Step 2: Feature Branches
- ✅ **Rebased**: Shows commit count for each feature
- ❌ **Failed**: Requires manual conflict resolution

#### Step 3: Integration Branch
- ✅ **Rebuilt**: Shows total commits and files changed
- ⚠️ **Auto-resolved conflicts**: Conflicts between features were handled automatically

#### Step 4: Custom Component
- ✅ **Synced**: Changes copied to custom component repo
- ℹ️ **No changes needed**: Already in sync

### Success Indicators

After successful sync:
- Job completes with green checkmark ✅
- Summary shows reasonable numbers:
  - Feature branches: 1-3 commits each
  - Integration branch: ~6-8 commits
  - Files changed: ~15-20 files
- PRs update automatically to show clean commit counts
- Custom component has new timestamp

### What to Check After Sync

1. **PR #1** (Require Acknowledgment): Should show **1 commit**
2. **PR #2** (Location Restriction): Should show **3 commits**
3. **PR #6** (Integration Tracking): Should show **~6 commits**
4. **Custom Component**: Check https://github.com/GuiPoM/google-assistant-unleashed for new commit

## Troubleshooting

### Error: "Resource not accessible by integration"

**Cause**: PAT secret is missing or invalid

**Fix**:
1. Verify `PAT_CUSTOM_COMPONENT` secret exists in repository settings
2. Check PAT has `repo` scope
3. Verify PAT hasn't expired
4. Regenerate PAT if needed and update secret

### Error: "Rebase failed - manual intervention required"

**Cause**: Feature branch has complex conflicts with upstream changes

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

### Error: "Could not auto-resolve conflicts"

**Cause**: Integration branch merge conflicts are too complex

**Fix**:
1. Check workflow logs to see which files had conflicts
2. Run manual rebuild:
   ```bash
   git checkout integration/google-assistant-unleashed
   git reset --hard upstream/dev
   git merge --no-ff feature/require-acknowledgment -m "Merge ack feature"
   git merge --no-ff feature/location-restriction -m "Merge presence feature"
   # Resolve conflicts manually
   git push origin integration/google-assistant-unleashed --force-with-lease
   ```
3. Custom component sync will work on next workflow run

### Workflow doesn't appear in Actions tab

**Cause**: Workflow file not in default branch or syntax error

**Fix**:
1. Ensure workflow file exists in `dev` branch (default branch)
2. Check YAML syntax: `yamllint .github/workflows/sync-all-branches.yml`
3. Wait a few minutes for GitHub to index the workflow
4. Refresh the Actions page

### Custom component not synced

**Possible causes**:
- PAT secret not configured properly
- "Sync to custom component" option was unchecked
- No changes detected (files already in sync)

**Fix**:
1. Verify "Sync to custom component" was checked when running workflow
2. Check workflow summary to see if changes were detected
3. Verify PAT_CUSTOM_COMPONENT secret is configured
4. If files should have changed but didn't, check workflow logs

## Security Notes

### About PAT Token

- ✅ **Secure**: Stored encrypted in GitHub Secrets
- ✅ **Scoped**: Only has access to your repositories
- ✅ **Revocable**: Can be revoked anytime from GitHub settings
- ⚠️ **Expiration**: Remember to renew before expiration

### Best Practices

1. **Use fine-grained tokens** (if available): More secure than classic PATs
2. **Set expiration**: Don't use "no expiration" unless necessary
3. **Rotate regularly**: Update PAT every 3-6 months
4. **Minimal scope**: Only grant `repo` scope, nothing more
5. **Monitor usage**: Review Security tab for any suspicious activity

## When to Run

Run the workflow:

1. **Weekly**: To stay current with Home Assistant development
2. **After updating features**: When you add commits to feature branches
3. **Before starting new work**: To ensure you're working on latest code
4. **When monitoring alerts**: If upstream changes are detected in google_assistant component

## Related Documentation

- [Complete Sync Automation](SYNC_AUTOMATION.md) - Detailed workflow explanation
- [Integration Workflow](INTEGRATION_WORKFLOW.md) - Branch strategy and manual steps
- [Monitoring](MONITORING.md) - Upstream change detection

## Quick Reference

### Run Workflow
```
https://github.com/GuiPoM/homeassistant_core/actions/workflows/sync-all-branches.yml
→ "Run workflow" → "Run workflow"
```

### Check Results
- View workflow summary (shows what changed)
- Check PR #1, #2, #6 (should show clean commit counts)
- Check custom component repo (should have new timestamp)

### Manual Override
If workflow fails, see [manual sync steps](SYNC_AUTOMATION.md#manual-sync-alternative)
