---
name: destroy-digo-app
description: Tear down a Digo app's AWS infrastructure — Amplify app, S3 bucket, and (optionally) the Postgres schema. Use when the user wants to destroy, tear down, remove, or decommission a digo-labs app's AWS resources, or invokes `/destroy-digo-app`.
---

# Destroy a Digo App

Run the app-template's `destroy` script to remove the AWS infrastructure `init-aws` created — the Amplify app (and its domain association), the per-app S3 bucket, and, unless told otherwise, the app's Postgres schema. This is the inverse of [`/create-digo-app`](https://design.digo-labs.com/docs/skills/skill-create-digo-app). The canonical reference is [Deploying to AWS → Destroying an app](https://design.digo-labs.com/docs/guide/deploying-to-aws#destroying-an-app).

This is destructive and creates no backups. Confirm carefully and surface every step.

## Inputs to collect

Use `AskUserQuestion`.

1. **Which app** — the directory of the cloned app. It must contain the app-template `package.json` (with the app's `name`) and `scripts/destroy.sh`. Everything — bucket, Amplify app, schema — is derived from `package.json` "name".
2. **Keep the database?**
   - **Destroy everything** (default) — removes the AWS infra AND drops the Postgres schema.
   - **Keep the schema** (`--keep-db`) — removes only the AWS infra, leaving the data in place.

## Prerequisites (stop on any failure; surface the error)

- Run from inside the app's directory (where `package.json` and `scripts/destroy.sh` live).
- `aws sts get-caller-identity` succeeds (run `aws sso login --sso-session productionclub` if your session expired). `npm run destroy` runs under the **Provisioner** profile automatically, which carries the delete permissions — you don't set a profile by hand.
- The user has explicitly confirmed they want to destroy this specific app.

## Workflow

### 1. Confirm the target

Spell out exactly what will be removed (all derived from `package.json` "name"):

- Amplify app `<name>` + its `main` branch and domain association `<name>.digo-labs.com`.
- S3 bucket `<name>-digo-labs-storage` — **and all its contents**.
- Postgres schema `<name with hyphens → underscores>` — unless `--keep-db`.

Shared `monorepo/*` secrets, the git repo, and `.env` are left untouched.

### 2. Run destroy

```bash
# remove everything, including the Postgres schema:
npm run destroy

# remove the AWS infra but keep the schema + data:
npm run destroy -- --keep-db
```

The script prints what it will delete, then asks you to **type the exact app name to confirm** before doing anything. Provide the name from `package.json`. It then proceeds in order: drop the Postgres schema (unless `--keep-db`) → delete the Amplify domain association → delete the Amplify app → empty and delete the S3 bucket. Surface the output verbatim.

### 3. Report

- What was removed (Amplify app, bucket, schema — or schema kept).
- Anything the script reported it skipped (e.g. "no Amplify app named …; skipping") or couldn't delete.
- Reminder: the local repo and `.env` remain — delete the directory yourself if you want it gone.

## Error handling

| Error | Likely cause | Action |
|---|---|---|
| Access denied on a delete call | Provisioner session expired, or its permission set is missing a delete action. | Run `aws sso login --sso-session productionclub`; if it persists, ask an admin to check the Provisioner permission set. |
| "Could not read name from package.json" | Not run from an app cloned from app-template. | `cd` into the app directory and retry. |
| Confirmation aborted | Typed name didn't match. | Re-run and type the exact `package.json` "name". |
| Schema drop fails on missing `.env` | `.env` was removed before teardown. | Re-run with `--keep-db` to skip the schema drop, or restore `.env` (`init-aws` writes it). |

## Do not

- Run without explicit confirmation of the specific app — this is irreversible and empties the bucket.
- Override the profile — `npm run destroy` already forces `AWS_PROFILE=provisioner`; don't set `AWS_PROFILE` to anything else.
- Touch shared `monorepo/*` secrets or any other app's resources.

## Caution

Teardown is destructive with no undo. Watch the domain-association → delete-app sequence and the S3 empty/delete steps; if any step errors mid-run, stop and surface it rather than assuming success, then verify the result in the AWS Console.
