# Foetz Drive via Mac Chrome bridge — 2026-07-17

## Verified context

- Actual Foetz Drive URL: `https://www.leclercdrive.fr/region-luxembourg/mondercange/drive-foetz.aspx`
- Address: 11 Rue du Brill, 3898 Foetz Mondercange.
- Browser-derived Drive ID: `986101`.
- Browser-derived active shopping host: `fd4-courses.leclercdrive.fr`.
- `mcp-leclerc-drive` locator returned irrelevant French results for `Foetz`/Luxembourg postal searches. Do not use that result to select Foetz.

## Correct bootstrap

1. In dedicated Mac Chrome, open the Foetz URL and click **Commencer mes courses**.
2. It selects the active host:
   `https://fd4-courses.leclercdrive.fr/magasin-986101-986101-foetz.aspx`
3. Set MCP context explicitly:

```text
set_store(store_id="986101", host="fd4-courses.leclercdrive.fr")
```

4. Prove it through `get_store`, `search_product("lait")`, and `get_cart`.

## Live results observed

- `search_product("lait")` returned Foetz catalogue products with local prices and availability.
- `get_cart()` returned an empty remote Foetz cart.

## Bridge security

Chrome CDP is private through the Mac → server reverse SSH tunnel, with both ends loopback-only. The server's `127.0.0.1:<PORT>` identified a macOS Chrome instance; no cookies were read or output.
