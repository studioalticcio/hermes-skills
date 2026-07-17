# Picard public-stack probe — 2026-07-17

Scope: unauthenticated, non-destructive site and endpoint inspection. Evidence is current as of the date above; revalidate before adapting.

## Architecture

- Commerce: `https://www.picard.fr/`, Salesforce Commerce Cloud / Demandware, locale path `Sites-picard-Site/fr_FR`.
- Store locator: `https://magasins.picard.fr/`, Leadformance front end.
- `picard.be` redirects `www.picard.be` to a small legacy/static site and is not evidence of active LU C&C operations.

## Official locator and LU result

- Public form: `GET https://magasins.picard.fr/search?country=LU&query=<place>`.
- Form fields: `country`, `query`, optional `lat`, `lon`, `geo`.
- The home page offers `LU` in its country selector and exposes a Click & Collect service filter (value `5f877b73b67e79225d17e7ed`).
- Live request `https://magasins.picard.fr/search?country=LU&query=Luxembourg` returned `locations: []` and `hitsTotal: 0`. Do not assert the identities of “two Luxembourg stores” from unverified third-party listings.
- Locator script: `https://storage.leadformance.com/assets/production-front-offices/v3-picard/v1.23.1/build/home.min.js`.
- Locator config names `https://autosuggest.leadformance.com/cities` for city suggestions. Its expected body is `{query, language:'fr', countries:['lu'], hitsPerPage:3}`; direct non-browser POST yielded HTTP 403.

## Commerce: verified public calls

Base: `https://www.picard.fr/on/demandware.store/Sites-picard-Site/fr_FR/`.

### Cart

Verified:

```http
POST CartSFRA-AddProduct
Content-Type: application/x-www-form-urlencoded

pid=000000000000073097&quantity=1
```

The HTTP 200 JSON had `quantityTotal: 1` and these `cart.actionUrls`:

- `CartSFRA-RemoveProductLineItem`
- `CartSFRA-UpdateQuantity`
- `CartSFRA-SelectShippingMethod`
- `CartSFRA-AddCoupon`
- `CartSFRA-RemoveCouponLineItem`

Read route: `Cart-Show`. Product tiles use `CartSFRA-AddProduct`; do not implement legacy guessed `Cart-AddProduct` / `Cart-MiniAddProduct` routes without testing.

### Pickup/store eligibility

Page-injected route names:

- `ShippingContext-Get`
- `ShippingContext-Calculate`
- `ShippingContext-FindStores`
- `LAD-GetAvailableServices`
- `LAD-UpdateCities`
- `GoogleAddress-Autocomplete`
- `GoogleAddress-Details`
- `LAD-ClearDeliveryModeContext`

Recovered JS request shapes:

```http
GET ShippingContext-FindStores?latitude=<lat>&longitude=<lon>
GET LAD-GetAvailableServices?country=<country>&zipcode=<postcode>&city=<city>&codeinsee=<code>&storeId=<optional>&shipFromStoreAddress=<optional>
```

Client checks `isladeligible` and `ispickupeligible`. Use this chain as the source of checkout-eligible pickup stores; public locator results are secondary.

### Login/account routes observed

- `Login-LoginForm`
- `Login-Logout`
- `Account-ShowSignupForm`
- `Account-FidelityRegister`
- `Account-DeleteAlias`

Capture a real browser login submission before implementing it: it may include CSRF/anti-bot fields.

## Session handling

Observed SFCC session state includes `dwsid` (HttpOnly), `sid`, `dwac_*`, and `dwanonymous_*`. Preserve a full cookie jar across address/store-context and cart calls. No clear standalone selected-store cookie was observed before store selection; it may be server-session state. A fresh guest jar is never evidence about a user's authenticated cart.
