---
name: code
description: Write code in a Digo app repo (any repo outside the core monorepo) in the house style, matching the neighbouring code and checking every platform API against the installed package before using it. Use when asked to create or change any code in an app — components, pages, hooks, helpers, services, schemas, configs, types, tests. Inside the core monorepo use code-in-core instead.
---

# Write Code: $ARGUMENTS

Code that goes into the core monorepo (root `package.json` named `@digo-labs/index`) uses `digo-core:code-in-core`.

## Where the truth is

For any `@digo-labs/*` API you haven't seen used in this app: **installed types > package guide > site**. Read its
types in `node_modules/@digo-labs/<package>/`, then the guide shipped in that package (its `README.md`; skip it if the installed
version is still a stub that only points to the site), and only then one page of https://design.digo-labs.com
(start from `llms.txt`). The installed
version is what the app runs; when sources disagree, the earlier one wins. The same goes for outside libraries:
their installed types or their own docs, never memory.

## Before writing

Read the target file and its 2-3 closest siblings in full, and match them in everything the style below doesn't
fix (naming, imports, formatting, how services and state are called). Where old code breaks a rule, new code
follows the rule; don't rewrite old code unasked. Search before you declare: grep the app and
the `@digo-labs/common` types for an existing type, constant, helper, hook or JSX block with the same job, and
reuse it.

## House style

- Zero comments in TypeScript source; a value that needs explaining gets a named constant.
- `function` declarations for components and functions; handlers are `function handleX()`; short inline callbacks
  may be arrows.
- Props: an `interface Properties` (`<Name>Properties` when exported or when a file has several), taken as one
  `properties` parameter and destructured on the first line.
- Module-level helpers live in a `<feature>-helpers.ts` class of `public static` methods; a helper only one class
  uses is a private member of it.
- Typed results: `const result: Type = { … }; return result;`; named return types, never inline object types.
- Enums for closed sets in app code, members in `UPPER_CASE` unless the neighbours differ; string unions for public
  props exported from packages. A content prop named like an HTML attribute (`title`) is `Omit`-ted from the
  element props it extends.
- One source per shape and value: shared unions are named types; magic strings are constants; a value two sides
  must agree on (event, channel, header, storage key) is one constant both import.
- Feature folders: `<feature>-types.ts`, `<feature>-consts.ts`, `<feature>-helpers.ts`, components, hooks, and an
  `index.ts` barrel; import from the barrel. `<feature>-consts.ts` holds only what two files share or content edited in one place; single-use
  values stay inline, single-use constants at the top of their file.
- Two consumers = shared code: extract it and move the original caller in the same change; never copy. To share
  without an import cycle, move the code down to the module both sides import.
- Build only what has a caller now: no options or exports "for completeness", no test-only controls on shipped
  components. Adding a prop must not turn a working component into a chain of wrappers: propose restructures
  first. Split a file that grows to about twice its largest sibling.
- Tests live in `tests/`, mirroring `src/`, built from the app's real definitions.
- When the app uses the design system (`@digo-labs/ui`): typography only with `typo-1`…`typo-18`, `typo-header` / `typo-label` /
  `typo-body` / `typo-code` and `typo-weight-N`, never `text-sm`-style sizes (colour classes are fine); colours from
  the palette tokens, never hex; the `cs-*` utilities before hand-written equivalents.

Known traps: a timer handle a guard reads is cleared and nulled together; never delete a hook call for an unused
return value (it can be a subscription); React Three Fiber copies `uniforms`, so mutable uniforms need a memoized
`ShaderMaterial` with `<primitive attach="material">`.

## Platform and UI

- Digo's AWS services (backend, auth, database, storage, AI, realtime, deploy) go only through the `@digo-labs/*`
  APIs. Never call AWS directly, never alias into another package's internals or patch `node_modules`; if core
  can't do it, stop and say so: that is a core change.
- Each app builds its own UI: its own components, another library, or the opt-in `@digo-labs/ui` design system.
  AWS event apps (the app renders `Aws*` components or its `CLAUDE.md` says so) are the exception for what guests
  see: the `@digo-labs/aws` components (`AwsBlock`, `AwsBlockGroup`, `AwsShape`, `AwsPattern`, `AwsTexture` and
  the rest) with their palette, type and motion as shipped. Position them, even inside canvas or WebGPU scenes;
  never redraw them or invent their motion. Staff screens stay free.

## Check

Run the app's type check and lint and fix what they raise; for UI, look at it running. Report what changed, what
you couldn't verify, and any gap that needs core.
