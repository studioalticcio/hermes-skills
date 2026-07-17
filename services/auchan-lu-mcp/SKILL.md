---
name: auchan-lu-mcp
description: Patch and operate mcp-auchan-drive against Auchan Luxembourg's PrestaShop/Klevu stack.
version: 0.1.0
platforms: [linux]
metadata:
  hermes:
    tags: [auchan, groceries, mcp, prestashop, klevu, luxembourg]
---

# Auchan LU MCP

Use when the user asks to prepare an Auchan Drive order on `auchan.lu` or to troubleshoot `mcp-auchan-drive` for Luxembourg.

## Current reality

`mcp-auchan-drive` is written for `auchan.fr`:

- hardcoded default base URL: `https://www.auchan.fr`
- France store locator uses `/offering-contexts` + French government geocoder
- product search parses France `/recherche?text=...` HTML
- cart/orders/favorites paths are France-specific

Auchan Luxembourg is different:

- `https://auchan.lu` / `https://www.auchan.lu` redirect behaviour matters
- valid public shop contexts discovered: `/bertrange/`, `/foetz/`, `/contern/`
- logged-in/store-selected sessions may redirect to `/in-store/`; with Kirchberg request cookies, `prestashop.urls.pages.*` all pointed to `/in-store/...`
- listed drives also include Kirchberg, Differdange, La Cloche d'Or, but `/kirchberg/`, `/differdange/`, `/cloche-dor/` 404 during setup
- `ps_fc` appears to encode selected favorite carrier/store context (`ps_fc=162` seen after Kirchberg switch; Contern cookie uses `ps_fc=187`)
- Set `AUCHAN_CONTEXT_PATH=contern` for the Contern operational context; LU client builds account/cart URLs under `/{context}/...`
- product search is Klevu (`https://eucs32v2.ksearchnet.com/cs/v2/search`) with API key `klevu-168718255592515755`
- local resolver may poison `eucs32v2.ksearchnet.com` to `::`; bypass via pinned Cloudflare IPs `104.20.47.97,172.66.148.194`

## Installed patch locations

Installed package path:

```bash
/home/user/.npm-global/lib/node_modules/mcp-auchan-drive/dist/
```

Patched files:

- `auchan/client.js`
  - reads `AUCHAN_BASE_URL`
  - detects LU via `AUCHAN_COUNTRY=LU` or `auchan.lu`
  - product search uses Klevu through `https.request` with pinned IP + `Host`/SNI
  - LU `search_product` maps Klevu records to the MCP product shape
  - LU `search_promos` uses Klevu and filters promo-ish records
  - LU `get_cart`, `get_orders`, `get_favorites` fail gracefully instead of France 404s
- `auchan/locator.js`
  - LU `find_stores` returns static known drive list instead of France `/offering-contexts`

Hermes MCP config entry:

```yaml
mcp_servers:
  auchan-drive:
    command: node
    args:
      - /home/user/.npm-global/lib/node_modules/mcp-auchan-drive/dist/index.js
    env:
      AUCHAN_BASE_URL: https://www.auchan.lu   # or https://auchan.lu
      AUCHAN_COUNTRY: LU
      AUCHAN_MIN_INTERVAL_MS: '1200'
      AUCHAN_JITTER_MS: '500'
      AUCHAN_COOKIE: <cookie header>
```

Use `hermes mcp test auchan-drive` after changes.

## Cookie/auth pitfall

Prefer the raw DevTools Network `Cookie:` header from a logged-in request to `auchan.lu`, not the browser cookie table. Browser-table copies can truncate large `PrestaShop-*` values. Do not echo cookies back to the user or store them in reusable scripts.

If the user says “not the same cart”, stop immediately: you are adding to a throwaway/server-side session, not the user’s browser cart. Do not keep retrying with cookie jars or fresh `PHPSESSID`s. Ask for the full raw Network `Cookie:` header from an authenticated cart/product request, then use exactly that header. A lone `PHPSESSID` is usually insufficient because LU cart state also depends on `PrestaShop-*`, `ps_fc`, carrier/store context, and consent cookies.

Known context signals:

- Contern cookie observed with `ps_fc=187`; set `AUCHAN_CONTEXT_PATH=contern`.
- Kirchberg cookie observed with `ps_fc=162`; Kirchberg may not have a simple `/kirchberg/` public context.
- The account dashboard `/contern/mon-compte` can be logged in and expose latest-order summary even when `/contern/historique-commandes` redirects to login. Treat each endpoint separately; do not infer full order-history access from dashboard login.

## Verification and direct tool calls

Use `hermes mcp test auchan-drive` only to verify connection/tool discovery. Do **not** guess CLI invoke syntax (`hermes mcp call`, `run`, `run-tool`, `invoke`, etc. were not valid in the 2026-07-04 session and caused loops). For actual tool calls, use the bundled direct MCP client:

```bash
node ~/.hermes/skills/services/auchan-lu-mcp/scripts/auchan-call.mjs search_product '{"query":"lait","limit":5}'
node ~/.hermes/skills/services/auchan-lu-mcp/scripts/auchan-call.mjs get_cart '{}'
```

Expected current output shape:

- `find_stores({query:'kirchberg'})` returns a static Kirchberg record with caveat note
- `find_stores({query:'contern'})` returns Contern
- `search_product({query:'lait'})` returns Klevu products, e.g. Luxlait UHT demi-écrémé 6x1l
- `get_cart` returns reachability/login state, but detailed cart parsing is not complete
- `get_orders` may only report page reachability; full order item extraction is not complete
- `get_favorites` endpoint mapping is still incomplete

See `references/contern-cart-planning-2026-07-04.md` for the Contern cart-planning session details and verified latest-order summary.
See `references/sku-mapping-pitfalls.md` for SKU-to-product mismatch cases and verified substitutions.
See `references/lu-add-to-cart-flow.md` for complete implementation details, product ID mappings, and working script templates.
See `scripts/lu-add-to-cart.sh` for a reusable bash script template.

## Add-to-cart on LU

LU does not use the FR `/cart/update` JSON endpoint. Working flow discovered 2026-07-04, verified 2026-07-05:

1. Ensure carrier/store cookie is valid. Calling `set-favorite-carrier-cookie` may rotate the PrestaShop cookie name/value.
   - POST multipart to `https://auchan.lu/<context>/module/mydeliverypopin/ajax`.
   - Fields: `action=set-favorite-carrier-cookie`, `targetCarrier=<visible carrier id>`, optionally `idAddress`, `address`, `zipcode`, `redirectUrl`.
   - Parse every `Set-Cookie`; remove deleted old `PrestaShop-*`; persist the new `PrestaShop-*` in `AUCHAN_COOKIE`.
   - Contern observed values: `ps_fc=187`; visible carrier image/id `210`.
2. Fetch product page with current cookie and extract `prestashop.static_token` or `<input name="token">`.
3. POST URL-encoded form to:
   `https://auchan.lu/<context>/panier?update=1&id_product=<numeric id>&id_product_attribute=0&token=<token>&op=up`
   with body: `ajax=1&action=update&product_page=1&qty=<increment>`.
4. Parse response JSON. Success is real only if `cart.products` contains the product with expected `cart_quantity`. A misleading `success:true` with `quantity:0` means stale cookie/carrier context.
5. Verify final cart by fetching `/panier?action=show` and parsing `var prestashop = {...}`; use `prestashop.cart.totals.total` and `prestashop.cart.products`.

**CRITICAL**: Session persistence (PHPSESSID cookie) must be maintained across ALL requests. Each request with a new PHPSESSID creates a separate cart. Use a cookie jar or persistent session.

See `references/lu-add-to-cart-flow.md` for complete implementation details, product ID mappings, and working script templates.
See `scripts/lu-add-to-cart.sh` for a reusable bash script template.

## Pitfalls

- **SKU mismatch**: User-provided SKUs may map to unrelated products (e.g., 3819404 → Harrys bread, 3819405 → Harrys bread). Always verify SKU → product mapping via `search_product` before attempting add-to-cart.
- **Brand confusion**: Père Dodu family pack may not exist; fall back to available Père Dodu SKUs (e.g., 3965146 for x4 400g) or Le Gaulois family formats (e.g., 3965185).
- **Gnocchi family pack**: Use Lustucru XXL 650g (SKU 2542822) as the closest family pack match.

## Next implementation steps

1. Implement endpoint-specific parsers; do not rely on generic `order-card` HTML assumptions.
   - Dashboard latest-order summary lives in `/contern/mon-compte` server HTML.
   - Full history route may redirect despite dashboard login; inspect effective URL and body length before parsing.
   - `var prestashop = {...}` is a huge JS object and may be JS-ish rather than strict JSON; parse with a brace-matching Node `vm` approach if needed, but avoid dumping personal data.
2. Implement detailed cart extraction from PrestaShop cart/module responses.
3. Map wishlist/favorites endpoint actions; `/module/mywishlist/action` with no action returns `{"success":false,"message":"Action inconnue"}`.
4. Patch LU `addToCart` in `mcp-auchan-drive` to use the working PrestaShop flow above instead of France `/cart/update`.

## Safety

- Never print `AUCHAN_COOKIE`.
- Avoid storing temporary scripts that embed cookies.
- If reinstalling `mcp-auchan-drive`, reapply patches or fork/package this adapter; npm reinstall will overwrite `dist/` changes.
