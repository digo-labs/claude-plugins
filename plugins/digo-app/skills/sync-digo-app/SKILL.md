---
name: sync-digo-app
description: Propagate template-owned infra/config changes from app-template into apps cloned from it (websockets-hub, reinvent-avatar, …). Reports which cloned apps have drifted from the template, then syncs the ones you pick. Use when the user wants to sync apps with app-template, pull template updates into a cloned app, check which apps are outdated/stale/behind the template, or invokes `/sync-digo-app`.
---

# Sync a Digo App with app-template

Apps are created from `digo-labs/app-template` via "Use this template", so each has its **own git history and remote — there is no git ancestry linking it back to the template.** Infra and config files therefore drift silently: fix `scripts/init-aws.sh` in the template and every cloned app keeps the stale copy.

This skill closes that gap. It reads the template's `.template-sync.json` manifest, reports which cloned apps have drifted and on which files, lets you pick what to apply (with per-file control over anything risky), and applies the picks on a dedicated branch per app — never touching app-owned files, never auto-pushing.

One-way only: **template → app.** It never writes back to the template.

## What it syncs — the manifest

The template owns `.template-sync.json`. Every file tracked in the template is matched against its globs; **first match wins** in this order:

1. `ignore` — never touched (generated/secret: `package-lock.json`, `.env`, `.env.local`).
2. `merge` — partial merge. `package.json` → only the template's `scripts` and `overrides` keys (app `name` and app-added script keys preserved; **dependencies never touched** — that's `npm run update:digo-labs`).
3. `reviewOnDrift` — app-owned, never overwritten, but a drift is reported as a manual-review note (`src/index.tsx`: every app rewrites its routes, but a change to the router *bootstrap* is worth surfacing).
4. `scaffoldOnce` — seeded at app creation, **never re-synced** (`src/pages/**`, `src/db.ts`, `src/app.config.ts`, `src/overrides.ts`, `index.html`, `README.md`, `public/**`).
5. `sync` — the infra/config that should track the template verbatim (`scripts/**`, `eslint.config.js`, `vite*.ts`, `tsconfig*.json`, `drizzle.config.ts`, `.gitignore`, `.vscode/**`, `certs/**`, `.env.development`, `.env.example`, `src/index.css`, `src/main.tsx`).

A tracked template file matching **no** bucket is **unclassified** — report it so the manifest can be updated; never guess.

## Modes

- `/sync-digo-app` — scan → drift report → pick apps/changes → apply.
- `/sync-digo-app --check` — scan → drift report only. Changes nothing, no prompts.

## Prerequisites (stop on any failure; surface the error)

- `git --version` succeeds. For the optional PR step: `gh auth status`.
- The template is reachable (see step 1). Its `.template-sync.json` must exist — if missing, stop and tell the user to add it (this skill can't sync without it).

## Workflow

### 1. Locate the template

- If the current directory (or a passed path) contains `.template-sync.json`, use it.
- Else look for a sibling directory named `app-template` (check `./app-template`, `../app-template`). If found, use it.
- Else ask the user for the path, or offer to `git clone https://github.com/digo-labs/app-template` into a temp dir. (A fresh clone only carries the manifest once it's committed & pushed to the template repo — prefer a local sibling if the manifest was added but not yet pushed.)

Set `SCAN_ROOT` to the template's **parent** directory. Check `git -C <template> status --porcelain`; if dirty or not on `main`, warn that you're reading its working tree and let the user proceed or stop.

### 2. Discover cloned apps

Scan each immediate subdirectory of `SCAN_ROOT`. A directory is a target when it is a git repo (`.git` present), is **not** the template, and its `package.json` `dependencies` include `@digo-labs/app`:

```bash
for d in "$SCAN_ROOT"/*/; do
  [ -d "$d/.git" ] || continue
  [ "$(basename "$d")" = "app-template" ] && continue
  node -e "process.exit(require('$d/package.json').dependencies?.['@digo-labs/app']?0:1)" 2>/dev/null && echo "$d"
done
```

This includes apps like `websockets-hub` and `reinvent-avatar`; it excludes the `core` monorepo, `claude-plugins`, and workspace monorepos like `digo-reinvent` (which don't depend on `@digo-labs/app`).

### 3. Compute drift (read-only)

Enumerate the template's tracked files (`git -C <template> ls-files`) and assign each to its bucket (precedence above). For every app, compute:

- **`sync` files** — compare template vs app with `cmp -s`.
  - App missing the file → **add** (safe).
  - Content differs → classify **stale** vs **diverged** by blob lineage: the app's file is *stale* (safe) if its content ever existed in the template's history; *diverged* (risky) if it never did.

    ```bash
    ah=$(git -C "$app" hash-object -- "$path")          # app file's blob sha
    intmpl=$(for c in $(git -C "$template" log --format=%H -- "$path"); do
               git -C "$template" rev-parse "$c:$path" 2>/dev/null; done | sort -u | grep -qx "$ah" && echo yes || echo no)
    # intmpl=yes → stale/safe (app holds a prior template version); no → diverged/risky
    ```
    When lineage can't be determined, treat as **risky** (safer — it just becomes its own checkbox).
- **`merge` (`package.json`)** — diff the template's `scripts`/`overrides` against the app's. A template key absent in the app, or app-added keys → safe. A template key the app has with a **different** value → **risky** (overwriting an app's edit).
- **`reviewOnDrift`** — if it differs, record a **manual-review note** (not applied, not a checkbox).
- **Template-deleted** — an app file matching a `sync`/`scaffoldOnce` glob that is absent from the template `HEAD` **but present in template history** → **risky delete candidate**. (Absent from history too = app-added; leave alone.)
- `scaffoldOnce` and `ignore` files are skipped entirely.

### 4. Report

Print a per-app summary: **clean** or **stale**. For stale apps list, grouped: safe updates (add/stale files, safe `package.json` keys), ⚠ risky items (diverged files, risky keys, delete candidates), and any manual-review notes. Also list **unclassified** template files once, globally.

If `--check`, stop here.

### 5. Pick what to apply

Use `AskUserQuestion` (multi-select). Note the 4-options-per-question cap — batch if a list exceeds it.

1. First question: **which stale apps to sync** — one option per stale app (its *safe* bundle). Clean apps aren't offered.
2. Then, for each selected app that has risky items: a follow-up multi-select — **one option per risky item** (`overwrite diverged <file>`, `overwrite <key> in package.json`, `delete <file> (removed from template)`), so the user decides each individually.

Nothing risky is ever included by ticking only the app box.

### 6. Apply, validate, offer PR

Per selected app, operating only on that app's ticked changes:

- Require a clean working tree (`git -C <app> status --porcelain` empty). If dirty, warn and skip that app (or let the user stash).
- `git -C <app> switch -c sync/app-template` (or reuse it if it exists).
- Apply: copy each ticked `sync` file from the template (create parent dirs); `git rm` ticked delete candidates; merge ticked `package.json` keys by editing the app's `package.json` (preserve `name` and app-only keys).
- If `overrides` changed → `npm install` (updates the lockfile). Then validate: `npm run lint` and typecheck (`npx tsc -b`). Report pass/fail; a failure doesn't roll back — surface it for the user.
- **Offer** to `git commit` and `gh pr create` for that app. Never push or open a PR without the user's go-ahead.

### 7. Summary

Per app: branch created, files applied, validation result, and anything **held for manual review** (risky items left unticked, `reviewOnDrift` notes, unclassified template files). Remind the user nothing was pushed.

## Error handling

| Error | Likely cause | Action |
|---|---|---|
| No `.template-sync.json` in the template | Manifest not added/committed, or template located wrong | Confirm the template path; tell the user to add the manifest. Don't sync without it. |
| No apps discovered | `SCAN_ROOT` wrong, or apps live elsewhere | Confirm the parent directory; ask the user where the apps are. |
| App working tree dirty | Uncommitted local work | Skip that app and report it; suggest committing/stashing first. |
| `npm install` / `lint` / `tsc` fails after apply | A template change is genuinely incompatible with the app | Surface the output verbatim; leave changes on the branch for the user to resolve. |
| Blob-lineage check inconclusive | Shallow clone / rewritten template history | Treat the file as risky (own checkbox) rather than assuming stale. |

## Do not

- Touch `scaffoldOnce` files, `package.json` dependencies/`name`, `.env`/`.env.local`, or any file outside the manifest's `sync`/`merge` buckets.
- Overwrite a **diverged** file or **delete** a file without an explicit tick for that specific item — risky items are always per-file.
- Push or open a PR without the user's confirmation. Never write to the template.
- Sync an app whose working tree is dirty.

## Caution

The value is in *not* clobbering app work. When lineage or intent is uncertain, default to **risky** (surface it, let the user decide) rather than folding it into the safe bundle. Over-asking is cheap; a silently overwritten hand-edit is not.
