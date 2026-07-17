---
name: picard-luxembourg
description: Use when planning, pricing, or building a real Picard Luxembourg Click & Collect basket, including cross-store comparison with Auchan Luxembourg.
version: 1.0.0
metadata:
  hermes:
    tags: [picard, luxembourg, click-and-collect, groceries, mcp, shopping]
---

# Picard Luxembourg

## Reality

Picard Luxembourg is served through the Picard France commerce stack, not a separate `picard.lu` webshop.

- Catalogues and store context are hosted at `https://www.picard.fr/` (Salesforce Commerce Cloud / Demandware).
- The separate official locator is `https://magasins.picard.fr/` (Leadformance). Its public LU search currently returns no locations for `https://magasins.picard.fr/search?country=LU&query=Luxembourg`; do **not** claim two Luxembourg store identities without fresh first-party checkout evidence.
- `picard.be` redirects to a legacy/static site and is not sufficient proof of current Luxembourg Click & Collect availability.
- Never treat `picard.fr` catalogue availability as Luxembourg-store availability until the Luxembourg store has been selected and cart contents verified.
- The former `picard` MCP is catalogue-only for practical purposes: its `add_to_cart` is an in-memory cart, never a Picard order/cart. Do not imply otherwise.

See `references/public-stack-probe-2026-07-17.md` for dated request/response evidence and locator findings.

## Existing setup

Current MCP name: `picard`.

Installed source: `/home/user/.hermes/mcp/mcp-picard/`.

Wrapper: `/home/user/.hermes/mcp/mcp-picard/run-hermes.sh`.

The venv requires a Nix `libstdc++` loader path in its wrapper for `curl_cffi`; preserve that when upgrading/rebuilding.

Current exposed tools:

- Catalogue: `search_products`, `get_product_details`, `browse_category`, `get_promotions`, `compare_nutrition`
- `find_stores` (best-effort)
- Remote cart: `get_cart`, `add_to_cart(product_id, quantity)`, `update_cart_item(line_item_uuid, quantity)`, `remove_cart_item(line_item_uuid)`.

The cart adapter must use only authenticated page-context `fetch` through the loopback Chrome CDP bridge. It must not export/replay cookies or automate login, and it has no checkout capability.

## Picard commerce endpoints discovered

Base path:

`https://www.picard.fr/on/demandware.store/Sites-picard-Site/fr_FR/`

Key endpoints exposed by Picard's own storefront JavaScript:

| Purpose | Endpoint |
|---|---|
| Show cart | `Cart-Show` |
| Add a product (current storefront AJAX route) | `Cart-AddProduct?format=ajax` |
| Update / remove | `CartSFRA-UpdateQuantity` / `CartSFRA-RemoveProductLineItem` |
| Select shipping | `CartSFRA-SelectShippingMethod` |
| Pickup store candidates | `ShippingContext-FindStores` |
| Service eligibility | `LAD-GetAvailableServices` |
| Store/context flow | `ShippingContext-Get`, `ShippingContext-Calculate`, `LAD-UpdateCities`, `GoogleAddress-Autocomplete`, `GoogleAddress-Details` |

The storefront changed after the original probe: `CartSFRA-AddProduct` now returns HTTP 410. `Cart-AddToCartProduct` is the visible form target but may return 2xx without persisting a line. For a real write, navigate to the selected product page and serialise its `form.js-AddToCart` through authenticated Chrome page context, then POST it to `Cart-AddProduct?format=ajax`. Preserve the actual named `Quantity` control (capital Q), rather than adding a guessed generic `quantity` key. Do not extract or persist browser cookies, CSRF, or session values. Independently confirm the fresh `Cart-Show` product line after every mutation; a 422 means selected-store unavailability and requires a disclosed substitution. See `references/live-cart-flow-2026-07-17.md` for the verified flow.

For pickup discovery, call `ShippingContext-FindStores?latitude=<lat>&longitude=<lon>`, then `LAD-GetAvailableServices?country=<country>&zipcode=<postcode>&city=<city>&codeinsee=<code>&storeId=<optional>&shipFromStoreAddress=<optional>`. The client consumes `ispickupeligible` and `isladeligible`; treat this as authoritative over the locator.

See `references/public-stack-probe-2026-07-17.md` for request data and observed responses.

## Procedure

1. Search/select a Luxembourg Pick-up store and set the store context first.
2. Search catalogues using Picard MCP; retrieve product details only for candidates actually in contention.
3. Evaluate store-specific availability, final product price, pack size, and nutrition. Do not substitute without reporting it.
4. Build a real remote cart only after an authenticated Picard session and selected Luxembourg store are proven.
5. Execute only the current storefront form flow through page-context Chrome CDP. Keep mutations sequential; immediately fetch/parse `Cart-Show`, then independently verify a fresh authenticated tab's visible minicart count and item list. Compare product IDs, quantities, pickup store, and total against the requested basket. Never treat a 2xx mutation response as sufficient proof.
6. Before enabling a mutation endpoint, confirm its current URL-encoded parameter names from authenticated storefront JavaScript or a harmless observed request. Do not infer a line-item field such as `uuid` solely from an endpoint name. If the empty cart offers no safe confirmation source, report the blocker rather than adding a real product to discover it.
7. A smoke test is read-only: verify the bridge is loopback-only, identify an authenticated Picard page, and fetch `Cart-Show` through page context. Do not add a test item unless the user explicitly authorizes it and immediate removal plus post-cleanup `Cart-Show` verification are included.
8. Never proceed to checkout or payment. Present the verified basket for the user to collect/pay.

## Browser-session bridge

For Cloudflare/DataDome-protected commerce sessions, use the dedicated Mac Chrome profile + localhost-only SSH reverse CDP tunnel rather than server-side password login or a cookie replay. Zen/Firefox can remain the normal browser, but `mcp-leclerc-drive` requires Chrome CDP. See `references/browser-cdp-bridge.md` for the exact launch, tunnel, and verification sequence.

## Authentication and secrets

- Do not request passwords or browser cookies in chat.
- Do not log, echo, commit, or put account credentials/cookies in a skill or temporary script.
- Do not automate password login. Picard's account form has CSRF protection and may require an interactive Cloudflare browser challenge; a direct HTTP form post is not valid authentication evidence.
- First authentication and pickup-store selection happen in a visible browser. Only then may the adapter consume a safely installed browser-derived session.
- Store any final account/session secret only in `/var/lib/hermes/secrets/services.env`, using the existing `get_secret()` pattern.
- Guest/unauthenticated cart experiments must use a separate ephemeral cookie jar and must be cleared; they cannot prove the user account's cart workflow.

See `references/authentication-and-pickup-probe-2026-07-17.md` for the dated login, Cloudflare, and Strassen/Foetz target-store evidence.

## Cross-store optimization: Auchan + Picard

For the user, allocate **all frozen items** to Picard by default. Use Leclerc Foetz for non-frozen goods and Auchan Foetz only where it is competitively better. When Leclerc Foetz is the collection stop, choose Picard Foetz rather than adding a Strassen detour. Optimise against the actual shared shopping list, not per-item price in a vacuum.

1. Lock requirements: quantity, acceptable substitutions, freshness/frozen status, meal role, dietary constraints, and whether a separate pickup is worth it.
2. Query both stores for candidate products.
3. Compare normalised unit price, pack size, nutrition/ingredients where material, availability at the selected pickup store, and total additional journey friction.
4. Allocate items to the lower-cost acceptable supplier only where the marginal saving clears the second-stop threshold.
5. Produce two explicit carts, a combined total, and the reason for each allocation.
6. Add only after the user approves the proposed split; verify each remote cart separately.

## Pitfalls

- `picard.lu` is not the operating webshop; do not build against it.
- A successful `add_to_cart` from the upstream MCP means only an in-process list changed.
- Do not assume Picard France delivery eligibility proves Luxembourg pickup eligibility.
- Store selection precedes availability; product catalogue presence is insufficient.
- Do not silently turn an unavailable Picard item into an Auchan equivalent or vice versa.

## Completion criteria

A Picard basket is complete only when the authenticated, selected Luxembourg-store `Cart-Show` response contains every intended product ID and quantity, and its total and pickup context are reported back to the user.
