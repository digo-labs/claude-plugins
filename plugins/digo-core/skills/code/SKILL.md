---
name: code
description: Write code in a Digo app repo (any repo outside the core monorepo) in the house style — the skill carries the style rules itself, matches the neighbouring code, and opens a docs page only for a platform API it hasn't verified. Use when asked to create or change any code in an app — components, pages, hooks, helpers, services, schemas, configs, types, tests. Inside the core monorepo use code-in-core instead.
---

# Write Code: $ARGUMENTS

Write code the way the user writes it: the house style below, plus the habits of the code around it. There is no docs read up front — this skill is the style guide, and the app's own code shows the rest.

**Code that goes into the core monorepo** (the repo whose root `package.json` is named `@digo-labs/index`, with `packages/ui`, `packages/common`, `backend/`) — even from an app session with core added as a folder? Use `digo-core:code-in-core` for it instead.

## 1. Read the neighbourhood

- Parse the request: what kind of code, where it lives, what it does.
- Read the target file and the 2–3 closest siblings in full (same folder, same kind), plus the barrel they export from. For everything the style below doesn't fix — naming, import order and alignment, formatting, how services and state are called — match them. Where old code breaks a house rule, new code follows the rule; don't rewrite old code unasked.
- **Search before you declare.** Most past mistakes were copies. Before writing a type, union, constant, helper, hook or repeated block of JSX, grep the app (and the `@digo-labs/common` types it already imports) for one with the same shape, values or job. Reuse it. Copy the neighbours' style, never their duplication.

## 2. House style

**TypeScript**

- Zero comments in TypeScript source. If a value needs explaining, give it a named constant.
- `function` declarations for components and functions; handlers are `function handleX()`. Short inline callbacks (`.map`, `.filter`, effect bodies) may stay arrows.
- Component props are an `interface Properties` (`<Name>Properties` when exported or when the file has several components), taken as one `properties` parameter and destructured on the first line of the body.
- Module-level free functions go into a `<feature>-helpers.ts` class of `public static` methods (`class PrintHelpers`). A helper only one class uses is a private member of that class.
- Build typed results before returning them: `const result: Type = { … }; return result;`. Functions have named return types, never inline object types.
- Enums for closed sets in app code, members and values in `UPPER_CASE` unless the neighbours differ. String unions for public props exported from packages.
- One source per shape: a union used in two places is a named type; shared shapes get a general name, not a feature one. A content prop named like an HTML attribute (`title`) is `Omit`-ted from the element props it extends.
- Magic strings are named constants. A value two sides must agree on (event or channel name, header, storage key) is one constant both import.

**Structure**

- A feature folder splits into `types.ts`, `consts.ts`, `<feature>-helpers.ts`, its components and hooks, and an `index.ts` barrel that re-exports them. Import from the barrel.
- `consts.ts` holds only what two or more files share, or content someone edits in one place (copy, step tables, catalogs). Single-use values and class strings stay inline in the file that uses them; single-use constants sit at the top of that file.
- Two consumers = shared code. When the logic or JSX you need already exists, extract it (to the helpers class, or an app component) and switch the original caller to it in the same change. To share without an import cycle, move the code down to the module both sides import; never copy it.
- Build only what has a caller now: no options, exports or props "for completeness", no test-only controls on shipped components.
- Adding a prop must not turn a working component into a chain of wrappers. If a restructure seems needed, propose it first.
- When a file grows to about twice its largest sibling, split it by sub-domain.
- Tests live in `tests/`, mirroring `src/`, never next to the source. Test data is built from the app's real definitions (the `db.ts` tables), not a hand-copied schema.

**Styling** — when the app uses core's styles (`@digo-labs/ui` or `@digo-labs/common` CSS): typography only with `typo-1`…`typo-18`, `typo-header` / `typo-label` / `typo-body` / `typo-code` and `typo-weight-N`, never `text-sm`-style sizes (colour classes are fine); colours from the palette tokens, never hex; the `cs-*` utilities (`cs-transition`, `cs-focus`, `cs-disabled`, …) before hand-written equivalents. Otherwise follow the app's own styling.

**Known traps**

- A timer handle that a guard reads is cleared and set to `null` together, in one method.
- Never delete a hook call because its return value is unused: it can be a subscription (`useDesignSystem()` keeps `cssColor()` reads in step with the theme).
- React Three Fiber copies the `uniforms` prop: for uniforms you mutate, use a memoized `ShaderMaterial` with `<primitive attach="material">`.

## 3. UI is the app's choice

Use `@digo-labs/ui` components when they fit, another library, or the app's own design — follow what the app already does and what the screen needs. Check the real API of anything you haven't used in this app, never code it from memory: a core component's props in its installed types (or its docs page), an outside library's in its own docs or source.

**Exception — AWS event apps** (the app renders `Aws*` components from `@digo-labs/ui`, or its `CLAUDE.md` says so): everything guests see uses the AWS RE26 brand components (`AwsBlock`, `AwsBlockGroup`, `AwsShape`, `AwsPattern`, `AwsTexture`) with their palette, type and motion as shipped. Position them, even inside canvas or WebGPU scenes; never redraw them or invent their motion. Staff screens (consoles, setup, print queues) stay free.

## 4. Platform goes through core

Digo's AWS services — backend, auth, database, storage, AI, realtime, deploy — are used only through the `@digo-labs/*` APIs (`services.*`, `defineApp`, `defineDatabases`, `db:push`, `init-aws`). Never call AWS directly, never work around those APIs, and never fix a package problem from the app's config (aliases into another package's internals, patched `node_modules`). If core can't do what the app needs, stop and say so: that is a core change.

Verify before you call: if you haven't seen an API used in this app or this session, open its installed types in `node_modules/@digo-labs/*`, or its one Guide page from `https://design.digo-labs.com/llms.txt` (Authentication, Declaring Tables, Database Changes, Storage and Files, AI Features, WebSockets and Channels, Deploying to AWS). One page per API, never the whole Development section. When a page and the installed types disagree, the types win.

## 5. Check and report

Run the app's type check and lint from its `package.json` scripts and fix what they raise; for UI, look at it in the browser. Report in a few lines: what changed, anything you couldn't verify, and any gap that needs core.
