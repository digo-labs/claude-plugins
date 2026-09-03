---
name: release-audit
description: Audit the core monorepo's npm packages — what changed since each package's last publish, which need releasing and at what version — then, on confirmation, run the full changesets release and offer to bump the downstream apps that consume @digo-labs packages. Use when the user asks what packages need updating/publishing, whether npm is stale, wants to release packages, or invokes `/release-audit`.
---

# Release Audit

Audits every publishable package in the core monorepo against its last published state, proposes version bumps, and — behind a single confirmation gate — writes changesets and runs the release. Afterwards (or when nothing needs publishing) it reports which sibling apps in `~/digo-labs` are behind on `@digo-labs/*` deps and offers to bump the ones the user picks.

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

**Internal cascade:** `.changeset/config.json` has `updateInternalDependencies: patch`, so `changeset version` auto-patches dependents (common → ui/services/app/docs, etc.). Do **not** write changesets for cascade-only packages — just list the cascade in the report so the user knows those will bump and republish too.

### Report

Present one terse table: package · local vs published version · proposed bump · one-line summary of what changed · flags (⚠ uncommitted, ⚠ risky, ⚠ version/npm mismatch). Then the cascade note.

## Phase 2 — The gate

One `AskUserQuestion` popup, recommended option first:

- **Release as proposed (Recommended)** — proceed with the bumps shown.
- Per-risky-package patch/minor choices (as extra questions in the same popup, only when risky flags exist).
- **Report only** — stop here, touch nothing; continue to Phase 4.

Before publishing, verify npm auth with `npm whoami` (packages publish with restricted access). If not authenticated, stop and tell the user to `npm login` — don't attempt workarounds.

## Phase 3 — Release (only after confirmation)

1. Write one changeset file per directly-changed package in `.changeset/` (kebab-case filename, e.g. `release-audit-<date>.md` or one file covering all packages):

   ```markdown
   ---
   "@digo-labs/ui": patch
   "@digo-labs/common": patch
   ---

   <one-line summary of the release>
   ```

2. `npx changeset version` — bumps versions and cascades internal dependents.
3. `npm run build:packages`.
4. `npx changeset publish`.
5. If any step fails, stop, report the failure verbatim, and leave the tree as-is for the user to inspect.

End of phase: list the files changed by the release (package.json versions, lockfile, consumed changesets) so the user can review, commit, and push.

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
