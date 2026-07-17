# Picard live cart flow — verified 2026-07-17

## Preconditions

- Use the dedicated authenticated Chrome profile through the localhost-only CDP bridge.
- Select the actual Luxembourg Click & Collect store and slot first. In the verified session, Strassen was store `1276`; do not infer Foetz availability from it.

## Actual add-to-cart mechanics

The visible product form posts to `Cart-AddToCartProduct`, but that route can return HTTP 200 without creating a persistent cart line.

The storefront bundle uses:

```js
$.ajax({
  type: 'POST',
  url: CommonPicard.utils.ajaxUrl(Urls.addProduct),
  data: form.serialize()
})
```

For the current storefront this resolves to:

```
POST /on/demandware.store/Sites-picard-Site/fr_FR/Cart-AddProduct?format=ajax
```

Form payload essentials:

- `cartAction=add`
- `pid=<18-digit Picard product id>`
- `sourcePage=null`
- `Quantity=<integer>` — capital Q. A lower-case `quantity` is ignored.

Fetch the product page and parse/submit its form entirely inside the authenticated browser context. Do not extract cookies or tokens.

## Verification

An HTTP 200 is not success. Immediately request `Cart-Show` in the same Chrome context and prove that the expected product label/line item exists. A `422` in this flow means the selected store cannot add that item; report it and use a clearly disclosed acceptable substitute only if allowed.

## Proven live additions

The corrected flow added and persisted Picard product `000000000000082054` (4 noix de coco givrées), then yogurt ice cream, fruit mix, Brussels sprouts, bio grilled vegetables, limande, breaded chicken, peeled shrimp, and ASC breaded salmon.
