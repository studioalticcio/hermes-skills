# `/clear` command requested UX

the user requested a Telegram bot command for deleting Hermes conversation history.

Required behavior:

- Command: `/clear`
- User must be able to choose between:
  - delete latest conversation
  - delete a specific conversation
  - delete all conversations
- Destructive deletion must ask for confirmation before executing.
- “Specific” needs either a selectable list or a requested conversation/session id.

Important correction from the original session: the first attempt only saved a template skill and did **not** implement the bot. Future work should inspect Hermes' actual Telegram gateway and session-store code, implement the handler, and verify against real/disposable session data.
