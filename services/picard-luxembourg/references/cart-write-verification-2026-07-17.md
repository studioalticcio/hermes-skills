# Picard cart-write verification — 2026-07-17

## Current storefront observations

- Product pages expose a real form endpoint: `POST Cart-AddToCartProduct`, not the previously documented `CartSFRA-AddProduct` route (which returned HTTP 410).
- A product form currently includes at least `cartAction=add`, `pid`, `sourcePage`, and uppercase `Quantity` (for example, `1.0`).
- Product forms may have no visible CSRF input; do not manufacture one. If a CSRF field exists, keep its value inside Chrome/browser form submission.
- A `200` response from the form post, or even `Cart-Show` HTTP 200 afterwards, did **not** prove that a Picard cart line existed in this session.

## Required write proof

After every intended add/remove/update:

1. Read the visible Picard minicart count in the same authenticated browser tab **and** inspect the remote cart page for the intended product ID/name and quantity.
2. Re-open a fresh same-profile Picard tab and verify the count/item persists. This catches tab-local or no-op form submissions.
3. Only then report an item as added.

If either proof fails, report the cart as empty/unverified and do not describe a basket, total, or pickup allocation as real.

## Pickup context

A selected C&C UI can show a slot while the cart page lacks a store context. Confirm selected pickup store and slot from the cart/checkout state before writing products. In this session Strassen was observed as pickup store ID `1276`; user prefers Foetz when paired with Leclerc Foetz, subject to browser-derived availability.
