# Picard Chrome cart adapter — 2026-07-17

## Proven state

- Dedicated Mac Chrome is reached through a localhost-only reverse CDP tunnel at `http://127.0.0.1:<PORT>`.
- An authenticated Picard account and **Click & Collect Picard Strassen** selection were verified in the visible browser (store ID `1276`; a selected pickup slot was displayed).
- A `Cart-Show` request made in the page context returned HTTP 200 and an empty cart.
- Closing the Picard tab did **not** erase the browser profile/session; opening a new `https://www.picard.fr/` tab restored authenticated account and C&C context.

## Current add-to-cart contract

The former route `CartSFRA-AddProduct` returned HTTP 410 on the current storefront. Do not use it.

On a live product page, inspect the product form (`form.js-AddToCart`). The observed form action was:

`https://www.picard.fr/on/demandware.store/Sites-picard-Site/fr_FR/Cart-AddToCartProduct`

The form carries `cartAction=add`, `pid`, quantity controls, and browser/session-bound hidden values. The safe pattern is:

1. Navigate the authenticated Chrome tab to the exact product page.
2. Locate its `form.js-AddToCart` in **that page context**.
3. Build `FormData(form)` and change only the requested quantity.
4. POST it to `form.action` from the same page context (`credentials: 'same-origin'`).
5. Immediately fetch `Cart-Show` in the page context and verify product IDs, quantities, total, store, and slot.

Never extract, print, save, or replay the form's hidden CSRF/session values. The live page's add buttons may begin disabled while availability/UI state settles; do not interpret a disabled button as a reason to bypass store-context verification.

## Adapter implementation status

`/home/user/.hermes/mcp/mcp-picard/` gained a browser/CDP remote-cart adapter (`src/api/cart.py`) and MCP tools. Its initial mutation implementation still targets the stale `CartSFRA-AddProduct` route and must be patched to use the live product-form pattern above before any cart mutation. Tests passing for the adapter are unit-level; they do not establish a live cart write.
