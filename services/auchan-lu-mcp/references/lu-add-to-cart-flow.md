# LU Add-to-Cart Flow (Verified 2026-07-05)

## Working Flow

The Auchan Luxembourg (auchan.lu) PrestaShop implementation uses a **4-step manual flow** for adding products to cart. This is different from the France `/cart/update` JSON endpoint.

### Prerequisites
- Valid store context cookie: `ps_fc=187` for Contern
- Valid PHPSESSID for session persistence
- User must be on the Contern context path: `/contern/`

### Step-by-Step

1. **Set store context cookie**
   ```
   ps_fc=187  (Contern)
   ```

2. **Fetch product page**
   ```
   GET https://auchan.lu/contern/{category}/{productId}-{name}-{offerId}.html
   ```
   Extract `prestashop.static_token` from the HTML:
   - Look in `var prestashop = {...token:"VALUE"...}` JS object
   - Or `<input type="hidden" name="token" value="VALUE">`

3. **POST to cart endpoint**
   ```
   POST https://auchan.lu/contern/panier?update=1&id_product={productId}&id_product_attribute=0&token={token}&op=up
   
   Body (URL-encoded):
   ajax=1&action=update&product_page=1&qty={quantity}
   ```

4. **Verify cart**
   ```
   GET https://auchan.lu/contern/panier?action=show
   ```
   Parse `var prestashop = {...}` object for:
   - `prestashop.cart.products` - array of cart items
   - `prestashop.cart.products_count` - total item count
   - `prestashop.cart.totals.total` - cart total

### Critical Notes

- **Session persistence is required**: Each request must use the SAME PHPSESSID cookie. Using a new session for each request creates separate carts.
- **Token is per-page**: The `prestashop.static_token` is embedded in each product page and must be extracted fresh for each product.
- **Success indicator**: The POST response contains `"success":true` but this can be misleading. True verification requires checking the cart contents after.
- **Guest vs logged-in**: Guest carts may show `products_count: 0` in some responses even when items are present. Always verify via the `/panier?action=show` endpoint.

### Product ID Mapping

| User SKU | Product ID | Name | URL Path |
|----------|------------|------|----------|
| 4145932 | 98834341 | Jus d'orange sans pulpe 90cl | /jus-d-orange/98834341-jus-d-orange-sans-pulpe-90cl-4145932.html |
| 3965146 | 98827206 | Cordon bleu de poulet x4 400g | /cordon-bleu/98827206-cordon-bleu-de-poulet-x4-400g-3965146.html |
| 2542822 | 98808806 | Gnocchi à poêler extra fromage XXL 650g | /gnocchis/98808806-gnocchi-a-poeler-extra-fromage-format-xxl-650g-2542822.html |
| 345606 | 14427 | Lait entier UHT 3.5%MG 6x1l | /lait-entier/14427-lait-entier-uht-35mg-6x1l-345606.html |
| 3292100 | 11908 | Sauce Aïoli 470g | /autres-sauces-froides/11908-sauce-aioli-470g-3292100.html |
| 3647516 | 13118 | Epinard Feuilles 250g | /epinards/13118-epinard-feuilles-250g-3647516.html |

### MCP Server Limitation

The `mcp-auchan-drive` server's `add_to_cart` tool uses the France `/cart/update` JSON endpoint, which **returns 404 for auchan.lu**. The LU implementation requires the PrestaShop form POST flow described above. To add items to cart via MCP, you must:

1. Use `search_product` to get the product details (populates internal cache)
2. Manually implement the 4-step flow with the product ID and a persistent session

The MCP server's cookie provider uses `AUCHAN_COOKIE` environment variable which only contains `consentement_cookies`, not PHPSESSID. For cart operations, you need the full session cookies including PHPSESSID.

### Working Script Template

```bash
#!/bin/bash
# Add to cart with persistent session
COOKIE_JAR=$(mktemp)
BASE_URL="https://auchan.lu/contern"

# Set your PHPSESSID and ps_fc here
curl -s -A "Mozilla/5.0" -H "Cookie: ps_fc=187" -c "$COOKIE_JAR" -b "$COOKIE_JAR" "$BASE_URL/" > /dev/null

# For each product
product_url="$BASE_URL/{urlPath}"
html=$(curl -s -A "Mozilla/5.0" -b "$COOKIE_JAR" -c "$COOKIE_JAR" "$product_url")
token=$(echo "$html" | grep -o '"token":"[^"]*"' | head -1 | cut -d'"' -f4)

curl -s -A "Mozilla/5.0" -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
  -X POST "$BASE_URL/panier?update=1&id_product={productId}&id_product_attribute=0&token=$token&op=up" \
  -d "ajax=1&action=update&product_page=1&qty={quantity}"

rm -f "$COOKIE_JAR"
```

### Error Patterns

- **404 on `/cart`**: Using France endpoint on LU site
- **Token extraction fails**: Product page HTML structure changed, or wrong context path
- **Cart shows 0 items**: Session not persistent between requests (new PHPSESSID each time)
- **"success":true but quantity:0**: Stale cookie/carrier context - need to re-authenticate
