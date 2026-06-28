---
name: search-aliexpress-deals
description: Find and rank genuinely good AliExpress products for a specified delivery country, city, and postcode. Use when the user asks for AliExpress deals, bargains, product recommendations, price comparisons, or goods available to order in their location. Verify the exact variant at cart or pre-payment checkout, destination eligibility, stock, VAT, shipping charge, estimated delivery, seller quality, price history, local alternatives, and independent reviews before calling anything available or a deal.
---

# Search AliExpress Deals

Find products that are good purchases at their delivered price and can actually be ordered to the user's destination. Treat aggregator pages as discovery evidence, never as availability proof.

## Establish the request

Determine:

- Destination country and, when AliExpress requires it, city and postcode.
- Product categories, exclusions, budget, quantity, and any size, voltage, plug, language, warranty, or compatibility constraints.
- Maximum acceptable delivery time when the request is time-sensitive.

Use the location already supplied in the conversation. If only a country is known, search with that country and clearly state that postcode-level verification remains pending. Ask for a postcode only when the site cannot expose destination-specific checkout information without it.

## Research candidates

Search current sources; do not rely on remembered prices.

1. Discover candidates on AliExpress and at least one independent deal community or aggregator.
2. Check price history with PriceArchive, AliHelper, or another tracker. Ignore the seller's crossed-out reference price.
3. Compare the exact model and variant against current local retailers and price-comparison sites in the destination country.
4. Find at least one substantive independent review or measurement. Prefer professional testing, official technical documentation, and established enthusiast communities over affiliate listicles.
5. For chargers, power banks, batteries, mains-powered products, protective equipment, or other safety-sensitive goods, require reputable-brand provenance and independent safety/electrical testing. Exclude unverifiable products.

Search broadly, but spend checkout-verification effort only on candidates likely to pass the deal threshold.

## Verify orderability at the destination

Perform these checks for the exact recommended variant:

1. Open the live AliExpress product page, not a search snippet or cached tracker.
2. Set the ship-to country and available city/postcode fields to the user's destination.
3. Select the exact model, colour, capacity, plug, bundle, and ship-from warehouse being recommended.
4. Confirm the variant is in stock and the quantity control permits the requested quantity.
5. Add it to the cart and proceed as far as the final review immediately before payment. Never submit the order.
6. Record the item price, discounts that actually apply, VAT/tax, shipping charge, final delivered total, shipping service, and estimated arrival date or range.
7. Reject the candidate if AliExpress says it cannot ship there, the variant changes at checkout, stock disappears, delivery details remain hidden, or checkout cannot be verified.

Do not claim that an item is available merely because its page opens. If login, CAPTCHA, address access, or another barrier prevents the cart check, label it **unverified**, keep it out of the main recommendations, and state the exact missing proof.

## Judge delivery

Apply the user's limit when provided. Otherwise use these defaults:

- Up to 14 calendar days: good.
- 15–21 calendar days: reasonable.
- More than 21 calendar days: exclude unless the saving is exceptional and the user said speed is unimportant.
- Untracked shipping or no delivery estimate: exclude.

Judge shipping cost through the final delivered total, not in isolation. Normally require both:

- Shipping no greater than 25% of the item price, unless the delivered total still clearly wins for a very cheap product.
- Delivered total at least 15% below the best trustworthy local price for the identical variant.

Prefer EU/local warehouses when their modest premium materially improves delivery or returns. Account for minimum-order free-shipping thresholds without padding the basket with unwanted goods.

## Judge product and seller quality

Use these as defaults, not substitutes for judgment:

- Product rating at least 4.7/5 with meaningful recent review volume.
- Store feedback at least 95%, established operating history, and preferably an official or authorised store.
- Recent photo reviews consistent with the advertised variant.
- No recurring reports of counterfeits, substituted components, fake capacity, unsafe construction, or warranty avoidance.

Read low and recent reviews. Exclude suspicious review patterns. For components, confirm exact chipset, dimensions, interfaces, voltage, protocol, regional bands, and operating-system compatibility.

## Decide whether it is a deal

Recommend an item only when all mandatory gates pass:

- Exact variant is orderable to the stated destination.
- Final delivered total and tracked delivery estimate are visible.
- Delivery is reasonable.
- Product and seller evidence are credible.
- Delivered price beats the comparable local option by at least 15%, or provides a clearly explained capability unavailable locally.
- Current price is normally within 10% of its credible 90-day low after applied coupons.

Treat personalised Coins prices, new-user discounts, app-only offers, cashback, and coupon codes as conditional until they visibly apply in that user's cart. Never include unearned cashback in the purchase price. Distinguish historical lows from current executable prices.

## Report results

Lead with the strongest verified purchases. For each one provide:

- Exact product and variant.
- Clickable AliExpress item URL.
- Final delivered price in the user's local currency, including VAT and shipping.
- Shipping origin, service, and estimated arrival.
- Evidence that checkout accepted the destination, with verification date and time.
- Local comparison price and percentage saving.
- Price-history verdict.
- Independent-review verdict and material drawbacks.
- Seller/store evidence.

Then provide a short **wait/skip** section for attractive-looking candidates that failed price, delivery, seller, or availability checks. Keep unverified items separate from verified recommendations.

Never describe a result as verified after its price or availability evidence has gone stale. Recheck live checkout information in the same session immediately before reporting.
