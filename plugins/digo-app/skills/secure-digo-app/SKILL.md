---
name: secure-digo-app
description: Bring an app cloned from app-template onto the tier-gated backend — declare per-table access rules in db.ts with the owner, bump @digo-labs packages, run db:push, and verify the rules live. Use when an app's database calls return 403 after the backend security upgrade, when the user wants to add access rules or secure an app, or invokes `/secure-digo-app`.
---

# Secure a Digo App

`api.digo-labs.com` enforces authentication on every request. Callers get a **tier** — `public < user < org < admin` (signed out, any signed-in user, verified organization email, admin role) — and every database table must declare **access rules**: the minimum tier to read, the minimum tier to write, and optionally an **owner column** that scopes rows to the signed-in user. **A table with no rule answers 403 — fail closed.**

Apps created from `app-template` before the upgrade call `defineDatabases(name, tables)` with two arguments and have no rules, so all their database calls now return 403. This skill upgrades ONE app: it declares the rules with the app's owner (they are per-table judgment calls — never guess them), bumps the `@digo-labs` packages, walks the owner through `db:push`, and proves the rules live with probes.

Two facts that shape the flow:

- **Rules are server-side data.** `db:push` writes them into the backend's `common.tableAccess` table — the app's database calls start working again **without redeploying the app**.
- **The dependency bump matters separately.** `@digo-labs/services@0.1.18+` moved the AI client to the `/ai` routes and added the Replicate provider; older published clients call paths the backend no longer serves. Apps that use AI need the bump **and** a redeploy; apps that don't can take the bump lazily.

## Prerequisites (stop on any failure; surface the error)

- The target is a Digo app: its `package.json` `dependencies` include `@digo-labs/app`.
- `npm run db:push` will open an AWS Session Manager tunnel to the private database: the owner needs AWS credentials (`aws sso login`) and the `session-manager-plugin` (macOS: `brew install --cask session-manager-plugin`).

## Workflow

### 1. Identify the app

Use the current directory if its `package.json` depends on `@digo-labs/app`; otherwise ask for the path. Read the app `name` (its database schema is the name with hyphens → underscores).

If the working tree is dirty, tell the owner what's uncommitted and let them decide: continue on top, or commit/stash first. Never assume.

### 2. Read `src/db.ts`

- **Already 3 arguments?** Report the existing rules table-by-table, confirm they still match the owner's intent, and skip to step 5.
- Two arguments → collect every table and its columns for step 4.
- If the file deviates heavily from the template shape (generated code, re-exports), surface it and adapt — never blind-rewrite.

### 3. Check the login situation

Tiers only differentiate if the app has sign-in. Check `src/app.config.ts` for `auth` in `defineApp`. If the app has **no login**, say so plainly before asking anything: every visitor is `public`, so a `user` tier would make that operation unreachable from the app. The realistic choices become `read: 'public'` with writes done by admins elsewhere, or adding login first (see the app-template `LoginPage`). Let the owner decide with that context.

### 4. Ask the owner for each table's rules

One `AskUserQuestion` question per table (batch up to 4 tables per call). Options, with the recommendation first:

- **`read: 'user', write: 'user'` (Recommended)** — the app-template default; any signed-in user.
- **`read: 'public', write: 'user'`** — public content, signed-in editing.
- **`read: 'user', write: 'user', owner: '<column>'`** — offer ONLY when the table has a plausible owner column (`userId`, `ownerId`, `authorId`, …); each user then sees and edits only their own rows, the column is stamped from the session, and a client-supplied value is rejected.
- **`read: 'public', write: 'admin'`** — content managed by admins, visible to all.

Describe consequences in plain words ("anonymous visitors get 401 on reads"), not just tier names.

### 5. Edit `src/db.ts`

Add the third argument and `access` to the destructure, mirroring the template exactly — aligned formatting, no comments:

```ts
export const { tables, databases, schema, access } = defineDatabases(pkg.name, {
  items: {
    id:          uuid('id').primaryKey().defaultRandom(),
    name:        text('name').notNull(),
    description: text('description').notNull().default(''),
  },
}, {
  items: { read: 'user', write: 'user' },
});
```

The map is **total** — every table must appear or the call doesn't compile. `owner` is typed against that table's columns, so a typo is a compile error.

### 6. Bump the packages

`npm run update:digo-labs` (every app has the script). This updates all `@digo-labs/*` to latest and rewrites the lockfile.

### 7. Validate

`npx tsc -b` and `npm run lint`. A compile error inside the new map is a typo'd tier or a non-existent owner column — fix before proceeding.

### 8. The owner runs db:push

Never run it for them — it needs their TTY (`strict: true` prompts) and they must review the plan:

```bash
npm run db:push
```

What they should see: the tunnel line (`Database tunnel open (via bastion …)`), **no `DROP` statements in the drizzle plan** (abort and investigate if any appear), and the confirmation line `Access rules synced for '<schema>': …` listing every table.

### 9. Verify live

Probe the real backend with the app's origin (rules are live immediately — no redeploy):

```bash
curl -s -o /dev/null -w "%{http_code}" -X POST 'https://api.digo-labs.com/database-get-all' \
  -H 'Content-Type: application/json' -H 'Origin: https://<app-subdomain>.digo-labs.com' \
  -d '{"table":"<table>"}'
```

Expected: `200` for a `read: 'public'` table, `401` for a `read: 'user'` table probed anonymously — the 401 IS the proof the rule is enforced. Report a small table of route → expected → actual.

### 10. Report

Summarize: rules declared, packages bumped, push output, probe results, and whether the app needs a **redeploy** (yes if it uses AI or the owner wants the new packages live; no for the rules alone). Hand the owner a one-sentence lowercase commit message (e.g. `declare table access rules and update digo packages`). Never commit or push yourself.

## Error handling

| Error | Likely cause | Action |
|---|---|---|
| `db:push` fails: `'src/db.ts' does not export 'access'` | The destructure wasn't updated in step 5 | Add `access` to the exported destructure and re-run. |
| `db:push` hangs or `session-manager-plugin … not found` | Tunnel prerequisites missing | `aws sso login`; install the plugin; re-run. |
| Drizzle plan shows `DROP` | Schema drift beyond the rules (someone changed tables) | Abort. Diff the plan against intent with the owner before anything is applied. |
| Still 403 after push | Rules didn't sync (push aborted early) or wrong table name probed | Re-read the push output for the `Access rules synced` line; check the schema name. |
| AI calls fail after the upgrade | App still runs an old published client against the `/ai` routes | The app needs the dep bump deployed — rebuild/redeploy the app. |
| Compile error in the access map | Typo'd tier or owner column | The types are the guard — fix the name; never widen types to silence it. |

## Do not

- Guess or default a table's rules without the owner answering — they are security decisions.
- Run `db:push` yourself — the owner runs it and reviews the plan.
- Touch anything beyond `src/db.ts`, `package.json`/lockfile (via the update script), and what validation requires.
- Commit or push — hand the owner the commit message.

## Caution

The dangerous failure here is silent: rules that *look* declared but never synced leave the app 403ing with no code error anywhere. Step 9's probes are not optional — a rule is DONE when a probe against `api.digo-labs.com` proves it, never when the file is edited.
