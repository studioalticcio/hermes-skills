---
name: grocery-cart-automation
description: Use when comparing retailers and creating or maintaining authenticated grocery carts across retailer-specific web stacks, MCPs, or browser sessions.
version: 1.0.0
metadata:
  hermes:
    tags: [groceries, cart, shopping, mcp, price-comparison, click-and-collect]
---

# Grocery Cart Automation

## Scope

Use for real-account grocery carts, especially multi-store allocation. A cart is a remote, mutable state—not a shopping-list suggestion. Catalogue search, price comparison, cart mutation, pickup context, and checkout are distinct stages.

## Operating sequence

1. Capture requirements: quantities, acceptable substitutions, dietary constraints, product role, pickup/delivery preference, and the permitted number of retail stops.
2. Establish each retailer's active store before treating stock or pricing as applicable.
3. Search candidates and normalise: unit price, pack size, current promotion, nutrition/ingredients where material, and store-specific availability.
4. Allocate by *net basket value*: item saving minus an explicit second-stop cost. Do not optimise each SKU in isolation.
5. Present the proposed retailer split, per-store subtotals, substitutions, and reasons. Get approval before any real cart mutation.
6. Mutate serially. After every add, update, or removal, retrieve the authoritative remote cart and verify product, quantity, store/pickup context, and total.
7. Stop before payment, checkout confirmation, delivery-slot booking, or any irreversible purchase step unless separately and explicitly authorised.

## Authentication discipline

- Never request, repeat, log, commit, or put passwords, cookies, CSRF tokens, or payment data in MCP tool arguments, skills, or scripts.
- Prefer an interactive visible browser where anti-bot or Cloudflare/DataDome checks are involved; a successful HTTP form post is not necessarily an authenticated session.
- Treat browser-derived sessions as short-lived and retailer/store-bound. Verify account state and selected store before mutation; report reauthentication required rather than retrying credentials.
- Preserve the complete retailer session/cookie jar across calls. Do not create a new session per cart request.

## Browser-bound retailers

Some retailers reject headless HTTP or cookie replay and require requests to originate in a real browser through CDP.

- The MCP must run on the same machine as that browser, or connect through a deliberately private CDP tunnel.
- Do not expose a Chrome remote-debugging port publicly. Bind locally and tunnel it through SSH/Tailscale only.
- A no-display server cannot truthfully claim a visible-browser retailer integration works merely because the MCP process is installed.
- The user performs interactive login, CAPTCHA, MFA, and any permission prompts themselves. Automation begins only after that session is established.

## Verification standard

A mutation response such as HTTP 200 or `success: true` is insufficient. A cart change is complete only after a fresh cart read confirms:

- intended product identity;
- intended quantity;
- selected store / pickup mode;
- authoritative subtotal or total;
- any unavailable or substituted item.

On timeout or ambiguous response, read the cart before retrying. Never blindly retry a write, since it may duplicate an item.

## Common pitfalls

- **Planning cart mistaken for a retailer cart:** label local lists as plans; never call them prepared orders.
- **Catalogue ≠ store stock:** product listings do not establish Click & Collect availability.
- **Per-item optimisation:** a €0.30 saving is not worth a separate pickup run without clearing the stop threshold.
- **Silent substitutions:** preserve user choice; offer alternatives explicitly.
- **Parallel writes:** serialize mutations to avoid bot protection, rate limits, and cart races.

## Retailer adapters

Keep retailer-specific URLs, request shapes, and dated probes under `references/` in the relevant retailer skill. This umbrella governs the cross-store safety and optimisation contract; it is not a source of retailer endpoint truth.

## Completion criteria

Report a basket only as ready when every approved retailer cart has been freshly verified and the user can see the store split, pickup context, exact items, quantities, totals, and unresolved substitutions.
