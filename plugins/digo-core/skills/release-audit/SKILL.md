---
name: release-audit
description: Audit the core monorepo's npm packages — what changed since each package's last publish, which need releasing and at what version — then guide the user through `npm run release` and offer to bump the downstream apps that consume @digo-labs packages. Use when the user asks what packages need updating/publishing, whether npm is stale, wants to release packages, or invokes `/release-audit`.
---

# Release Audit

Audits every publishable package in the core monorepo against its last published state, proposes version bumps, and — behind a single confirmation gate — hands the user a precise cheat-sheet for running `npm run release` themselves (their npm 2FA makes the publish theirs). Afterwards (or when nothing needs publishing) it reports which sibling apps in `~/digo-labs` are behind on `@digo-labs/*` deps and offers to bump the ones the user picks.

**Git rules, non-negotiable:** the skill never commits and never pushes — not in core, not in any downstream app. Every run ends with the working tree changed (or untouched) and a list of what the user should review and commit themselves.

Runs from the core monorepo root (`~/digo-labs/core`). If invoked elsewhere, operate on that path anyway.

## Phase 1 — Audit

### Package inventory

Publishable packages are every workspace whose `package.json` lacks `"private": true`. Enumerate dynamically — `packages/*/package.json` plus `backend/package.json` — never hardcode the list (as of writing: app, common, docs, eslint-config, services, tsconfig, ui, vite-config, ws, backend).

### Baseline per package

For each package, find the last commit where its `package.json` `version` field actually changed (not just any touch of the file):

```bash
git log -L '/"version":/',+1:packages/<pkg>/package.json --format=%H | head -20
```

The most recent commit in that output whose hunk shows a `-`/`+` version pair is the release-baseline commit. Then:

1. **Diff since baseline** — `git diff --stat <baseline> -- <pkgdir>` (diffing against the working tree deliberately includes uncommitted changes: npm packs the working tree, so uncommitted work ships).
2. **Flag uncommitted separately** — `git status --porcelain <pkgdir>`; anything listed gets an explicit ⚠ uncommitted marker in the report.
3. **Cross-check npm** — `npm view <name> version`. Local version ≠ published version is a warning (a bump was made but publish likely failed, or vice versa); surface it, don't silently "fix" it.

A package with an empty diff and matching npm version is current — skip it in the release plan.

### Version proposal

Default is **patch** for every changed package (house convention — history is patch-only, everything is pre-1.0).

Flag a package as **risky** when the diff shows any of:

- removed or renamed exports in its `index.ts` / public entry files
- a dependency removed or replaced in its `package.json`
- a peer-dependency change

Risky packages get called out in the gate with a patch-vs-minor choice; never silently ship a suspected breaking change as patch.

**Internal cascade:** internal `@digo-labs/*` ranges use `^`, so a patch/minor of a dependency still satisfies dependents' ranges — `changeset version` correctly bumps **nothing** beyond the packages with changesets, and consumers pick up the new dependency transitively at install. Only a major (or a range that stops satisfying) triggers dependent republishes via `updateInternalDependencies: patch`. Don't predict republish cascades for patch releases; note transitive pickup in the report instead.

### Report

Present one terse table: package · local vs published version · proposed bump · one-line summary of what changed · flags (⚠ uncommitted, ⚠ risky, ⚠ version/npm mismatch). Then the cascade note.

## Phase 2 — The gate

One `AskUserQuestion` popup, recommended option first:

- **Proceed with this plan (Recommended)** — continue to the guided release.
- Per-risky-package patch/minor choices (as extra questions in the same popup, only when risky flags exist).
- **Report only** — stop here; continue to Phase 4.

## Phase 3 — Guided release (the user runs it)

The user publishes themselves — their npm account requires a 2FA code per publish, and only their interactive terminal can answer that prompt. The skill never writes changesets, never bumps versions, never publishes.

After the gate, print a short release brief the user follows in their own terminal:

1. The command: `cd ~/digo-labs/core && npm run release`.
2. Changeset prompt cheat-sheet — exactly which packages to select with space+enter, the major/minor answers (normally: none/none → everything patch), and a ready-to-paste summary line derived from the audit.
3. Remind them the publish step asks for the authenticator code in the terminal.

Then **wait** for the user to say the release ran. When they do, verify with `npm view <name> version` that every proposed package now shows the expected version; report any mismatch. Remind the user the version bumps + consumed changeset are uncommitted — reviewing and committing them is theirs.

If the release brief was delivered but the user declines to run it now, skip verification and continue to Phase 4 with the currently-published versions.

## Phase 4 — Downstream apps (always runs, even on a no-op audit)

### Scan

Every sibling `~/digo-labs/*/package.json` (excluding `core` and `claude-plugins`) that lists `@digo-labs/*` in dependencies or devDependencies. For each, compare every `@digo-labs/*` range against the latest published version (post-release if Phase 3 ran). Report a table: project · outdated packages (have → latest).

### Bump

`AskUserQuestion` with `multiSelect: true` listing the stale projects (plus a "none" path via cancel/Other). For each picked project:

1. Update **all** `@digo-labs/*` deps to `^<latest>` — not just the packages this release touched.
2. `npm install` in that project so the lockfile is coherent.
3. No commit — the user reviews each app's diff themselves.

### app-template boot check

If `app-template` was bumped, additionally verify it boots (standing rule: template changes are boot-verified before commit):

1. Start its dev server.
2. Poll until the page returns HTTP 200; capture a headless screenshot (house pattern: puppeteer headless) and check the console for errors.
3. Stop the server. Report pass/fail with the screenshot.

Other apps skip the boot check.

## Final report

One consolidated summary: what was published (or "nothing to publish"), what cascaded, which downstream projects were bumped, the app-template boot result, and the exact list of repos with uncommitted changes awaiting the user's review/commit/push.
