---
name: code
description: Write code in a Digo app repo (any repo outside the core monorepo) in the house style, matching the neighbouring code and checking every platform API against the installed package before using it. Use when asked to create or change any code in an app — components, pages, hooks, helpers, services, schemas, configs, types, tests. Inside the core monorepo use code-in-core instead.
---

# Write Code: $ARGUMENTS

Code that goes into the core monorepo (root `package.json` named `@digo-labs/index`) uses `digo-core:code-in-core`.

## Where the truth is

For any `@digo-labs/*` API you haven't seen used in this app: **installed types > package guide > site**. Read its
types in `node_modules/@digo-labs/<package>/`, then the guide shipped in that package (its `README.md` or guide
file, when present), and only then one page of https://design.digo-labs.com (start from `llms.txt`). The installed
version is what the app runs; when sources disagree, the earlier one wins. The same goes for outside libraries:
their installed types or their own docs, never memory.

## Before writing

Read the target file and its 2-3 closest siblings in full, and match them in everything the style below doesn't
fix (naming, imports, formatting, how services and state are called). Search before you declare: grep the app and
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
- Enums for closed sets in app code; string unions for public props exported from packages.
- One source per shape and value: shared unions are named types; magic strings are constants; a value two sides
  must agree on (event, channel, header, storage key) is one constant both import.
- Feature folders: `types.ts`, `consts.ts`, `<feature>-helpers.ts`, components, hooks, and an `index.ts` barrel.
  `consts.ts` holds only what two files share or content edited in one place.
- Two consumers = shared code: extract it and move the original caller in the same change; never copy.
- Build only what has a caller now; propose restructures before doing them; split a file that grows to about
  twice its largest sibling.
- Tests live in `tests/`, mirroring `src/`, built from the app's real definitions.
- When the app uses core's styles: typography only through `typo-*` classes, colours from the palette tokens, the
  `cs-*` utilities before hand-written equivalents.

Known traps: a timer handle a guard reads is cleared and nulled together; never delete a hook call for an unused
return value (it can be a subscription); React Three Fiber copies `uniforms`, so mutable uniforms need a memoized
`ShaderMaterial` with `<primitive attach="material">`.

## Platform and UI

- Digo's AWS services (backend, auth, database, storage, AI, realtime, deploy) go only through the `@digo-labs/*`
  APIs. Never call AWS directly, work around them or patch packages from the app; if core can't do it, stop and say
  so: that is a core change.
- UI is the app's choice (core components, another library or its own design), except what guests see in AWS
  event apps, which uses the RE26 brand components as shipped: position them, never redraw them or invent their
  motion.

## Check

Run the app's type check and lint and fix what they raise; for UI, look at it running. Report what changed, what
you couldn't verify, and any gap that needs core.
