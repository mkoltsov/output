# Scalper plan: electronic earmuffs under US$100

## Objective and status

Add one Scalper target for **adult electronic hearing-protection earmuffs** with a verified item price plus shipping of **less than US$100**. Electronic earmuffs only is the confirmed preference.

This is an implementation plan, based on a read-only review of the current repository. No target has been added, no implementation tests have been run, and no product listings have been verified for purchase.

## 1. Define the acceptance rules

### Confirmed requirements

- Electronic earmuffs designed and documented as hearing protection.
- Strict price ceiling: qualifying total must be below US$100; US$100.00 does not qualify.

### Proposed defaults

- New, complete adult earmuffs from an identifiable manufacturer.
- Direct delivery to the configured United States destination.
- Prefer free shipping; accept verified shipping up to US$10 inclusive, provided item plus shipping remains below US$100. The US$10 shipping cap is a proposed default, not a separately confirmed preference.
- Follow the existing Scalper budget convention: item price plus shipping, before sales tax. Show tax separately when known. Do not label that amount an all-in checkout total when tax is unknown. If an after-tax ceiling is wanted, add explicit tax/mandatory-fee fields and enforce the complete checkout total instead.
- Require manufacturer-backed attenuation information for the exact model, normally a published NRR. Store the rating system with the number; do not treat different rating systems as interchangeable.
- Record battery requirements, included charging equipment, fit adjustments, and useful communication features when documented. Do not infer features from a brand name.

Exclude passive earmuffs, ordinary music/ANC headphones, children's models, accessories sold alone, empty packaging, used or defective products, incomplete devices, and products whose identity or protection rating cannot be established.

For a complete earmuff bundle, included replacement cushions are acceptable. An accessory-only listing is not. The distinction must use the primary product, rather than blindly rejecting every page that mentions cushions.

NIOSH explains that ANC headphones should not be treated as hearing protection unless labeled with an NRR, and that fit determines the protection an individual actually receives. A rating is product evidence, not a guarantee of sufficient protection for every exposure. Do not rank solely by the largest advertised dB number.

Source: [NIOSH — Provide Hearing Protection](https://www.cdc.gov/niosh/noise/prevent/ppe.html).

## 2. Files to change

Repository: `~/dev/scalper`.

1. **`deals.json`** — append the electronic-earmuff target under `targets`.
2. **`scalper.py`** — enforce the new target's category, electronic functionality, shipping limits, price consistency, and positive live-listing evidence; update optional result fields and their rendering.
3. **`test_scalper_filters.py`** — add the target, price, shipping, category, and browser-verification regression cases.
4. **`test_ebay_validation.py`** — add relevant canonical-page, unavailable-variant, and HTTP-verification cases for supported marketplace behavior.
5. **`README.md`** — document the new opt-in fields, budget convention, and isolated verification procedure.

Morning Digest integration already reads Scalper's configuration and generated results. Review `~/dev/learn/morning_digest/scalper_digest.py` and `digest_section_pages.py` during integration; change their optional presentation only if needed to display the hearing-protection evidence.

The repository already contains uncommitted changes. Preserve them and the existing target. Treat `public/` as generated output, not as the configuration source. Generate output through the application rather than hand-editing result files.

## 3. Add the target configuration

Use the existing fields:

- `id`: `electronic-earmuffs-under-100`.
- `name`: `Electronic hearing-protection earmuffs under US$100`.
- `max_price_usd`: `100`.
- `shipping_destinations`: United States only.
- `inherit_marketplace_search_hints`: `false`.
- `marketplace_search_hints`: target-specific sources for genuine hearing-protection products and direct delivery.
- `local_marketplaces`: disable the inherited OfferUp pickup exception for this delivery-only target.
- `search_intent`: find complete adult electronic earmuffs with exact model/rating evidence, verified current stock, and verified delivery pricing.
- `acceptance_criteria`: express every rule in section 1, including coupon eligibility and the exclusive total-price ceiling.
- `required_any_patterns`: useful model or product-family vocabulary for discovery. These patterns currently use OR semantics, so they cannot independently prove every requirement.
- `reject_patterns`: primary-item patterns for accessory-only, defective, incomplete, or incompatible listings; avoid broad expressions that reject legitimate bundles.
- `search_queries`: several complementary searches, for example `electronic hearing protection earmuffs NRR free shipping`, `electronic earmuffs hearing protection sale`, and exact manufacturer/model queries after their official specifications have been checked.

Do not invent a category-wide `usual_market_price_usd`. An apparent discount should be evaluated against the same exact model, condition, and included equipment.

Add new optional fields with explicit implementation:

- `product_category`: `electronic_hearing_protection`.
- `require_verified_shipping`: `true`.
- `max_shipping_usd`: `10`.
- `required_all_patterns`: optional AND requirements, if regex support is used alongside structured model evidence.

These fields are proposed extensions. They do not exist as enforced rules today; adding them to JSON alone would not make them effective. Apply the new strict checks only to targets that opt in, preserving existing target behavior.

## 4. Correct the relevant validation gaps

Current code findings:

- `normalize_deal()` already rejects totals at or above the configured maximum.
- When total is absent, unknown shipping currently becomes zero through `price + (shipping or 0)`.
- A returned `total_usd` is trusted without checking it against item price plus shipping.
- The search prompt permits estimating unknown shipping in some situations.
- HTTP/browser validation mostly searches for negative status and shipping text. It does not consistently require positive evidence of a current purchase action, selected model/variant, current price, or delivery charge.
- `--validate-config` currently checks that configuration loads and contains targets; it is not complete schema validation.

Implementation:

1. Add a target-scoped hearing-protection validator that requires electronic earmuffs and manufacturer evidence for the exact model. A seller's generic description or a rating for a related product is insufficient.
2. Reject missing, negative, non-finite, or otherwise invalid item/shipping prices. Explicit verified free delivery is zero; unknown delivery is not zero.
3. Calculate totals from verified components using decimal currency values or integer cents. If the returned total contradicts those components, reject and record the discrepancy.
4. Enforce the exclusive US$100 ceiling and inclusive US$10 shipping cap.
5. Override the prompt's estimated-shipping allowance when `require_verified_shipping` is enabled.
6. Extend configuration validation to catch duplicate target IDs, invalid regexes, incorrect option types, and invalid numeric limits. Keep optional fields backward compatible.

## 5. Require positive current availability and shipping evidence

For every candidate:

1. Open its exact canonical listing page and identify the selected product/model/variant.
2. Confirm the page represents that item, rather than a search/category page or related-product widget.
3. Require an active purchase action associated with that selected item and current stock evidence. A leftover purchase button alone is insufficient.
4. Reject sold, ended, removed, reserved, unavailable, out-of-stock, or contradictory status.
5. Read current item price from the selected listing, rather than retaining a discovery snippet's old price.
6. Confirm delivery to the configured destination and a numeric shipping amount or explicitly applicable free shipping.
7. Check thresholds and eligibility. “Free shipping over US$150” does not establish free shipping for a smaller order. Do not add filler items or assume an unknown membership to obtain a lower price.
8. Apply only currently valid, eligible discounts. Post-purchase rebates, gift-card values, uncertain coupons, or subscription conditions should not reduce the qualifying cash price.
9. Recompute the total and rerun the category, condition, price, and shipping checks.
10. Recheck selected listings immediately before notification/publication.

If access is blocked, the selected variant is unavailable, stock is ambiguous, or shipping remains “calculated at checkout,” exclude the candidate from qualifying results. A generic HTTP success response is not verification.

Use the existing managed-browser broker if rendering is necessary. Release agent-owned leases/tabs afterward. Verification stops before any purchase or payment.

## 6. Rank and display useful results

Among fully qualifying listings, rank by:

1. Clear exact-model identity and documented hearing-protection features.
2. Lower verified item-plus-shipping total, compared within the same model or meaningful product class.
3. Seller authenticity, return/warranty information, and completeness of evidence.
4. Applicable free delivery and uncomplicated purchasing conditions.
5. Documented fit/comfort and communication features; make feature differences visible rather than assuming every electronic earmuff is equivalent.

Deduplicate the same seller/model/variant listing and redundant tracking URLs. Preserve variant identifiers needed to distinguish real offers.

Each public result should show model, electronic functionality, manufacturer rating and rating system, condition, item price, shipping, qualifying total, tax status, important conditions, canonical listing URL, and verification time. Keep destination details, private postal codes, session data, and notification credentials private.

The existing Scalper section should show the strongest few matches and link to its detail page. Empty results must say that no currently verified offer qualified. Do not substitute older availability claims.

## 7. Add regression coverage

### Price and shipping

- Verified item US$99.99 plus free shipping: accept.
- Verified item US$89.99 plus US$9.99 shipping: accept at US$99.98.
- Total exactly US$100.00: reject.
- Item below the ceiling but delivery raises total to US$100 or more: reject.
- Shipping exceeds US$10 while total remains under US$100: reject under the proposed shipping policy.
- Unknown shipping, an unmet free-shipping threshold, unconfirmed destination delivery, or estimated shipping: reject.
- Negative, NaN, infinite, missing, or contradictory monetary values: reject.

### Product identity and condition

- Complete new electronic earmuffs with exact manufacturer rating evidence: accept when all other rules pass.
- Passive earmuffs or ordinary ANC headphones: reject.
- Replacement cushions, cases, or other accessories sold alone: reject.
- Complete electronic earmuffs bundled with cushions: do not reject solely for the accessory mention.
- Used, defective, incomplete, child-only, unclear-identity, or undocumented-rating products: reject under the proposed defaults.

### Live verification

- A discovery snippet says available but the exact page is sold/out of stock: reject.
- Another variant is available, but the qualifying priced variant is not: reject.
- Redirect to home/search/error page, absent purchase action, blocked browser access, ambiguous stock, or no confirmed shipping price: reject.
- Related-item stock or rating evidence must not validate the selected product.
- Expired or ineligible coupons cannot produce a qualifying price.

### Integration

- Preserve existing target definitions and behavior when the new options are absent.
- Verify target-filtered runs search only the new hearing target.
- Verify dry runs send no notifications, persist no notification state, and write only to the isolated output directory.
- Verify optional evidence fields survive serialization and render correctly in Scalper and Morning Digest.
- Verify publication omits private data and stale/unverified listings.
- Verify failing network checks reach the existing telemetry and automation-health reporting.

## 8. Validate implementation safely

Use the same Python environment as the existing runner. The following commands are for the later implementation step; they have not been executed for this plan.

```bash
cd ~/dev/scalper
umask 077
hearing_tmp=$(mktemp -d)
scalper_python=~/dev/.venvs/cron/bin/python
otel_wrapper=~/.local/bin/otel-python-cron.sh
otel_instrument=~/dev/.venvs/cron/bin/opentelemetry-instrument
printf '{}\n' > "$hearing_tmp/secrets.json"

"$scalper_python" -m json.tool deals.json > /dev/null
"$scalper_python" scalper.py --validate-config \
  --secrets "$hearing_tmp/secrets.json"
"$scalper_python" -m unittest -q
git diff --check

"$otel_wrapper" scalper "$otel_instrument" "$scalper_python" scalper.py \
  --target electronic-earmuffs-under-100 \
  --dry-run \
  --secrets "$hearing_tmp/secrets.json" \
  --state "$hearing_tmp/state.json" \
  --public-dir "$hearing_tmp/public" \
  --log-file "$hearing_tmp/run.log"
```

Before the live dry run, confirm that a scheduled Scalper run is not active and coordinate with its existing lock. Do not interrupt another running job.

An empty temporary secrets file avoids loading the private ntfy topic during validation. The current validation command otherwise logs its complete private notification URL. If implementation changes this logging, redact the topic rather than displaying it.

`--dry-run` still writes generated pages, so the temporary `--public-dir` is essential. Inspect isolated results, recheck exact selected listings, and retain useful debugging evidence privately. Remove temporary files after review. Do not publish this test directory or raw private source data.

Exercise the real Morning Digest integration with `--email --no-send` after the new target has produced verified results. Check the delivered-price wording, target visibility, ordering, detail-page link, browser rendering, and stale-data guards.

## 9. Monitoring and rollout

Reuse the existing Scalper runner and schedule. Add no new cron entry, timer, or long-running service.

The current runner already uses the local OTel wrapper with service name `scalper`. Extend that instrumentation for any new verification path: sample every third API call, record every failed call/job, export through the existing node-textfile metrics directory, and surface failures in the Microserver automation snapshot. Keep unknown stock/shipping rejections distinguishable from network or parsing failures.

After tests and the isolated live run pass, let the existing recurring run load the new configuration. A job that has already started will keep the configuration it loaded at startup.

Check the generated target results and the normal Digest integration. Review public output for personal data and credentials before publishing, then verify both the published branch content and the live page. Preserve unrelated work and artifacts.

## 10. Completion criteria

- [ ] One electronic-earmuff target is configured with the confirmed type and strict US$100 ceiling.
- [ ] Proposed condition, tax, and shipping defaults are documented and enforced.
- [ ] Missing shipping never becomes free shipping for this target.
- [ ] Current price, product identity, manufacturer rating, stock, and delivery cost are positively verified.
- [ ] Price and shipping boundaries, rejection cases, and existing-target compatibility tests pass.
- [ ] An isolated instrumented live run produces only verified offers, or an honest empty result.
- [ ] Real Morning Digest preview/browser validation passes and includes the new target/detail link.
- [ ] Published output is privacy checked and verified live.
- [ ] No extra scheduler or purchase action is introduced.

Rollback if needed: remove or disable only the new target and its opt-in behavior. Retain unrelated configurations and useful verification logs.
