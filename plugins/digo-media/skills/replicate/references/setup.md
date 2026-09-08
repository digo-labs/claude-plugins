# Replicate Setup

## How the token reaches the script

`scripts/replicate_run.py` reads the Replicate API token from one place only: AWS SSM Parameter Store, SecureString **`/digo/replicate/api-token`** in **us-east-1**, via `aws ssm get-parameter --with-decryption` under the caller's SSO session. There is no environment-variable or file fallback.

Nothing is stored on disk. A teammate needs three things: the AWS CLI, a valid SSO login (`aws sso login --sso-session productionclub`), and a permission set that may read the parameter. The Replicate bill lands on the company account that owns the token.

Overrides: `REPLICATE_SSM_PARAMETER` (name), `REPLICATE_SSM_REGION` (region), `AWS_PROFILE` (which SSO profile the CLI uses), `DIGO_MEDIA_OUT` (output root, default `~/Pictures/image-generations`).

## Runtime

The script talks to the Replicate HTTP API with the standard library only. It bootstraps a virtualenv at `~/.cache/digo-media/venv` (override the parent with `DIGO_MEDIA_HOME`) with Pillow, used by `embed` to shrink images for artifact pages. The venv lives outside the plugin cache on purpose: Claude Code replaces the plugin directory on every update. Delete the venv folder to force a clean reinstall.

## One-time admin setup

Account `954039860919`, region `us-east-1`. Done once by an Admin.

### 1. Create the Replicate token

On https://replicate.com/account/api-tokens, signed in to the company Replicate account, create a token named `digo-media` and copy the `r8_…` value.

### 2. Create the parameter (Console)

1. Open https://console.aws.amazon.com/systems-manager/ with the region set to **N. Virginia (us-east-1)**.
2. In the navigation pane choose **Parameter Store**, then **Create parameter**.
3. **Name**: `/digo/replicate/api-token`.
4. **Description**: `Replicate API token shared by the digo-media Claude plugin`.
5. **Parameter tier**: **Standard**.
6. **Type**: **SecureString**. Leave **KMS Key ID** on the default `alias/aws/ssm`.
7. **Value**: paste the `r8_…` token.
8. Choose **Create parameter**.

Equivalent CLI:

```bash
aws ssm put-parameter --region us-east-1 \
  --name /digo/replicate/api-token --type SecureString \
  --description "Replicate API token shared by the digo-media Claude plugin" \
  --value "r8_..."
```

Rotate later with the same command plus `--overwrite`; nothing on teammates' machines changes.

### 3. Let the permission sets read it

Permission sets belong to the **ProductionClub** IAM Identity Center instance, owned by account **977306778338** (PCdogs), not by digo-labs. Only an administrator of that account can edit them; a digo-labs Admin cannot, and the Identity Center page inside digo-labs shows an "Enable" screen that must not be used.

Checked 2026-09-08: **Admin, CoreDeveloper and ReadOnly already read the parameter** through their existing policies. Only **AppDeveloper** and **Provisioner** need this inline policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadReplicateToken",
      "Effect": "Allow",
      "Action": "ssm:GetParameter",
      "Resource": "arn:aws:ssm:us-east-1:954039860919:parameter/digo/replicate/api-token"
    },
    {
      "Sid": "DecryptSsmSecureStrings",
      "Effect": "Allow",
      "Action": "kms:Decrypt",
      "Resource": "arn:aws:kms:us-east-1:954039860919:alias/aws/ssm"
    }
  ]
}
```

Console, in account 977306778338: search **IAM Identity Center** → **Multi-account permissions** → **Permission sets** → open the set → **Permissions policies** tab → **Inline policy** → **Create inline policy** (paste the block) or **Edit** (add the two statements inside the existing `Statement` list; a set holds one inline policy) → **Save changes** → **Reprovision** if the set shows as out of date. Repeat for the second set. Users then run `aws sso login --sso-session productionclub` once.

### 4. Verify

From any teammate machine:

```bash
python3 "<skill>/scripts/replicate_run.py" setup-check
```

Expected: `"runtime": {"ok": true, ...}`, `"aws": {"ok": true, ...}` and `"token": {"ok": true, "source": "ssm:/digo/replicate/api-token (us-east-1)", "replicate_account": "..."}`.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Not logged in to AWS (... Token has expired ...)` | SSO session expired | `aws sso login --sso-session productionclub` |
| `Not logged in to AWS (Unable to locate credentials)` | No AWS config on this machine | Ask an admin for the shared `~/.aws/config` (sso-session `productionclub`), then log in |
| `AWS CLI not found` | CLI missing | `brew install awscli` |
| `the AppDeveloper role cannot read /digo/replicate/api-token` | Permission set lacks the policy above | An Identity Center admin (account 977306778338) adds the inline policy and reprovisions |
| `SSM parameter ... does not exist` | Step 2 not done, or wrong region | Create it in us-east-1 |
| `http_status: 401` from Replicate | Token revoked or rotated badly | Admin creates a new token and overwrites the parameter |
| `429` / `throttled` | Replicate account low on credit, one prediction at a time | Top up credit; the script already retries with backoff |
| Venv broken after a Python upgrade | Interpreter path changed | `rm -rf ~/.cache/digo-media/venv` and re-run |

## Optional: official Replicate CLI

Not needed by the skill. For ad-hoc shell experiments: https://github.com/replicate/cli. It reads `REPLICATE_API_TOKEN`, so export it for that shell only:

```bash
export REPLICATE_API_TOKEN="$(aws ssm get-parameter --region us-east-1 --name /digo/replicate/api-token --with-decryption --query Parameter.Value --output text)"
```
