---
name: build-idea
description: Take an idea — a function, component, page, feature, or whole app — from rough thought to working code by composing the other skills. Shape it, size it, build it, wrap it. Use when the user has an idea they want implemented end to end, or invokes /build-idea.
---

# Build Idea: $ARGUMENTS

Orchestrate, don't duplicate. Every phase delegates to an existing skill by name — when those skills improve, this one improves with them. Never restate their instructions here; invoke them.

Ideas come in every size — a single function, a component, a page, a feature, a whole app. Scale each phase to the idea; skip ceremony a small idea doesn't need.

## 1. Shape

Get to shared understanding before anything is built:

- Idea is vague or brand new → run `/brainstorm`. It ends with a structured, buildable summary.
- Idea is already half-formed and needs stress-testing → run `/grill-me`.

Facts about the current repo are looked up, never asked. Only real decisions reach the user — popups, recommended option first. Do not move on until the user confirms the shape.

## 2. Size

Judge honestly whether the whole thing fits this session:

- **Fits** → keep the confirmed summary in-session and start building.
- **Doesn't fit** → write a plan memory file: destination, decisions locked, steps/rounds, verify recipes, and which code skill executes it. Add its index line marked ⏳. Invoking `/build-idea` with no arguments resumes the newest ⏳ plan; each session builds the next round and updates the file as it goes. No memory system available? Put the plan at `documents/plans/<name>.md` in the repo instead.

## 3. Build

All code goes through the code skills, never written bare:

- Inside the digo core monorepo → `/code-in-core` and `code`
- Anywhere else → `/code`

Work in small rounds: implement a piece, verify it actually works (boot, page renders, headless check — whatever this repo's recipes are), then continue. A deviation from the confirmed shape is a popup, not a silent choice.

## 4. Wrap

- Verify end to end and show proof: screenshot, test output, or boot log.
- Multi-session plan? Update the plan file; flip its index line to ✅ only when the destination is reached.
- Offer `/review` on the changed code when that skill is available.
- Report what landed and what stayed open. Never commit or push — that is the user's call.
