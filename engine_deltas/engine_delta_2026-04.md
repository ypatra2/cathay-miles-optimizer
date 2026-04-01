# Cathay Miles Engine — Deep Research Delta Report
## Date: March 2026

**Executive Summary and Key Findings**
The optimization of Asia Miles accrual via Hong Kong credit cards requires an intricate understanding of constantly shifting bank policies, Merchant Category Codes (MCC), and promotional tiers. Based on exhaustive research into the March 2026 landscape of the four target credit cards (Standard Chartered Cathay Mastercard, HSBC EveryMile VISA, HSBC Red Mastercard, and HSBC VISA Signature), several critical updates must be injected into the existing Python calculation engine. 

The evidence leans toward a broader industry crackdown on "passive" or "low-margin" spending categories. E-wallets (PayMe, AlipayHK, WeChat Pay) are now universally excluded from basic mileage accrual across the board. Furthermore, significant shifts have occurred in the definition of "Dining"—specifically, food delivery applications (Keeta, Foodpanda, Deliveroo) are aggressively filtered out of dining multipliers by banks like HSBC. Additionally, we see a structural pivot in overseas spending rewards; for instance, the HSBC Travel Guru programme now exclusively targets *physical* overseas spending, entirely nullifying online foreign currency transactions from its highest bonus tiers. Consequently, your Python engine requires structural updates to differentiate between physical and online overseas spend, as well as the immediate correction of the Standard Chartered Cathay Mastercard's online spending rate, which has reverted to the base rate rather than the premium tier.

---

## 1. 🔄 RATE CHANGES (vs current engine)

The current state of your calculation engine contains several inaccuracies based on recent policy shifts and updated Terms & Conditions from the issuing banks. The following table highlights the exact Deltas that must be corrected.

| Card | Category | Old Rate (HK$/mi) | New Rate (HK$/mi) | Source |
|------|----------|-------------------|-------------------|--------|
| **SC Cathay Mastercard** | Online General | 4.0 | **6.0** | [cite: 1, 2] |
| **SC Cathay Mastercard** | Food Delivery | 4.0 | **6.0** | [cite: 1, 2] |
| **SC Cathay Mastercard** | Travel Booking (OTA) | 4.0 | **6.0** | [cite: 1, 2] |
| **SC Cathay Mastercard** | Ride-Hailing (Uber) | 4.0 | **6.0** | [cite: 1, 2] |
| **HSBC Red Mastercard** | Supermarkets | 25.0 | **25.0** (Confirmed) | [cite: 3, 4] |
| **HSBC VISA Signature** | Food Delivery | 2.78 (Dining) | **25.0** (Base) | [cite: 5] |

### Analytical Context for Rate Changes
**Standard Chartered Cathay Mastercard:** The previous assumption in the engine that "Online General" and its derivatives (Food Delivery, Ride-Hailing, OTAs) earn HK$4 = 1 mile is fundamentally incorrect for the current period. Official Standard Chartered documentation strictly limits the HK$4 = 1 mile accelerated rate to *Dining*, *Hotels*, and *Overseas* categories [cite: 1, 2]. All other eligible spending in Hong Kong dollars, including online retail, reverts to the base rate of HK$6 = 1 mile [cite: 1, 2]. 

**HSBC VISA Signature:** The engine previously grouped "Food Delivery" into general dining logic. Research clearly indicates that third-party delivery aggregators (Keeta, Foodpanda) are assigned distinct MCCs (often 5814 Fast Food or a distinct delivery code) that bypass the standard 5812 Dining MCC required to trigger HSBC's Red Hot Rewards "Dining" multiplier [cite: 5]. As such, these transactions fall to the base 0.4% RewardCash (RC) rate, equivalent to HK$25 = 1 mile [cite: 5].

---

## 2. ➕ MISSING CATEGORIES TO ADD

To accurately model the real-world spending habits of a Hong Kong consumer in 2026, the `CATEGORIES` array in your engine must be expanded. 

| Card | Category to Add | Rate (HKD/Mile) | Cap | Notes |
|------|-----------------|------------------|-----|-------|
| **SC Cathay** | Hotels (Direct Booking) | 4.0 | None | Explicitly added as an accelerated tier alongside Dining and Overseas [cite: 1, 2]. |
| **All HSBC Cards** | Overseas (Physical) | Varies | Varies | Must separate Physical vs Online to support Travel Guru rules [cite: 6, 7]. |
| **All HSBC Cards** | Overseas (Online) | Varies | Varies | Excluded from Travel Guru bonuses [cite: 6, 7]. |
| **All HSBC Cards** | Online Bill Payment (e-Banking) | 25.0 | None | Paying bills via HSBC e-banking yields 0.4% RC [cite: 8]. |

### Analytical Context for Missing Categories
**The Physical vs. Online Overseas Divergence:** A monumental shift occurred in the HSBC Travel Guru programme effective September 1, 2024, and continuing firmly through 2026. Foreign currency spending is now strictly limited to transactions made at *overseas physical stores* [cite: 6, 7]. Online foreign currency spending is explicitly excluded from the extra 3% to 6% RewardCash rebates. The engine must separate the `Overseas` category into `Overseas (Physical)` and `Overseas (Online)` to prevent aggressive over-calculation of miles.

**Hotel Bookings:** Standard Chartered Cathay explicitly lists "Hotels" as a designated HK$4=1 mile category [cite: 1, 2]. This applies to direct hotel bookings, differentiating it from OTA bookings which process as general online retail (HK$6=1 mile).

---

## 3. 🚫 EXCLUSIONS (Zero-earn categories)

The landscape of zero-earn categories has solidified. Banks are actively neutralizing loopholes that previously allowed users to generate miles without incurring merchant fees.

| Card | Excluded Transaction Type | Details |
|------|---------------------------|---------|
| **All Cards** | E-Wallets (PayMe / AlipayHK / WeChat Pay) | Absolutely no basic mileage or RewardCash accrual for top-ups or transfers across SC Cathay and all HSBC cards [cite: 2, 3, 9, 10]. |
| **All Cards** | Direct Tax & Insurance Payments | Paying IRD or Insurance directly via credit card portals earns zero. *Exception:* Using HSBC Online Banking bill pay yields 0.4% RC [cite: 8]. |
| **HSBC Red** | Supermarkets | Supermarkets are *not* zero-earn, but they are relegated to the abysmal 0.4% RC (HK$25=1mi) base rate [cite: 3]. |
| **HSBC EveryMile** | Supermarkets | Categorized under "other eligible transactions", earning a heavily penalized 0.4% RC (HK$12.5=1mi) instead of the 1% general rate [cite: 9]. |

---

## 4. 📊 SPENDING CAPS & THRESHOLDS (Verified)

To prevent the engine from outputting infinite linear miles, strict algorithmic caps must be enforced. The following thresholds are verified for 2026.

| Card | Cap/Threshold | Amount | Period | Status |
|------|---------------|--------|--------|--------|
| **HSBC Red** | 4% Online Shopping | **HK$10,000** | Monthly | Active. Excess earns 0.4% RC [cite: 3, 4]. |
| **HSBC Red** | 8% Designated Merchants | **HK$1,250** | Monthly | Active. Excess earns 0.4% RC [cite: 3, 11]. |
| **HSBC VISA Sig**| Red Hot Rewards (5X) | **HK$100,000** | Annual | Active. Excess earns 0.4% RC [cite: 12]. |
| **HSBC EveryMile**| Overseas Promo Threshold | **Min HK$12,000** | Per Phase | Active (Jan-Jun 2026). Must exceed 12k to trigger 1.5% RC bonus [cite: 13, 14, 15]. |
| **HSBC EveryMile**| Overseas Promo Cap | **Max HK$15,000** | Per Phase | Active. The bonus 1.5% RC is capped at $225 RC (which perfectly correlates to $15,000 of spend) [cite: 14, 15, 16]. |

---

## 5. 🎯 ACTIVE PROMOTIONS (Current Month - March 2026)

Your engine must account for the following time-sensitive active promotions.

| Card | Promo Name | Details | Validity |
|------|------------|---------|----------|
| **HSBC EveryMile** | Overseas Spending Offer (Phase 1) | Spend > HK$12,000 to earn extra 1.5% RC (Total 2.5% RC = HK$2/mi). Capped at $225 RC per phase. | Jan 1, 2026 - Mar 31, 2026 [cite: 13, 14, 15] |
| **HSBC EveryMile** | Agoda Hotel Promo | 15% off year-round plus 30% monthly flash deals on designated hotel bookings. | Year-round 2026 [cite: 13, 17] |
| **HSBC All Cards** | Travel Guru (Phase 3) | Extra 3% (GO), 4% (GING), or 6% (GURU) on physical overseas spend. Requires registration. | Valid through Dec 31, 2026 [cite: 6, 7, 18] |
| **SC Cathay** | RentSmart Promo | Settle rental deposits/payments via RentSmart to earn HK$6=1 mile plus up to 1.5% fee waiver. | Until Apr 30, 2026 [cite: 1] |

---

## 6. 🏷️ MCC INTELLIGENCE

A robust calculation engine requires granular Merchant Category Code (MCC) intelligence to avoid misclassifying everyday edge-case transactions.

| Merchant/Type | MCC Code | Classification | Which Card Benefits |
|---------------|----------|----------------|---------------------|
| **Uber / Uber Eats** | 4111 / 4121 | Commuter/Taxi or Online | **HSBC Red** treats this as Online Retail (4% RC / HK$2.5=1mi) [cite: 3, 19]. SC Cathay treats it as local base (HK$6=1mi) [cite: 2]. |
| **Foodpanda / Keeta** | 5814 (Fast Food / Delivery) | Online Retail / Dining Exclusion | Excluded from HSBC Red Hot Dining. Benefits **HSBC Red** (Online 4% RC) [cite: 5, 20]. |
| **Online Bill Pay** | Various | Bill Payment via e-banking | **HSBC Cards** earn a flat 0.4% RC (1 RC/$250) when paid through the HSBC Online Banking portal [cite: 8]. |
| **Hotels (Direct)** | 3500-3999 | Lodging / Hotels | **SC Cathay** explicitly grants HK$4=1mi for direct hotel bookings [cite: 1, 2]. |

---

## 7. 📝 RULES FOR CALCULATION ENGINE

Below is the definitive, Python-parseable logic required to update the `calculate_miles()` function. It synthesizes the exact mathematical rules dictated by the 2026 terms and conditions.

### Engine Architecture Updates:
1. **Update `CATEGORIES` array**:
   - Split `Overseas` into `Overseas (Physical)` and `Overseas (Online)`.
   - Add `Hotels (Direct Booking)`.
   - Add `Online Bill Payment (e-Banking)`.

2. **Update SC Cathay Mastercard Logic**:
   ```python
   # Standard Chartered Cathay Mastercard Updates
   if card == "Standard Chartered Cathay Mastercard":
       if category in ["E-Wallets (PayMe/Alipay/WeChat)", "Insurance / Utilities / Tax"]:
           rate = 0.0
       elif category in ["Cathay Pacific Flights", "HK Express Flights", "Cathay Partner Dining"]:
           rate = 2.0
       elif category in ["Dining (Premium)", "Dining (Casual)", "Hotels (Direct Booking)", "Overseas (Physical)", "Overseas (Online)"]:
           rate = 4.0
       else:
           # Online General, Food Delivery, OTA, Ride-Hailing, Supermarkets, In-Store, Octopus AAVS
           rate = 6.0
   ```

3. **Update HSBC EveryMile VISA Logic**:
   ```python
   # HSBC EveryMile VISA Updates
   elif card == "HSBC EveryMile VISA":
       if category == "E-Wallets (PayMe/Alipay/WeChat)":
           rate = 0.0
       elif category in ["Supermarkets", "Insurance / Utilities / Tax", "Online Bill Payment (e-Banking)", "Octopus AAVS"]:
           rate = 12.5 # 0.4% RC -> 1 RC per 250 -> 20 miles per 250 -> 12.5 HKD/mi
       elif category in ["Travel Booking (Designated OTA)", "EveryMile Designated Everyday"]:
           rate = 2.0
       elif category == "Overseas (Physical)":
           # Evaluate Promo Threshold (Jan-Jun 2026 Phase)
           if amount >= 12000:
               # Max spend for the extra 1.5% RC is 15000 (cap $225 RC)
               bonus_eligible_amount = min(amount, 15000)
               base_miles = amount / 5.0 # Base 1% RC -> HK$5=1mi
               bonus_miles = bonus_eligible_amount / 3.333 # Extra 1.5% RC -> HK$3.33=1mi
               miles = base_miles + bonus_miles
               rate = amount / miles if miles > 0 else 0
               notes = "Overseas Promo Triggered: HK$2/mi effective on first 15k, HK$5/mi thereafter."
           else:
               rate = 5.0
               notes = "Did not meet HK$12k overseas threshold. Base HK$5=1mi applied."
       elif category == "Overseas (Online)":
           rate = 5.0 # Excluded from Travel Guru and Physical promos
       else:
           rate = 5.0 # Base local rate
   ```

4. **Update HSBC Red Mastercard Logic**:
   ```python
   # HSBC Red Mastercard Updates
   elif card == "HSBC Red Mastercard":
       if category == "E-Wallets (PayMe/Alipay/WeChat)":
           rate = 0.0
       elif category in ["Supermarkets", "Insurance / Utilities / Tax", "Online Bill Payment (e-Banking)", "Octopus AAVS"]:
           rate = 25.0
       elif category == "Shopping (Designated 8%)":
           if amount <= 1250:
               rate = 1.25 # 8% RC
           else:
               miles = (1250 / 1.25) + ((amount - 1250) / 25.0)
               rate = amount / miles
       elif category in ["Online General", "Food Delivery", "Travel Booking (Non-Designated OTA)", "Travel Booking (Designated OTA)", "Ride-Hailing (Uber/Taxi Apps)", "Overseas (Online)"]:
           if amount <= 10000:
               rate = 2.5 # 4% RC
           else:
               miles = (10000 / 2.5) + ((amount - 10000) / 25.0)
               rate = amount / miles
       else:
           rate = 25.0 # Dining, In-Store General, Overseas (Physical)
   ```

5. **Update HSBC VISA Signature Logic**:
   ```python
   # HSBC VISA Signature Updates
   elif card == "HSBC VISA Signature":
       if category == "E-Wallets (PayMe/Alipay/WeChat)":
           rate = 0.0
       elif category in ["Food Delivery", "Supermarkets", "Insurance / Utilities / Tax", "Online Bill Payment (e-Banking)", "Octopus AAVS"]:
           rate = 25.0 # Explicitly bypasses Red Hot Dining
       elif category in ["Dining (Premium)", "Dining (Casual)", "Cathay Partner Dining"]:
           if amount <= 100000: # Assuming annual cap limit context
               rate = 2.78 # 3.6% RC (9X)
           else:
               rate = 25.0 # Drops to base 0.4% if annual cap exceeded
       elif category in ["Overseas (Physical)"]:
           rate = 6.25 # 1.6% RC Base (assuming non-Red Hot allocation, or mention Travel Guru stacking potential)
       else:
           rate = 6.25 # 1.6% Base
   ```

### Analyst Commentary on Mathematical Integrity
When executing `math.floor(miles)` in the main return statement, it is imperative to note that the backend systems of these institutions calculate points/RewardCash based on individual transaction integers, not aggregated monthly floats. For instance, HSBC calculates $1 RC for every HK$250 spent. If a transaction is HK$249, it yields 0 RC. To make the engine perfectly accurate in a real-world deployed app, future iterations should accept an *array of individual transaction amounts* rather than a bulk monthly sum, flooring each individual transaction against the $250 modulo logic before applying the multiplier conversions.

**Sources:**
1. [sc.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFB97JVC4FsEqPGeBpk2jKEt0P08SQMqNqZBKOWHMPe7F_otskLwOlAtY3JYQDv3GLo7_xBCWOoW0aLrV72l5IYz0pnRuUvPsGAbzE77XThY_vuraSQEXSS8ZI-9k094w==)
2. [sc.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzq2BR1WAMi6nJe41yh4yTlXZPCLZXKUmgYiB9dVJGu99COCWX9rU8Ea3jmWSPowV4NRGET6Tks0R593PAEOUFnSRjig9RhTL_ZoDgibX6JRGo8Qadf6IHcG2JuJD7pKMiGldwocRkLJxP2ksz3N663vQp1JPebqn7WZEG8jW0S5li23X8cA==)
3. [hkcashrebate.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-L6HWzMbmxUggjl93sxeT_wJONdwcfK7FrwxDKsVm7MrglhEmRGcWyogUMqgnYW10NhqXZwJElLak_JuLvjeEm7BMBPKKLsN5_0hdHxiF30Fcf8sl4A==)
4. [moneyhero.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVloBZIku7g9IJqclD9eNrvSyzCD1G60-6E3rs5y3mgaJJdP52WrVyDpAUK-Ml_TFSnBy6o-pJDmmi__n5L6VxmIzxGYTkt4xx3sPE-cXNsozbqvfVb-cBaDjtrOTTLgEYlSl-hsWQr_GBs7actaCKRpc1e4ZMUqjGk_ZNmYQ=)
5. [jetsofind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEm1xtAAMyiStT_FvilPtlILodRPJMVZoKNURP94jN7JeZRQ5aIs2y7jLTEcWzMP1ZglOscpOw90IGXmj2kL2r5PCJEJmy4QmquTQq_eGo66S_5q7uKrLXEHKYDNugQqHzPEyMANb0OpPrEarIeGc3qwTYG)
6. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQED4vDfl6f0yGRrxT-CTxFjjWoq1bW9OfmpErrEYrv5Wy4IXLWMwku-Oe_CVqMAUudroO61rZebMdSdCBsFUQ2xzx1VgLAZ03163f07wM_V0XMd0bIoU1ipfNEHm1pO7-7O6tZuElAtlJ0m_z6EsK81e3iLJc6VZg==)
7. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOe2YHybKni5AoCl193fHEgkTy58EO0OQQnaAtSfIaWyUHQ7vwDM-pu_IUqzcnUN1EuW-vFAYvrYk11oITrv1IWJsMstx2HZG6m2wjNZ3S9i1lgAKQVgR9otRKMR5-3ikec1N76yuT5wMhRPzceMeSMxBgfmppj3bPN9YuTQyBkid1SNbM4TbyFZ7FaUCjPRGI2pOnog==)
8. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGlLS4gcuUrBy8UCEJXmF2iTsRBJ3-iB5yx0wqbnna9SAjmFUWuM_JtfiJCk0aUb-p2RnBKir2l0MmBX63sEAUFv3P5Z3gfT9Oi8_4ZRXAd4laD_g2aWsCMcELkWqEHQxQLL5Rs9lNB0ex1TN84)
9. [jetsofind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdybap-06JaMh1-oVTmGSSAbMbyO2_EYjGJa96doorICIUpmvuR3MBHdvIljypmpr4LVfrMpIhujh_Etgsb0i_nSUe9hK-dAZhAnJIUg6xOQXPZYH5_j437LOv_KcMd5M=)
10. [sc.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyA1GEbWyQo3JZhCSQYseTMmmKbkp96i18GriUAxwzUSmGYrVu5jj7XrR1kzxg0xEVRG1Zucd2EK96Qlvd_woYgUZ5s4xPRNXQ8UvnpxWHuwSAWLbGbEAS6LDBy1X6mWjswuK0)
11. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzuRkYJtMKKpWeMabmSui8Glk6mLZ0eW8-a4a9N_2nCovGNf7QQeyGoyX3hFZc8K5LCPth9QDIS68ntu7kS54ztrc886H9StwTuFXf94VsH30qaKic9MNL5Vdf0e_psxxkZeaU_k2-)
12. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIdkbQdS8VU-q4qUqu5DOoNd7Al0UN9T1-CG2vD3vfM_Ex0J4VY7qBudkzDIePhDxHXSlO5yFhGGWXUmmZJZ0hLsLWqY93aYy12SyyxX1lHtGG9gfe0jsk3nj5sl0YBE3RJP452tdFEmPnthS3qSOMpTeoUhE77JHnstFxm7VvdYA8EP4=)
13. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwzHfz5i_ze1Gddvj44-uottGfOWaSJBLsp05NbxIazVAYp8yiy9mlUFi3j_wwMoVR4Lt1vdxLugpnjdaxhyWc1vNhS3LenI_H3-ZHEI-1k-FfnOz7CHIOk5DA9h_0O1i1LQSKM3txgl4SRDQFlp8eHPfQRbAkrIXT5KVH2BIUOFTB0wA=)
14. [mrmiles.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGctIbA7F3OF1V0tIGr7RIvLbORbIsJ65ymP5Yn8rMNvy-YHSIbtpMLQYJEtRKBDBBilpNTAKsXmUdfMqb5ISXL2hWDt6oku1XqfIe6nhRf4xT-w90Oi_DtoCMAj-t08BBh)
15. [flyformiles.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbGWJCNWc7nj_KrNCImSQNkU_2JJKoxra_L49x-qwzpyjgqNpIoNbKa4QD_QZyoSyYbcWdGdwuz_4lM2FFR9La1bdDfPBNf3FLASh8gLEAT3-1NkMbOhJyxsI8O-fmJpeK2JkDmOEfqF-EU_vcpSj0rOVI_ySE)
16. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4WncY_Ck4MSkmfomLvX8UX_FOSueuttyzs0ZuJY9pSdHi0sH_kf5XTxjjTcpvXK1d5ML9vzT4CfXTTzZe5lw375Y7I3bclYzrZH89I7s9COWb5pGpoByv-dFCyw3EBKhgw8LNyMul_G5yTbJ1SVKeL6zxpOPgAx6nPAXzgxLuGnhdOEnitRJQVWnRM1sDEE4b_xUoWo5OCA==)
17. [agoda.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGN6onGfw3IjVKthdJ9-TEAnvMuLRbYg01UErkJncNw_0Oh0pc6VjCbHHvXv-V4Zv0AQlmXsXNILhOHxfsVW_LbQmZo8ZtQ5LRy14G9XfkVd7aY0iIxK9UW)
18. [moneyhero.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiPm2xmsF3DEDyBXupw2UowBMYl1dm76DOm9ioBC7aCF3Zz24xqmfVWXWSPEjM4-UjBupOcL4UEhWqeq8aKqW2VIJOXGaeOGaTqINt392MmwFZsc0BGZf9AxG_DfyzTgejkFUcTSyUC9sv7TIB4h0qjFEZyI3k0tm_qElSCffyGqKkEwPcHY6-en33j6w52jrxfAeaL7ojk3O6dQ77)
19. [flyertalk.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtpbCTtNT6BxQtqWUw9mqIqYZJPRlyXUSOOXhBDd59cIgfQovIZ107GmZIW6EwWVwYnTrkB1juEWkbYdDPdHpbRj9HtI_KH90PRn7uy9xiUs1YSwVaNlH5FfA6a2siDBgUavfsa2lAvxDMjbaOYtXloBThOjLn3nGAuBCf-e85mo21OA46FloRUMx9C6xSi6ahA3s5wYd-FN7GgRR4L8zdBJM0VYjdvGT1h07YTFKIDmipFh72dLux)
20. [mrmiles.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4Xj4ErDewfLKiwIjHrNTWDEy4PftSmWqeWswBVQX2ulSV1b8JEbrKWfO8MWnB3DmhuJacLf0NHx871-BbbhT6PMBQuSZezGQC6vysTH6dFoqmhbvjiag2A_Y=)
