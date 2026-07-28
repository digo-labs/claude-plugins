---
name: create-digo-app
description: Scaffold a new Digo app from app-template — clone, name, install, optionally set up AWS, verify it boots. Use when the user wants to create a new digo-labs app, mentions "new app", "scaffold app", "start a new project from the template", or invokes `/create-digo-app`.
---

# Create a New Digo App

Scaffold a fresh app from the `digo-labs/app-template` repo, set its name, install dependencies, optionally set up its AWS infrastructure, and verify it boots — in one guided pass.

This file is orchestration only. **The docs are the source of truth for every fact and command** — versions, scripts, naming rules, AWS steps. Fetch them first and execute from them, so this skill never goes stale when the docs or the template change.

## 0. Fetch the docs first

Before anything else, `WebFetch`:

- `https://design.digo-labs.com/llms.txt` — the index of every guide page; keep it as context for the whole session.
- [Creating a New App](https://design.digo-labs.com/docs/guide/creating-a-new-app) — the walkthrough this skill automates; its Steps section holds the exact commands.
- [Naming Your App](https://design.digo-labs.com/docs/guide/naming-your-app) — the naming rule and everything the name drives.
- [Deploying to AWS](https://design.digo-labs.com/docs/guide/deploying-to-aws) — what `init-aws` sets up; only needed when AWS setup is on the table.

If a fetch fails, stop and tell the user — do not run the workflow from remembered facts.

**Drift rule:** when a fetched page disagrees with what the cloned template actually contains (the `engines` field in `package.json`, the scripts, the name regex in `scripts/init-aws.sh`, the port in `vite.config.ts`), the template wins for execution — and you flag the drift in the final report so the docs get fixed.

## Inputs to collect

The user may pass the app name as an argument (e.g. `/create-digo-app cool-tool`). Collect the rest with `AskUserQuestion`. Validate before continuing.

1. **App name** — required. Validate against the naming rule stated in [Naming Your App](https://design.digo-labs.com/docs/guide/naming-your-app); after cloning, re-check it against the regex `scripts/init-aws.sh` enforces (template wins). This single value drives the Postgres schema, S3 bucket, websocket id, subdomain, and Amplify app.
2. **Parent directory** — where to create the new app folder. Default to the current working directory. Refuse to continue if `<parent>/<app-name>` already exists.
3. **How to create the repo** — the two paths from the guide: **gh CLI** (creates the repo from the template and clones it in one command; needs `gh auth status` to pass) or **web template** (the user already clicked "Use this template" on the template repo and gives you the new repo's clone URL).
4. **AWS setup** — only ask if `aws sts get-caller-identity` succeeds. Run `npm run init-aws` now, or skip and run it later.

## Prerequisites (stop on any failure; surface the error + fix)

Check what the guide's Prerequisites section lists — Node at the minimum version it states (the template's `engines` field is authoritative once cloned), git, GitHub access to the `digo-labs` org. Plus: `<parent>/<app-name>` must not exist, the gh path needs `gh auth status` to pass, and the AWS path needs `aws sts get-caller-identity` to succeed.

## Workflow

### 1. Create the repo

Run the commands from the guide's **"Create the repo from the template"** step for the chosen path (gh CLI, or cloning the repo the user created from the web template). Either way you land in a clean standalone repo with its own history.

### 2. Set the app name

Follow [Naming Your App](https://design.digo-labs.com/docs/guide/naming-your-app): the real name goes in **one** place — `"name"` in `package.json`. `src/app.config.ts` and `src/db.ts` derive from it; you do **not** edit them. Optional: the `<title>` in `index.html`, the one deliberately-manual label (capitals and spaces allowed). Confirm `package.json` was updated before continuing.

### 3. Install dependencies

Run the guide's Install step (`npm install`). It pulls the `@digo-labs/*` packages from npm — no build of the core monorepo is needed.

### 4. (Optional) Set up AWS

Only if the user opted in — and **confirm once more** first: it creates real, billable AWS resources. Then run `npm run init-aws` as [Deploying to AWS](https://design.digo-labs.com/docs/guide/deploying-to-aws) describes and surface its output. The subdomain defaults to the app name; the guide shows how to pass a different one.

### 5. Verify it boots

Never report success on an unverified scaffold.

- Start the dev server with the preview browser (add a `.claude/launch.json` entry running `npm run dev` on the port from `vite.config.ts`). If no preview/browser tool is available in this session, run the dev server in the background and check the port responds.
- Confirm the login page renders and the console has no errors. Full Google sign-in can't be automated — the rendered login page is the bar.
- Take a screenshot for the report. Leave the server running for the user.

### 6. Report

What landed:

- Path to the new app, name set in `package.json` (and whether the `<title>` was set), dependencies installed, AWS ran/skipped, boot verified (include the screenshot).
- Any **docs drift** found under the drift rule, so the docs page can be fixed.

What's next — point, don't push:

- **Shape the idea** — `/brainstorm` turns a vague idea into a buildable concept; `/grill-me` stress-tests a plan the user already has.
- **Build features** — all code written in this app goes through the `/code` skill; it pulls the right docs pages and matches the design-system patterns.
- **Theme it** — swap `preset: defaultPreset` in `src/app.config.ts` for any curated preset exported by `@digo-labs/ui` (list the current options from the package or the theme-presets docs page — don't recite from memory). Custom presets are created in the core monorepo with `/create-preset`.
- **Stay current** — `npm run update:digo-labs` pulls the latest `@digo-labs/*` packages; `/sync-digo-app` reconciles template-owned config drift down the line.
- AWS skipped? `npm run init-aws` whenever they're ready.

## Errors

Troubleshooting lives in the guides, not here: **Common failures** on [Creating a New App](https://design.digo-labs.com/docs/guide/creating-a-new-app) covers scaffold-time errors (gh auth, org access, `npm install`, existing directory) and on [Deploying to AWS](https://design.digo-labs.com/docs/guide/deploying-to-aws) covers `init-aws` and deploy errors. On any failure: surface the exact error verbatim, consult those sections, and stop until it's resolved.

## Do not

- Edit `app.config.ts` or `db.ts` to set the name — the only name you set is `"name"` in `package.json` (and, optionally, the `<title>` in `index.html`).
- Run `init-aws` without explicit user confirmation — it creates real, billable AWS resources.
- Continue after a failed prerequisite, a failed step, or a failed boot verify.
- Answer from memory what the fetched docs or the cloned template can answer — versions, commands, naming rules, package and preset lists all come from them.

## After the skill completes

Stay available for follow-up. Any code the user asks for in the new app — tables in `src/db.ts`, pages, components, services — goes through the `/code` skill. For questions, fetch the relevant guide from `llms.txt` and answer from it. Tearing an app back down is the separate [`/destroy-digo-app`](https://design.digo-labs.com/docs/skills/skill-destroy-digo-app) skill.
