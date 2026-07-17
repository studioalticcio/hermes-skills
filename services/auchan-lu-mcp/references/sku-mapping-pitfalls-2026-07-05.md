# SKU Mapping Pitfalls — 2026-07-05

## Lesson
User-provided SKUs may map to **unrelated products** on Auchan Luxembourg. Always verify via `search_product` before attempting add-to-cart.

## Observed Cases
| User SKU | Expected Product | Actual Product | Resolution |
|----------|------------------|----------------|------------|
| 3819404 | Cordon Bleu Père Dodu family pack | Pain de mie American sandwich complet 14 tranches 600g (Harrys) | Use Père Dodu x4 400g (SKU 3965146) or Le Gaulois familial (SKU 3965185) |
| 3819405 | Gnocchi au fromage family pack | Pain de mie American sandwich 7 céréales 14 tranches 550g (Harrys) | Use Lustucru XXL 650g (SKU 2542822) |

## Verified Substitutions
| Request | SKU | Product | Price | Available |
|---------|-----|---------|-------|----------|
| Cordon Bleu Père Dodu family pack | 3965146 | Cordon bleu de poulet x4 400g — Père Dodu | €4.20 | ✅ |
| Gnocchi au fromage family pack | 2542822 | Gnocchi à poêler extra fromage format XXL 650g — Lustucru | €5.00 | ✅ |

## Workflow
1. **Always search by SKU first** to confirm product identity.
2. If mismatch: search by product name + brand + "family pack" or similar qualifiers.
3. Present options to user if multiple candidates exist.
4. Only proceed with add-to-cart after user confirmation on the resolved SKU.