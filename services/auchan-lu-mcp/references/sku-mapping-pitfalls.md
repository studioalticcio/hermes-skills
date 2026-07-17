# SKU Mapping Pitfalls and Verified Substitutions

## Verified SKU → Product Mappings (2026-07-05)

| Requested | User SKU | Product ID | Verified Product | Notes |
|-----------|----------|------------|-----------------|-------|
| Innocent orange without pulp | 4145932 | 98834341 | Jus d'orange sans pulpe 90cl | Exact match |
| Cordon Bleu Père Dodu | 3965146 | 98827206 | Cordon bleu de poulet x4 400g | Père Dodu brand |
| Gnocchi au fromage family pack | 2542822 | 98808806 | Gnocchi à poêler extra fromage format XXL 650g | Lustucru brand, closest family pack |
| Luxlait lait entier UHT 6x1l | 345606 | 14427 | Lait entier UHT 3.5%MG 6x1l | Exact match |
| Aioli | 3292100 | 11908 | Sauce Aïoli 470g | Exact match |
| Spinach leaves | 3647516 | 13118 | Epinard Feuilles 250g | Fresh spinach, not frozen |

## Common Pitfalls

### Invalid SKU Mappings
The following SKUs were found to map to INCORRECT products:

| Invalid SKU | Incorrectly Mapped To | Correct SKU | Correct Product |
|-------------|----------------------|-------------|-----------------|
| 3819404 | Pain de mie American | 3965146 | Cordon bleu de poulet x4 400g |
| 3819405 | Pain de mie 7 céréales | 2542822 | Gnocchi à poêler extra fromage XXL 650g |

**Always verify SKU → product mapping via `search_product` before attempting add-to-cart.**

### Brand Confusion
- **Père Dodu**: The family pack format may not always be available. Fall back to standard x4 400g (SKU 3965146) or Le Gaulois family formats (SKU 3965185).
- **Luxlait vs Candia**: Candia lait entier was not found; Luxlait (SKU 345606) is the verified substitute for UHT whole milk 6x1l.

### Product Format Variations
- **Gnocchi**: Multiple formats exist. For "family pack", use the XXL 650g (SKU 2542822).
- **Spinach**: Fresh (SKU 3647516, 250g) vs frozen alternatives. User confirmed preference for fresh.

## Search Strategy

When user provides a SKU:
1. First try exact SKU search via `search_product`
2. If no results, try the product name/description
3. If multiple results, verify brand and format match
4. Always confirm with user if substitution is needed

## Verification Commands

```bash
# Verify a SKU mapping
node ~/.hermes/skills/services/auchan-lu-mcp/scripts/auchan-call.mjs search_product '{"query":"4145932","limit":1}'

# Search by product name
node ~/.hermes/skills/services/auchan-lu-mcp/scripts/auchan-call.mjs search_product '{"query":"jus d orange sans pulpe","limit":5}'
```
