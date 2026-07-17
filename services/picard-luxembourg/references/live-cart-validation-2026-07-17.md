# Picard browser cart: current storefront validation

## Current add mechanism

The product page currently renders a `form.js-AddToCart` whose action is:

`Cart-AddToCartProduct`

The obsolete `CartSFRA-AddProduct` returned HTTP 410. Do not use it.

The current form contains the product ID, a storefront-specific quantity input name, and a per-page CSRF field. Constructing a generic request with `pid` plus `quantity` may return HTTP 200 **without actually changing the cart**.

## Required proof of a successful cart mutation

1. Submit the exact product form inside the authenticated browser context; preserve its named quantity field and CSRF data internally.
2. Read `Cart-Show` after the mutation.
3. Independently open or inspect a fresh authenticated Picard tab and confirm the visible minicart quantity and item list changed.
4. Only then report the item as added. An HTTP 2xx response, a generic JSON acknowledgement, or a same-document scrape is not proof.

## Current C&C context learned

A Picard Luxembourg Click & Collect selection can be present in the header while the cart is still empty. Do not infer cart state from the selected slot.

## Safety

Keep CSRF fields, cookies, account fields, and analytics payloads in browser execution only. Do not print full cart HTML or raw product-form HTML; extract only non-sensitive product names, quantities, totals, and store context.
