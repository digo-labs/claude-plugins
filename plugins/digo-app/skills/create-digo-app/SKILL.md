---
name: create-digo-app
description: Scaffold a new Digo app from app-template — clone, name, install, optionally set up AWS. Use when the user wants to create a new digo-labs app, mentions "new app", "scaffold app", "start a new project from the template", or invokes `/create-digo-app`.
---

# Create a New Digo App

Scaffold a fresh app from the `digo-labs/app-template` repo, set its name, install dependencies, and optionally set up its AWS infrastructure — in one guided pass. This skill is the executable path; the guide documents every concept in depth, so link out instead of restating:

- [Creating a New App](https://design.digo-labs.com/docs/guide/creating-a-new-app) — the manual walkthrough this skill automates.
- [Naming Your App](https://design.digo-labs.com/docs/guide/naming-your-app) — why one name drives everything.
- [Deploying to AWS](https://design.digo-labs.com/docs/guide/deploying-to-aws) — what `init-aws` sets up.

After scaffolding, load `https://design.digo-labs.com/llms.txt` so you can help build features on the new app with full design-system context.

The user may pass the app name as an argument (e.g. `/create-digo-app cool-tool`). If they don't, prompt for it.

## Inputs to collect

Use `AskUserQuestion`. Validate before continuing.

1. **App name** — required. Lowercase letters, digits, and hyphens; must match `^[a-z0-9][a-z0-9-]*[a-z0-9]$` (it has to be a valid npm name and a valid subdomain). No uppercase, underscores, spaces, or leading/trailing hyphen. Examples: `cool-tool`, `live-installation-2026`, `internal-portal`. This single value drives the Postgres schema, S3 bucket, websocket id, and Amplify app — see [Naming Your App](https://design.digo-labs.com/docs/guide/naming-your-app).
2. **Parent directory** — where to create the new app folder. Default to the user's current working directory. Confirm the path before proceeding. Refuse to continue if `<parent>/<app-name>` already exists.
3. **How to create the repo** — two paths:
   - **gh CLI** (recommended) — one command creates the repo from the template and clones it. Needs `gh auth status` to pass.
   - **Web template** — the user already clicked **"Use this template"** on [github.com/digo-labs/app-template](https://github.com/digo-labs/app-template) and gives you the new repo's clone URL.
4. **AWS setup** — only ask if `aws sts get-caller-identity` succeeds. Run `npm run init-aws` now, or skip and run it later.

## Prerequisites (run in order; stop on any failure and surface the error + fix)

- `node --version` → must be 22 or higher. If older, point the user to nvm or nodejs.org.
- `git --version` → must succeed.
- For the gh path: `gh auth status` → must be authenticated.
- `<parent>/<app-name>` must not already exist.
- For AWS setup only: `aws sts get-caller-identity` → must succeed.

## Workflow

### 1. Create the repo

**gh CLI path:**

```bash
gh repo create digo-labs/<app-name> --template digo-labs/app-template --private --clone
cd <app-name>
```

**Web-template path** (the user already created the repo):

```bash
git clone <user-provided-repo-url> <parent>/<app-name>
cd <parent>/<app-name>
```

Either way you land in a clean repo with its own history.

### 2. Set the app name

The template ships the placeholder name `app-template`. Set the real name in **one** place — `package.json` — and everything technical derives from it. `src/app.config.ts` and `src/db.ts` already read `pkg.name`, so you do **not** edit them. See [Naming Your App](https://design.digo-labs.com/docs/guide/naming-your-app).

- Edit `package.json`: set `"name": "<app-name>"`.
- Optional: set the browser tab title in `index.html` (`<title>…</title>`). This is the one deliberately-manual label — it can have capitals and spaces. Skip it if the user doesn't care.

Confirm `package.json` was updated before continuing.

### 3. Install dependencies

```bash
npm install
```

Pulls the latest `@digo-labs/common`, `@digo-labs/ui`, `@digo-labs/services`, and `@digo-labs/app` from npm. No build of the core monorepo is needed.

### 4. (Optional) Set up AWS

If the user opted in:

- **Confirm once more** that they want to create real, billable AWS resources (S3 bucket, Amplify app, domain mapping, Postgres schema). `init-aws` is idempotent and safe to re-run.
- Run `npm run init-aws`. Surface its output — it prints progress per step and writes `.env`.
- The subdomain defaults to the app name; pass a different one with `npm run init-aws -- <subdomain>`.

If the user skipped, note in the summary how to run it later. Full details: [Deploying to AWS](https://design.digo-labs.com/docs/guide/deploying-to-aws).

### 5. Load llms.txt for follow-up help

`WebFetch` `https://design.digo-labs.com/llms.txt` and keep it as context. It's the index of every guide page, so when the user asks "how do I add a table" or "how does websockets work" next, you can fetch the right page and answer authoritatively.

### 6. Report

Summarize what landed:

- Path to the new app: `<parent>/<app-name>`.
- Name set in `package.json` (and whether the `index.html` `<title>` was set).
- Dependencies installed.
- AWS: ran `init-aws` / skipped.

Tell the user what's next:

- `cd <app-name> && npm run dev` → opens at `http://localhost:8008`. The login page is the entry.
- AWS skipped? `npm run init-aws` whenever they're ready.
- For follow-up questions, fetch the relevant page from `https://design.digo-labs.com/llms.txt`.

## Error handling

| Error | Likely cause | Action |
|---|---|---|
| `gh repo create` / `git clone` returns "Permission denied" | User lacks access to the `digo-labs` org. | Confirm membership; surface the error. |
| `gh auth status` fails | Not logged in to GitHub CLI. | Run `gh auth login`, or switch to the web-template path. |
| `npm install` fails | Node version mismatch (must be 22+) or registry issue. | Show the error verbatim; check Node version first. |
| `init-aws` fails on secret access | Provisioner session expired, or its permission set can't read `monorepo/*`. | Surface the script's own error; have the user run `aws sso login --sso-session productionclub`, or ask an admin to check the Provisioner permission set. |
| Target directory exists | — | Refuse to continue. Ask the user to pick a different name or remove the existing directory. |

## Do not

- Edit `app.config.ts` or `db.ts` to set the name — they already derive it from `package.json`. The only name you set is `"name"` in `package.json` (and, optionally, the `<title>` in `index.html`).
- Run `init-aws` without explicit user confirmation — it creates real, billable AWS resources.
- Continue after a failed prerequisite. Stop and surface the failure.

## After the skill completes

Stay available for follow-up. The user will likely want to add tables (`src/db.ts` → `npm run db:push`), customize pages, add components, or deploy. For each, fetch the relevant page from `llms.txt` (e.g. `/docs/guide/declaring-tables`, `/docs/guide/deploying-to-aws`) and answer from the guide.

To tear an app back down, that's the separate [`/destroy-digo-app`](https://design.digo-labs.com/docs/skills/skill-destroy-digo-app) skill.
