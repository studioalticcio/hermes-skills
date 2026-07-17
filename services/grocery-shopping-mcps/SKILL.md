---
name: grocery-shopping-mcps
description: Use when planning groceries or connecting supermarket MCPs for the user in Luxembourg. Distinguish live catalogues, local planning carts, and real checkout state.
version: 1.0.0
metadata:
  hermes:
    tags: [groceries, mcp, luxembourg, shopping, meal-planning]
    related_skills: [auchan-lu-mcp, mealie]
---

# Grocery Shopping MCPs

## Overview

Use MCP catalogue data to ground a practical grocery list in actual stock and price. Treat checkout/cart integration as a separate capability: a search result or a local planning cart is not an order.

## When to Use

- Building a week’s grocery basket around time, nutrition, cost, or cooking constraints.
- Adding, testing, or repairing a supermarket MCP.
- Comparing frozen-convenience options with a fresh-food plan.

Do not use this instead of the store-specific skill when placing or modifying an authenticated real cart.

## Meal-planning loop

1. Start with the limiting constraint: household size, meal count, cooking-time ceiling, dietary exclusions, and existing staples. Completion: the list solves the stated friction rather than optimising an abstract diet.
2. Search the relevant store catalogue for the selected protein, carbohydrate, vegetable, fruit, and fallback meal components. Prefer verified availability over generic product claims. Completion: every named product is a live result or is labelled a generic staple.
3. Build redundancy deliberately: include genuinely low-effort fallback meals for tired evenings, rather than assuming meal prep will happen. Completion: the proposed basket works with the stated time ceiling.
4. State cart semantics before any cart action. Add to a real store cart only on an explicit request; a local MCP cart remains a planning list.

## Store boundaries

| Store MCP | Best use | Cart semantics |
|---|---|---|
| Auchan LU | Luxembourg Drive catalogue and authenticated Drive cart work | Can affect the real cart only with an intact authenticated cookie and verified LU add-to-cart flow. Load `auchan-lu-mcp`. |
| Picard | French frozen catalogue, nutrition comparison, promotions and local list planning | The MCP is catalogue-only vis-à-vis Picard checkout; its cart is in-memory and not synchronised to a Picard account. |

## Picard MCP installation

The maintained local installation pattern and its NixOS runtime workaround are in `references/picard-mcp-nixos.md`.

After adding an MCP with Hermes, run both `hermes mcp test <name>` and one live tool call. `mcp test` confirms startup/tool discovery, not that the store catalogue is actually reachable.

## Pitfalls

1. **France catalogue mistaken for Luxembourg availability.** Picard MCP targets `picard.fr`; its displayed prices and products are not a Luxembourg-store inventory guarantee.
2. **Local cart mistaken for checkout.** Never describe `add_to_cart` in the Picard MCP as having added an item to a user’s Picard account or order.
3. **Inventory-only meal plans.** A good basket contains a low-effort branch for fatigue; raw ingredients alone do not answer a “too tired to cook” constraint.
4. **Discovery mistaken for verification.** A server that exposes tools can still fail on its first web request. Exercise one catalogue search before reporting success.

## Verification checklist

- [ ] Store geography and catalogue scope are explicit.
- [ ] Product availability is backed by a live query where it matters.
- [ ] Any cart action has the right semantics and was explicitly requested.
- [ ] MCP transport discovery and one live catalogue call both succeeded.
