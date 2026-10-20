# digo-labs Claude Code plugins

A Claude Code plugin **marketplace** for the digo-labs team. It distributes our shared
skills so they work in **any repo**, not just one checkout.

Marketplace name: `digo-labs`

## Plugins

Skills are split by audience and subsystem:

| Plugin | Use it for | Skills |
| --- | --- | --- |
| **digo-core** | coding in digo core and digo apps | `code`, `code-in-core`, `review`, `release-audit` |
| **digo-ui** | authoring the `@digo-labs/ui` library | `implement-component`, `create-preset`, `update-presets` |
| **digo-docs** | the design-system docs site | `implement-component-docs`, `audit-docs` |
| **digo-app** | building apps on `@digo-labs/*` packages | `create-digo-app`, `sync-digo-app`, `secure-digo-app`, `destroy-digo-app` |
| **digo-media** | generating images, video and other media on Replicate | `create-media`, `replicate` |

## Install

```shell
/plugin marketplace add digo-labs/claude-plugins
/plugin install digo-core@digo-labs
/plugin install digo-ui@digo-labs
/plugin install digo-docs@digo-labs
/plugin install digo-app@digo-labs
/plugin install digo-media@digo-labs
```

Inside the `digo-labs/core` monorepo every plugin is registered and auto-enabled via that
repo's `.claude/settings.json` — just trust the workspace when prompted. In other repos,
install the ones you need (`digo-core` and `digo-app` are the usual picks outside `core`).

## Invoking skills

Plugin skills are **namespaced by plugin name**:

```shell
/digo-core:code
/digo-ui:implement-component
/digo-docs:audit-docs
/digo-app:create-digo-app
/digo-media:create-media
```

## Updates

Plugins track the **latest commit** on `main` (no pinned versions). With
`"autoUpdate": true` set for this marketplace, teammates pick up new pushes on the next
Claude Code startup. To pull manually:

```shell
/plugin marketplace update digo-labs
```

## Contributing

Each skill lives at `plugins/<plugin>/skills/<skill-name>/SKILL.md`. Edit it, commit, push
to `main` — that's the release. To add a skill, create a new folder under the relevant
plugin's `skills/` directory. Keep skills **self-contained**: don't reference another
skill by filesystem path, since plugins are cached independently. A skill may load a
sibling skill with the Skill tool (`digo-media:replicate`) and locate bundled scripts through
`${CLAUDE_SKILL_DIR}` (its own, or a sibling's inside the same plugin).

`digo-media` needs the AWS CLI and an SSO login: the Replicate token is read from SSM
Parameter Store at run time (see `plugins/digo-media/skills/replicate/references/replicate-setup.md`).
