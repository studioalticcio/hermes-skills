# Picard authentication and pickup probe — 2026-07-17

## Authentication

- Account page: `https://www.picard.fr/mon-compte`.
- Form action: `Login-LoginForm` under the SFCC base path.
- Fields observed: `dwfrm_login_username`, `dwfrm_login_password`, `csrf_token`.
- A direct HTTP login attempt reached Picard's Cloudflare browser challenge and did not establish an authenticated account session.

### Operating implication

Use an interactive, visible browser session for first authentication and Cloudflare completion. Do not attempt password-based HTTP login or save passwords. The adapter should consume a safely installed browser-derived session only after confirming authenticated account state and pickup-store context.

## Pickup stores

The user's intended Picard pickup options are Strassen and Foetz. Treat them as user-supplied targets, not currently verified store IDs. Resolve the exact store identifier/name from the authenticated Picard pickup flow before persisting or mutating a cart.

## Cart boundary

The discovered `CartSFRA-AddProduct` guest-cart request proves only anonymous cart mutation. It does not prove a Picard Luxembourg pickup context, stock allocation, or account-cart persistence. Require all three after browser authentication:

1. authenticated account confirmation;
2. selected Strassen/Foetz pickup store confirmation;
3. fresh `Cart-Show` verification after every cart mutation.
