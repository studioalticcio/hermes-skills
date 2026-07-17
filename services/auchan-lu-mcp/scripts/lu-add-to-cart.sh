#!/bin/bash
# Script template for adding products to Auchan LU cart with persistent session
# Usage: Save as add-to-cart.sh, chmod +x, then run with your PHPSESSID

# CONFIGURATION - SET THESE VALUES
CONTEXT_PATH="contern"          # Store context (contern, bertrange, foetz)
PS_FC="187"                    # Store cookie value (187 for Contern)
PHPSESSID="YOUR_SESSION_ID"    # Get from browser DevTools > Application > Cookies

# Product list: productId,urlPath,quantity,name
# Use the mappings from references/lu-add-to-cart-flow.md
products=(
  "98834341:/jus-d-orange/98834341-jus-d-orange-sans-pulpe-90cl-4145932.html:2:Innocent orange without pulp"
  "98827206:/cordon-bleu/98827206-cordon-bleu-de-poulet-x4-400g-3965146.html:1:Cordon Bleu Père Dodu x4 400g"
  "98808806:/gnocchis/98808806-gnocchi-a-poeler-extra-fromage-format-xxl-650g-2542822.html:1:Gnocchi à poêler extra fromage XXL 650g"
  "14427:/lait-entier/14427-lait-entier-uht-35mg-6x1l-345606.html:1:Luxlait lait entier UHT 6x1l"
  "11908:/autres-sauces-froides/11908-sauce-aioli-470g-3292100.html:1:Sauce Aïoli 470g"
  "13118:/epinards/13118-epinard-feuilles-250g-3647516.html:1:Epinard Feuilles 250g"
)

# DO NOT EDIT BELOW THIS LINE

BASE_URL="https://auchan.lu/$CONTEXT_PATH"
COOKIE_JAR=$(mktemp)
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Initialize session
curl -s -A "$UA" -H "Cookie: ps_fc=$PS_FC; PHPSESSID=$PHPSESSID" -c "$COOKIE_JAR" -b "$COOKIE_JAR" "$BASE_URL/" > /dev/null

echo "Adding products to Auchan LU cart..."
echo ""

for product in "${products[@]}"; do
  IFS=':' read -r productId urlPath quantity name <<< "$product"
  
  echo "Adding: $name (x$quantity)"
  
  # Get product page and extract token
  product_url="$BASE_URL$urlPath"
  html=$(curl -s -A "$UA" -b "$COOKIE_JAR" -c "$COOKIE_JAR" "$product_url")
  
  token=$(echo "$html" | grep -o '"token":"[^"]*"' | head -1 | cut -d'"' -f4)
  
  if [ -z "$token" ]; then
    echo "  ❌ Failed to extract token for $name"
    continue
  fi
  
  # Add to cart
  cart_url="$BASE_URL/panier?update=1&id_product=$productId&id_product_attribute=0&token=$token&op=up"
  response=$(curl -s -A "$UA" -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
    -X POST "$cart_url" \
    -d "ajax=1&action=update&product_page=1&qty=$quantity")
  
  if echo "$response" | grep -q '"success":true'; then
    echo "  ✅ Added successfully"
  else
    echo "  ❌ Failed: $response"
  fi
  
  sleep 0.5
done

echo ""
echo "Verifying cart..."
cart_page=$(curl -s -A "$UA" -b "$COOKIE_JAR" "$BASE_URL/panier?action=show")

# Extract cart info
if echo "$cart_page" | grep -q 'prestashop'; then
  item_count=$(echo "$cart_page" | grep -o '"products_count":[0-9]*' | grep -o '[0-9]*')
  echo "Cart has $item_count items"
  
  # Show product names
  echo ""
  echo "Cart contents:"
  echo "$cart_page" | grep -o '"name":"[^"]*"' | sed 's/"name":"//;s/"//' | sort | uniq
fi

# Cleanup
rm -f "$COOKIE_JAR"

echo ""
echo "Done!"
