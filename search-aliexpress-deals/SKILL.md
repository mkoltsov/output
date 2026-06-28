---
name: search-aliexpress-deals
description: Find rigorously verified AliExpress deals for a specified country, city, and postcode. Use for AliExpress bargains, product recommendations, price comparisons, or requests for goods deliverable to a location. Recommend only exact variants proven orderable in a live final pre-payment checkout for that destination, with the real existing-customer price, VAT, shipping, delivery estimate, seller quality, trustworthy reviews, exact-variant price history, and comparable local delivered price verified in the same session.
---

# Search AliExpress Deals

Return fewer results rather than misleading ones. A search result, aggregator, tracker, product page, or add-to-cart action does not prove the final price or destination availability.

## Set the verification context

Determine the destination country and the city/postcode fields AliExpress uses. Use the location already supplied. Ask for a postcode only when checkout cannot verify delivery without it. Never expose or publish a full saved address.

Determine the requested categories, exclusions, quantity, budget, delivery deadline, and compatibility constraints such as dimensions, voltage, plug, language, radio bands, warranty, and operating system.

Use a normal existing-customer account state by default. Exclude new-user, invite, app-install, targeted, and first-order prices unless the user explicitly confirms eligibility and the discount appears at final checkout.

## Discover candidates

Use live search, independent deal communities, aggregators, and price trackers only to find candidates. Never quote their displayed price as the current executable price.

For every promising candidate:

1. Identify the exact model, SKU, capacity, colour, bundle, plug, ship-from location, and quantity.
2. Compare the identical variant with reputable local retailers, including local VAT and delivery.
3. Find substantive independent testing or established enthusiast evidence. Do not rely on seller reviews or affiliate listicles as independent validation.
4. Read recent negative and photo reviews for substitutions, counterfeits, fake capacity, unsafe construction, misleading bundles, and warranty problems.

For chargers, power banks, batteries, mains-powered products, protective equipment, and other safety-sensitive goods, require reputable-brand provenance and independent technical or safety testing. Exclude unverifiable products.

## Reject misleading price patterns

Actively check for these traps:

- A low "from" price belonging to a cable, case, partial kit, lower capacity, or different model.
- A price per piece that requires buying several pieces.
- Choice, Bundle Deals, or free-shipping prices that require unwanted additional products or a minimum basket.
- Coins, cashback, store credit, app-only, new-user, invite, or targeted discounts unavailable to an ordinary existing customer.
- Coupons that are exhausted, country-restricted, minimum-spend dependent, or not visibly applied.
- A product page changing price, seller, warehouse, or variant in the cart.
- VAT, shipping, remote-area fees, or currency conversion omitted from the headline price.
- A price tracker combining multiple variants or reporting only the cheapest SKU.

Use price history only when it can isolate the identical item and variant. Otherwise label historical comparison unavailable and do not infer a bargain from the chart.

## Require live Poland/destination checkout proof

Use an interactive browser with the user's AliExpress destination selected. For each recommended item:

1. Set the exact destination country and available city/postcode fields before reading the price.
2. Open the live listing and select the exact recommended variant, warehouse, and quantity.
3. Confirm the listing says it can ship to that destination and shows an arrival estimate.
4. Add the item to the cart. Confirm that the cart line retains the same item ID, seller, variant, warehouse, quantity, and price.
5. Continue to the final order-review screen immediately before payment. Never place the order.
6. Confirm the saved destination is the requested location without revealing the full address.
7. Record the merchandise subtotal, discounts actually applied, VAT/tax, shipping, currency, final payable total, shipping service, tracking status, and estimated delivery range.
8. Compare the listing, cart, and order-review totals. Treat the final payable checkout total as authoritative and explain any difference.
9. Recheck the final screen immediately before reporting; stale checkout evidence does not qualify.

If login, CAPTCHA, missing address access, app-only pricing, or any other barrier prevents final order review, classify the item as **unverified** and exclude it from recommendations. It is acceptable to return **no verified deals**. Never substitute a tracker price or another country's checkout.

## Require reasonable delivery

Apply the user's deadline when provided. Otherwise require tracked delivery and use these defaults:

- Up to 14 calendar days: acceptable.
- 15–21 calendar days: acceptable only when the delivered saving is at least 30%.
- More than 21 calendar days, no estimate, or untracked shipping: reject.

Normally reject shipping that exceeds 25% of the merchandise price. For cheap products, allow an exception only if the final delivered total remains at least 25% below the identical local option.

Prefer a Polish or EU warehouse when a small premium materially improves delivery, returns, or warranty. Do not hide a minimum-order requirement by padding the basket.

## Require product, seller, and price quality

Normally require:

- Item rating at least 4.7/5, at least 100 completed orders, and at least 50 substantive reviews for that listing; allow a documented exception for a new listing in an established official store.
- Seller feedback at least 96%, established history, and an official or authorised store when counterfeit risk exists.
- No material conflict between the listing specifications, cart variant, official documentation, and independent review.
- Final delivered price at least 20% below the best reputable local delivered price for the identical variant.
- Final price within 5% of a trustworthy 90-day low for that exact variant, when exact-variant history exists.

For items above 250 zł without equivalent Polish/EU warranty and returns, require at least a 30% saving and explicitly account for the warranty risk. Do not call an item a deal merely because it is unavailable locally.

## Classify evidence

Use exactly these labels:

- **Verified deal**: passed final destination checkout and every quality gate.
- **Verified available, not a deal**: checkout works, but price, delivery, or quality threshold fails.
- **Unverified lead**: promising discovery that could not reach final destination checkout.
- **Unavailable**: exact variant cannot be ordered to the destination.

Only **Verified deal** items belong in the recommendation list. Do not present unverified leads as alternatives unless the user explicitly asks to see them.

## Report an audit trail

For every verified deal provide:

- Exact product, variant, quantity, seller, item ID, and direct AliExpress URL.
- Final payable amount in checkout currency and in local currency when different, including VAT and shipping.
- Shipping origin, tracked service, and estimated delivery dates.
- Statement that final pre-payment checkout accepted the specified country and postcode, with verification date and local time.
- Best identical local delivered price, source, and calculated saving.
- Exact-variant price-history result or an explicit statement that reliable history was unavailable.
- Independent-review evidence, seller metrics, and important drawbacks.
- Any eligibility condition that the checkout proved.

Finish with counts for verified deals, verified non-deals, unavailable items, and unverified leads. If no item passed, say so plainly and explain the dominant failure reasons without padding the answer with weaker recommendations.
