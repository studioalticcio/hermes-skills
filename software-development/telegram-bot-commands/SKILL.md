---
name: telegram-bot-commands
description: Design and implement Telegram bot commands for Hermes, including interactive callback flows, confirmations, and destructive-action safety.
platforms: [linux]
metadata:
  hermes.tags: [telegram, bot, commands, callbacks, destructive-actions]
---

# Telegram Bot Commands

Use this skill when adding or modifying commands exposed through the Telegram gateway/bot.

## Principles

- Build the command in the actual bot/gateway code; do not stop at a detached snippet or template.
- For destructive commands, use explicit scope selection plus confirmation before mutation.
- Prefer inline keyboards for bounded choices; use message-state only when free-form input is truly required.
- Keep callback data small, stable, and namespaced (`clear:latest`, `clear:confirm:all`, etc.).
- Verify in Telegram or through the bot handler test path before reporting success.

## Destructive command pattern

1. User invokes command.
2. Bot presents bounded scope options.
3. Bot presents a confirmation screen spelling out irreversibility and scope.
4. Bot executes the mutation only after confirmation.
5. Bot reports exact result.
6. Cancellation clears transient state.

## Session-reset commands: inspect native behaviour first

Before designing a Telegram `/clear` flow, inspect the installed gateway command registry and Telegram command menu. Hermes may already expose `/new` as a native command; it starts a fresh session while preserving the prior session in history. This is normally the right answer to “clear context”, and Telegram users can select it from the `/` command menu rather than type it.

Do **not** build a custom destructive `/clear` command merely because a user wants fresh context. Build one only when they explicitly want session-history deletion rather than a new session.

For a command that genuinely deletes conversation/session history, the desired UX is:

- `/clear`
- choose one:
  - latest conversation
  - specific conversation
  - all conversations
- if “specific”, prompt for/select a concrete conversation/session id
- confirmation before deletion
- execute deletion against the Hermes session store
- report what was deleted

Session-specific request details live in `references/clear-command-request.md`.

## Implementation notes

- Find the real Telegram gateway handler before writing code. Hermes gateway layout can move; inspect the current repository rather than guessing filenames.
- Deletion must target Hermes' real conversation/session database, not Telegram chat messages unless the user explicitly asks for Telegram-side message deletion.
- “All” must define scope precisely: current Telegram chat/user vs all chats reachable by the bot. Ask if the user's wording does not settle it.
- Keep audit/logging minimal but enough to debug accidental invocations; do not leak conversation contents into logs.

## Verification

- Handler is registered and reachable.
- Callback handlers cover every button state.
- Cancel path works at each step.
- Mutation path is tested on disposable/session-fixture data first.
- User-facing messages distinguish latest/specific/all.
