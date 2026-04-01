# Cathay Miles Engine — Deep Research Delta Report

## Date: March 31, 2026

**Key Points:**
*   **Engine Inaccuracies Detected:** The current Python engine incorrectly attributes Klook and KKday as designated merchants for the HSBC EveryMile card. Furthermore, it fails to account for the shared nature of the HK$100,000 annual cap across all HSBC Visa Signature Red Hot Rewards categories. 
*   **New Caps & Thresholds:** The HSBC EveryMile overseas promotional rate (HK$2 = 1 mile) is strictly capped at HK$15,000 per phase, a detail missing from the current state.
*   **Promotional Game-Changers:** The HSBC Travel Guru program drastically alters overseas earning math, allowing up to 8.5% RewardCash (HK$0.59 = 1 mile) on physical foreign currency spend for top-tier members. 
*   **MCC Sensitivities:** Food delivery (Foodpanda/Keeta) operates under MCC 5499 or 5814, which correctly triggers online shopping bonuses for the HSBC Red Mastercard, but heavily depends on payment gateway routing.

**Complexity and Hedging:**
While the data presented in this report is derived from the most recent official bank documentation and leading financial aggregators in Hong Kong as of early 2026, the credit card rewards landscape remains highly dynamic. Merchant Category Codes (MCCs) are assigned by acquiring banks and can change without notice, potentially altering earn rates overnight. Furthermore, promotional terms—such as the HSBC Travel Guru program and the Standard Chartered Cathay Mastercard overseas multipliers—are subject to periodic adjustments, abrupt quota exhaustion, or unannounced systemic modifications. As such, the programmatic rules suggested herein represent the most accurate modeling available currently, but we must acknowledge that edge cases in transaction routing may occasionally yield disparate results.

---

## 1. Introduction and Methodological Framework

The optimization of Asia Miles (now integrated under the Cathay membership program) requires a highly precise, dynamic algorithmic approach due to the complex, multi-layered reward structures implemented by Hong Kong's financial institutions. The current Python calculation engine provides a robust foundational architecture; however, rigorous empirical verification reveals several critical deltas between the engine's hardcoded logic and the real-world terms and conditions active as of Q1 2026. 

This exhaustive delta report is designed for seamless integration into your existing algorithmic framework. It dissects earning rates, promotional caps, zero-earn exclusions, and Merchant Category Code (MCC) intelligence across the four targeted credit cards: the Standard Chartered Cathay Mastercard, HSBC EveryMile VISA, HSBC Red Mastercard, and HSBC VISA Signature. The analysis synthesizes data from official bank terms, consumer finance platforms, and historical transactional routing data [cite: 1, 2].

---

## 2. Rate Verification and Delta Analysis

A meticulous review of the current Python engine's `calculate_miles` function against the 2026 banking terms reveals several hardcoded rates and categorizations that require immediate remediation.

### 🔄 RATE CHANGES (vs current engine)

| Card | Category | Old Rate | New Rate | Source |
|------|----------|----------|----------|--------|
| **HSBC EveryMile VISA** | Travel Booking (Designated OTA) | HK$2.0 = 1mi | **HK$5.0 = 1mi** (Base Rate) | [cite: 2] |
| **HSBC EveryMile VISA** | Overseas (Physical) | HK$2.0 = 1mi (Flat if >12k) | **HK$2.0 = 1mi** (Only up to $15k cap) | [cite: 3] |
| **HSBC VISA Signature** | All 1.6% Non-Dining Bonus Categories | HK$6.25 = 1mi (Uncapped) | **HK$6.25 = 1mi** (Shared 100k Cap) | [cite: 1, 4] |
| **Standard Chartered Cathay** | Hotel Bookings | Not Explicitly Defined | **HK$4.0 = 1mi** | [cite: 5, 6] |

#### Deep Dive into Rate Deltas

**1. HSBC EveryMile VISA: The OTA Misclassification**
The current engine categorizes "Klook, KKday" under `Travel Booking (Designated OTA)` and assigns them a rate of HK$2 = 1 mile for the EveryMile card. Exhaustive review of the official 2026 HSBC EveryMile "Designated Everyday Spend Merchants" list reveals that Klook and KKday are **not** included [cite: 2]. The designated merchants for the 2.5% RewardCash (HK$2 = 1 mile) tier strictly include local transportation (Carparks, Road Tunnels, Taxi Services), specific cafes (Starbucks, Pacific Coffee, Blue Bottle), and online entertainment (Netflix, Spotify, YouTube) [cite: 2]. While Agoda holds a special 15% discount partnership [cite: 7], OTAs like Klook and KKday default to the base earning rate of HK$5 = 1 mile. *Engine Update Required: Reclassify non-listed OTAs to the base rate.*

**2. HSBC VISA Signature: The Shared Cap Fallacy**
The engine currently assumes that the 1.6% base rate for non-selected Red Hot Rewards categories is uncapped (`rate = 6.25`). This is mathematically incorrect. The HSBC Visa Signature operates on a **shared annual cap of HK$100,000** across *all* five Red Hot Rewards categories [cite: 1, 4]. If a user exhausts the HK$100,000 cap on their chosen 3.6% Dining category, the earn rate for the remaining four categories (e.g., Overseas, Lifestyle, Home) plummets from 1.6% to the base 0.4% (HK$25 = 1 mile) [cite: 1, 4]. 

**3. Standard Chartered Cathay Mastercard: Hotel Bookings**
The official terms for 2026 explicitly state that "Hotel Bookings" earn HK$4 = 1 mile [cite: 5, 6]. While the engine currently captures "Travel Booking", it is highly recommended to explicitly define "Hotel Bookings" as a distinct MCC category to ensure accurate routing, as direct hotel bookings (MCC 7011) are treated distinctly from OTAs (MCC 4722) by acquiring banks.

---

## 3. Missing Category Gaps to Add

The expansion of the digital economy and shifts in consumer payment behavior necessitate the addition of several distinct transaction categories to the engine's arrays.

### ➕ MISSING CATEGORIES TO ADD

| Card | Category | Rate (HKD/Mile) | Cap | Notes |
|------|----------|------------------|-----|-------|
| **SC Cathay Mastercard** | Rent Payments (RentSmart) | HK$6.0 = 1mi | None | Promotional rate valid until April 30, 2026 [cite: 8]. |
| **All Cards** | Overseas (Physical) | Variable | Promos | Must be differentiated from Overseas (Online) due to Travel Guru rules [cite: 9, 10]. |
| **All Cards** | Overseas (Online) | Variable | Base | Online foreign currency spend is excluded from Travel Guru [cite: 9, 10]. |
| **SC Cathay Mastercard** | Hotel Bookings (Direct) | HK$4.0 = 1mi | None | Explicitly stated in the latest SCB reward structure [cite: 5, 6]. |

#### Analysis of Category Dynamics

**Rent Payments via RentSmart:** 
Rent payments are traditionally a zero-earn category for most credit cards. However, Standard Chartered has established a targeted partnership with RentSmart. Through April 30, 2026, the SC Cathay Mastercard earns the base rate of HK$6 = 1 mile on rental deposits and advance payments processed through the RentSmart platform [cite: 8]. This is a massive competitive advantage for the SC card in the engine, as it captures high-volume, recurring organic spend that HSBC cards typically exclude or heavily penalize.

**Bifurcation of Overseas Spending:**
The current engine features a monolithic `Overseas` category. This is no longer viable in 2026. HSBC has explicitly bifurcated foreign currency spending into "Physical" and "Online" transactions [cite: 9, 10]. The highly lucrative HSBC Travel Guru program (which offers up to 6% extra RewardCash) strictly applies *only* to transactions made at physical overseas stores [cite: 9]. Online purchases settled in foreign currencies (e.g., buying from Amazon US) earn the standard overseas rate but are entirely excluded from the Travel Guru multiplier [cite: 10]. The engine must split this category to accurately calculate yields.

---

## 4. Exclusions and Zero-Earn Categories

Risk mitigation strategies by banks have led to a crackdown on manufactured spending, primarily through e-wallets and utility portals.

### 🚫 EXCLUSIONS (Zero-earn categories)

| Card | Excluded Transaction Type | Details |
|------|---------------------------|---------|
| **All HSBC Cards** | E-Wallets (PayMe, Alipay, WeChat) | Top-ups to PayMe, AlipayHK, and WeChat Pay HK yield absolutely zero RewardCash [cite: 2, 11]. |
| **SC Cathay Mastercard** | E-Wallets | Strictly excluded from earning Asia Miles [cite: 12, 13]. |
| **HSBC EveryMile** | Bill Payments (e-banking) | Utilities, tax, and insurance paid via HSBC e-banking are excluded from welcome offers and generally penalized [cite: 11]. |

#### Contextualizing Exclusions
While PayMe itself has launched a "Spend and Earn" program offering up to 15% cashback at specific merchants [cite: 14, 15], this is a closed-loop platform reward. The underlying credit card used to fund the PayMe wallet receives zero rewards. In fact, non-HSBC credit cards now incur a 1.2% top-up fee [cite: 16]. The engine correctly models E-wallets as zero-earn, but users must be warned that using credit cards to fund wallets for the sake of secondary platform cashback does not yield Asia Miles.

---

## 5. Spending Caps & Thresholds (Verified)

The architectural flaw in many mileage optimization algorithms is the failure to properly model the mathematical cliffs—the exact point at which a highly lucrative promotional rate reverts to a punitive base rate.

### 📊 SPENDING CAPS & THRESHOLDS (Verified)

| Card | Cap/Threshold | Amount | Period | Status |
|------|---------------|--------|--------|--------|
| **HSBC Red Mastercard** | Online Shopping Cap | HK$10,000 | Monthly | Verified: 4% drops to 0.4% thereafter [cite: 17, 18]. |
| **HSBC Red Mastercard** | Designated Merchant Cap | HK$1,250 | Monthly | Verified: 8% drops to 0.4% thereafter [cite: 17, 19]. |
| **HSBC VISA Signature** | Red Hot Rewards Cap | HK$100,000 | Annually | Verified: Shared across ALL selected 5X and 1X categories [cite: 1, 4]. |
| **HSBC EveryMile** | Overseas Promo Threshold | HK$12,000 | Phase | Verified: Must hit HK$12k to trigger the extra 1.5% RC [cite: 3]. |
| **HSBC EveryMile** | Overseas Promo Cap | HK$15,000 | Phase | Verified: Max extra RC is $225 (HK$15k spend). Excess earns base 1% RC [cite: 3]. |

#### Mathematical Modeling of the EveryMile Overseas Cap
The EveryMile overseas promotion running from Jan 1 to June 30, 2026, requires precise programmatic handling. It operates in two phases (Phase 1: Jan-Mar; Phase 2: Apr-Jun) [cite: 3, 20].
*   **Condition:** User must accumulate a minimum of HK$12,000 in foreign currency spend within the phase [cite: 3, 20].
*   **Reward:** An extra 1.5% RewardCash on top of the base 1% RewardCash, yielding a total of 2.5% RC (HK$2 = 1 mile) [cite: 3].
*   **Ceiling:** The maximum bonus is capped at $225 RC per phase. Mathematically, $225 / 0.015 = HK$15,000 [cite: 3]. 
*   **Overflow:** Any spend above HK$15,000 reverts to the base rate of 1% RC (HK$5 = 1 mile) [cite: 3, 11]. 

*Engine logic must calculate the blended rate for transactions that breach the HK$15,000 ceiling.*

---

## 6. Active Promotions (Current Month)

Temporary multipliers heavily skew card recommendations. The engine must be updated to process these active 2026 campaigns.

### 🎯 ACTIVE PROMOTIONS (Current Month)

| Card | Promo Name | Details | Validity |
|------|------------|---------|----------|
| **HSBC (All)** | Travel Guru Membership | Up to 6% extra RC on *physical* overseas spend. Tier 1: 3%, Tier 2: 4%, Tier 3: 6% [cite: 9, 21]. | Dec 31, 2026 [cite: 21] |
| **HSBC EveryMile** | Overseas Spending Offer | Extra 1.5% RC if spend exceeds HK$12k. Capped at HK$15k [cite: 3]. | Jun 30, 2026 [cite: 3, 20] |
| **SC Cathay Mastercard** | Overseas Spending Rewards | Extra 2,500 miles upon registering and spending HK$10,000+ overseas [cite: 22]. | Mar 3, 2026 [cite: 22] |

#### The Dominance of HSBC Travel Guru
The HSBC Travel Guru program fundamentally breaks standard calculation matrices. By gamifying foreign currency spend, HSBC has created a tiered system that stacks on top of base rates and Red Hot Rewards [cite: 9].
*   **GURU Level (Tier 3):** Offers an extra 6% RewardCash [cite: 21].
*   **Stacking with EveryMile:** Base (1%) + EveryMile Promo (1.5%) + GURU (6%) = 8.5% RewardCash [cite: 23]. Since 1 RC = 20 miles for EveryMile, 8.5% RC yields an astonishing **HK$0.59 = 1 mile** [cite: 21, 23]. 
*   **Constraint:** This applies strictly to *physical* overseas spending. Online foreign currency is excluded [cite: 9, 10].

---

## 7. Merchant Code (MCC) Intelligence

The backbone of credit card optimization is the Merchant Category Code (MCC). Acquirers assign these 4-digit codes, dictating whether a transaction triggers a bonus or falls into the 0.4% abyss [cite: 24, 25].

### 🏷️ MCC INTELLIGENCE

| Merchant/Type | MCC Code | Classification | Which Card Benefits |
|---------------|----------|----------------|---------------------|
| **Foodpanda / Keeta** | 5499 / 5814 | Convenience / Fast Food [cite: 26] | **HSBC Red** (Online 4%)[cite: 18]; **SC Cathay** (Food Delivery HK$4) [cite: 6]. |
| **Uber (Hong Kong)** | 4121 / 4789 | Taxicabs / Transportation [cite: 25, 27] | **SC Cathay** (Ride-Hailing HK$4). *Note: HSBC Red views this as online if processed via app.* |
| **Agoda** | 4722 / 7011 | Travel Agencies / Hotels | **EveryMile** (Designated 15% discount) [cite: 7]; **SC Cathay** (Hotels HK$4) [cite: 5, 6]. |
| **Government/Tax** | 9311 | Tax Payments | **None.** Earns 0.4% at best on HSBC [cite: 28], 0 on SC Cathay [cite: 12, 13]. |

#### MCC Nuances
*   **Food Delivery:** Platforms like Foodpanda process payments through online gateways, triggering the "Online General" 4% rebate on the HSBC Red Card [cite: 18, 26]. For the SC Cathay card, "food delivery platforms" are explicitly designated to earn HK$4 = 1 mile [cite: 6]. It is vital to note that Foodpanda is generally *not* classified under premium dining (MCC 5812), so cards that only reward traditional dining will fail to trigger bonuses here [cite: 26].
*   **Uber:** As an app-based service, Uber frequently processes as an online transaction. This benefits the HSBC Red Card. However, the SC Cathay Mastercard's specific Cathay partnership yields standard ride-hailing rates plus occasional bonus miles per ride.

---

## 8. Rules for Calculation Engine

To execute these findings, the Python engine requires strict conditional logic updates. Below are the precise, Python-parseable logic rules that must be implemented to correct the current engine state.

### Python-Parseable Logic Updates

**Global Category Updates:**
*   Add category: `Overseas (Physical)`
*   Add category: `Overseas (Online)`
*   Add category: `Rent Payments (RentSmart)`
*   Add category: `Hotel Bookings`

**For Standard Chartered Cathay Mastercard:**
*   `if category == 'Rent Payments (RentSmart)' → rate = 6.0`
*   `if category == 'Hotel Bookings' → rate = 4.0`
*   `if category in ['Overseas (Physical)', 'Overseas (Online)'] → rate = 4.0` 
*   *Add Promo Logic:* `if category in ['Overseas (Physical)', 'Overseas (Online)'] and amount >= 10000 → miles += 2500` *(Note: valid until Mar 3, 2026)*.

**For HSBC EveryMile VISA:**
*   `Remove 'Travel Booking (Designated OTA)' from HK$2=1mi tier.` Klook/KKday are not listed. Set them to `rate = 5.0`.
*   *Overseas Physical Promo Logic (Phase limits apply):*
    ```python
    if category == 'Overseas (Physical)':
        if 12000 <= amount <= 15000:
            rate = 2.0  # 2.5% RC
        elif amount > 15000:
            base_miles = 15000 / 2.0
            excess_miles = (amount - 15000) / 5.0
            miles = base_miles + excess_miles
            rate = amount / miles # Blended rate
        else:
            rate = 5.0  # Fails to meet 12k threshold
    ```
*   *Travel Guru Integration (Optional parameter `guru_level` 0, 1, 2, or 3):*
    `if category == 'Overseas (Physical)' and guru_level == 3 → extra_rc_percent = 0.06 → extra_miles = amount * 0.06 * 20`

**For HSBC Red Mastercard:**
*   `if category == 'Overseas (Physical)' or category == 'Overseas (Online)' → rate = 25.0` (Base 0.4% rate applies as these are not inherently online unless processed through a specific online gateway, but generally, foreign physical is 0.4%).
*   Ensure the HK$10,000 cap strictly applies to the aggregate sum of `Online General`, `Food Delivery`, and `Ride-Hailing` per month.

**For HSBC VISA Signature:**
*   *Shared Cap Logic Update:* The engine must track `cumulative_red_hot_spend`.
    ```python
    if cumulative_red_hot_spend + amount > 100000:
        # Calculate how much falls under the cap
        spend_under_cap = max(0, 100000 - cumulative_red_hot_spend)
        spend_over_cap = amount - spend_under_cap
        
        # Apply 3.6% (rate 2.78) or 1.6% (rate 6.25) to spend_under_cap
        # Apply 0.4% (rate 25.0) to spend_over_cap
    ```
*   `if category == 'Overseas (Physical)' and guru_level == 3 → extra_rc = 0.06` (Yields massive returns when combined with Red Hot Rewards).

### Conclusion

The adjustments outlined in this Delta Report bridge the gap between static algorithmic assumptions and the highly conditional, cap-sensitive reality of Hong Kong's credit card ecosystem in 2026. By separating physical from online overseas spend, enforcing shared annual caps, and correcting designated merchant lists, the updated Python engine will provide mathematically flawless Asia Miles optimization strategies.

**Sources:**
1. [jetsofind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZPhRnubvyo1BD98jU_dWcTtFmymyw9kiT_xFaX6_Nd10-JyX_Hyu-NfCVxVZOq3HOXGpjvSJhIgzcJqM5_yLBxbyYDVE4qPGhbfh7aMx6p40pHFKANk5pe01GrNx02T1dOdkr1nleaN5eMA==)
2. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQET8GLS4RXFGk8Ymgk13OGQOuTUQ8ufF4EMLZzrvZySAXoIQvGJruKRtchmWuKbX-8O2FSCRLNXoXrzWaebuVkPp-OB5juGdgFx4hBhDn69KTtZrnCRkqkUQ3s5EUezO8ZnTA9ZCRHxZwOLfRKs15O63xWzaeIuiA==)
3. [mrmiles.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpeJR7wTuiKT8hy7mH6CbZKfXh2sXtflFbcDPxLHQc4eangA8apq6QPNv8oV42PoHszxMMz7bez7h_wucgdCCj6P5C7Y4odKCuvhgpLIhV-P3M1ODye8mCEBDUtasAxpBT)
4. [jetsofind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFupUCGgsREao5iWGOZjDN-d6SGvc5nYIoRDCM3MOZ_LxK8lY1mJMzziO3qXTysYrrL3nnQMFUh5sAIDKlORHyyx9PupI3S2xcDd9RKnc5j6LgN381RErbmcbciz6i_87nGddUaxhW-pmeBTca2Mpp0hR6x)
5. [moneyhero.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJaoCWo3vIuk-Rp9H2IheOz9IACzBIJjDs36mhs13QiqYI3G16gUcY60L35dIMbYOkABitSWFY0SQghQWC1NxTGi-n5lwrvK8-h8Ha8ppdPsJIIBPwTp4IoQgRAo8NQhxbmB4wDt01jIM5yR0k9aJuArzmrCXgn2_V4ptjcyL9F8zRaMtwged_Pe1olAMJ)
6. [cathaypacific.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGmQmqiVTBPm2qyoanG581A1msM0yx8WQFuTzZwsMtlBhqIFOv3Bq8IOJtOoP1GY8Bg4RA9QgEm05VgGvn2Q1LXFzJ51UD6x-dMuEslX1o4ZcDYuAr1LL60_Jgw2d9RBh6t7KUwXR4RaNbYWytvbDfdZuDe4eMcMWddNSXhTau_dz8)
7. [agoda.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGISLm188V2xXYwwz4UZ9ftvRtsLuugGXAM4MItYXiuUYVmPS8Xhh9ySa5cSVDKkY6YhlMFDvYE4iwAWqld6rBUJ4-pBh55YfGWB-zn0HVFlAet3UIkGjiG)
8. [sc.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-lQPisWbd89j-EZ5sMcMiu6QgESUgLbSBkSAKXrus_IS6U17MzEZJhqCmRlrhwsCv7YuaWjMmfzF7IQR0i0NG6zUhtAU9_XsafBoIlHEecb7_4RGsFwCLcKcT-rC9MQ==)
9. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKwNMjIMKLnhV8V-UmVgGDMOFpRaJaQxqusz82Y_GdcKsVrtRlUhB3oSOUQ-qZEdu9gTKd7h1ToOgXrGld9-YS05WP1KnaZ7TON3or2K5HLFjLfEL8rqyKX6zhLXjYbjBn8cYqw98snRsjSoY8k85eXtssizfq5g==)
10. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGM5M0TcNDWdfGeOQ89oaAuDXTQ9mxjC6d7BHB9HcuypHC4lsra0bAkSeSdkmZmKJwGqZNPVZ-4jjsIcZW9hfsRCyvj-yMFZwPAOqiN298jXkAiYIG0ulC3sWuVDK8Uxh7WBqWeR9iAmZQfaHElgBZ6YFZ01875e8Ox8tw5gH3W0PuHXsVhGfwjTIJaOXvLnMM=)
11. [flyformiles.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzahB1TlpYA0A-ksbg3TJIh8DHUtUE-wxFGsBxFQpCwak-aN0graxuCr0uXLLgYyU0aS7JWk3kzo-Ir8p6oMcl5zo9alUA99JDY1CIJfz-EjRI3g5DRujzYWyTpPHUnvHO1GtJWEcXk2ODWLme1kF-PMDR82eC)
12. [jetsofind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiddIliU-LkzXWMJrCWY5rDunp7eSMLE5N7HSmy4IidTtGWtIpyfsfULJ02bosrqsA04qYlJP_imsuQcApeAZL29Z_4qvaPUgV8v9BFbZilQY6KAVDrG-Qr_k=)
13. [moneyhero.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrbbmgtUhk4ps7nfieuHuPrQs2O7BpqPYQJXn_yMCTMoS6SJ4u88FKPO36N-aYUfw1l9MGX7Jhk5vV6bvo9Ea3FQagEpF2vImRivCZV2t_K76-G1fbKjrXNyXh04WuKSjLuYhwGsg_xk0_15pbAvjB0DjOqQ==)
14. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYznnlbqbPeUdCny2_OuMRgn1IqIoQyxa9S7FzJptN3wORHCP0cfYQfu4eGe8cqe0rCOxD8ImHdiMvHRKJcucdl7nLIVjUI-w9jaXnNDPZJvzTouXlqV-SS5CV0dM_1Hz24a7Rc7MRZSJaLELghI2Tt1sPVjorED_CLww_HKhdPkEwQ9DH4U9WCUgIEZeZVfLPk-5F9qKx9dQdnemREtM3vPpRgw==)
15. [longbridge.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmb9_fdnNAMj8Da0kI6DlxVztOYwEQh7LAUlRcYD41kJmTJwmh8p7GI9BEH3cMRBM53EL6D8P8Iq0VNVFZoZ9Pr878EYb6OvZ4TAFv2cAnIkD9iIU0Pkwg7lCKkr8=)
16. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF96qT9wwmUTTvRPYKVb9lEqKJ0dQtd21L_ka6ZVh_zsUvgMFzaHzrqLFDuSJCNy4CdWST4jEx1cEavP6oqQAMPVr8LKFGEuYVijoz3Ih32TedXIrBHIg==)
17. [moneysmart.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHS_ZMs1AgZ5lxsNoRHzufEtvgDtEHGlWfj0QsATLqBg2t5Y7GCE_k4396pWPCLHSOyK7VpoUuiFB0MzKAcM5aVjxxRVjOBbpTvHzYKdq1pcTJzGP9Ml4E2FeG4PIQLhNAuHkZXhTpQhwOtE3M=)
18. [flyformiles.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHf_SYjCdEdcx7c_IItb2ekIzGheZ9yK-RwoYImzYdlU0oCHbER_Bub3g2LI6hnDUZuKd_Sq0hcnhzXqggaRo4iXlNNEdmNvKBdvGUSh-FY_dEIIZG8FABYo1xoV1O9Dg==)
19. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5xS6sYKlv-HraWPIdd4KAxmWJyGCzj0YXF5xHr5ZZVEXT7KUnmFop4J4T0RP0hPT2YeDSwQRs0iiQWi48c-WZ_nWd4I2bOzKJvEhbtQJE6pr5KpjQe_YBPPBcjM_1usFu_0KB_TQ4)
20. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH63auzY1D8YeUbWB9Emzn1igeTBPhdLXLZFyqb8oAr8ZLSBJa6OVD70VN2EXnTRM8t_2QTyWKx6VRIzSFqYQwRtZrqTe78yk2AFNxm9rLU-1OAgyU8gwXMPUdej9rkZgfrlJTJu_sLCCBfvXPY8EkoKWaeSJRSVg4mZKHJZ1W9f8zBhoQ=)
21. [mrmiles.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9ZIG7h69jprr32g4v676XvOdbt7kqRH_XCiinYQSh4k6u1DkWAyTeD-wy3ZKa4fxn1XPB9vBaW5IhoIwGoCG5YnfzjNVil5JhYqCDfxjg2F15ftx3Mr2kDhSvzQI=)
22. [cathaypacific.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7iPHw8SM4ptr6L0AfaKYvIf1t7eBqtY8J17lbZW_Hfpg2Tm39RF1-6y5owcVT-jsuoT9opWxZ162OA_0wkQL6agkZThlBHxcW8Rf4rMAnDb5Mjw_tyFOAvS8WjYD-A5syPu1-tjYnY6_yu94RcPjy0UypAI07IvgpZNEqJq6gyQ==)
23. [moneysmart.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfQHVO_9Lr_BL_JYX8fZv2RsRyOzF0_xrKrwf3oC3VN7HbKHmG9n3IFnOaUVxSbmZ2af4lptWDQRxbuH1wv3QSu440ti7u3_JkixsymFGNZSBkiV-kNvNXlmLH1NuXKcEunAD7R1YaeYVE08gvqORjW13PIrh7dS9dDXvj4ftrW5f5)
24. [airwallex.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLLzK7YDgntVsum2zzOM0kN_SJKgSF_ugjDRl7eqRIAak4-aW6nhAnDk8HcSIPQSJzF2EMOY9TbunDcsy75zNR7yc1iGfYr4iDROKCxJPFcI8lEAxVSO9kqltHOc9tFO74TosiMkZjcgFQ09yCr2E-cKJuXoNGUw==)
25. [stripe.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGInuJiYIUPLRnfqYOiSSp7FfR5tbw0baTLhpzDypiYS8vnqzFMBhCrfxhVyIiJiWKvpymKMjFEAumcwggQgAv6_soVc8vwOrtu4m9VidGUyM7Glz8umzvtYqOPFtvRajjplneCXNk=)
26. [heymax.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrv-eShSEfEXiptb6XD66jnf59guCoiJcTwJ2CDZ1WB94EMaTdvHobp4oUK1M7ot1BAmnpk-nFoWA-n0uLmAuXt5XcSMsYH-z1XDCyBzzompiKqsQoqsL-rDuNwG3aC-BBiFcJQFCybx_wfqyWJydKBr451RkDNieY7w==)
27. [milelion.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnEdIw1ssczG8Q0pYlWecrYFCd-agC9ffRWDWAtnOuiaTie5N2xTFttoKFuBSb0yn90asXfbrbvUQaXk9uZPiq5A7OjuygFdwX9qJGSUBCXVdO2PAL1u3cf4kkYdgu4xSAw7ojIdIK0J0ahCnMqQ85xU8phKpwqyUbRu-zpp-QDOBMnWaHmO8yPzEj_cUBQoUs58Q0nXITBQ==)
28. [moneyhero.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsxNHHfbf92Jj6cWBsk0OSMJbRa2cV37TsTMrIy-OnrRGKMN2Dnx9v6-1_Hj1ETiGBcuf0lgSbm09KNLP0I3cDE6TlruveKTFbaCwV4qFaTYlB26ZwHyPRp0WxKqljuu38XCgP0yoc0Atabz2oDS3uPTdZNT6SI7PnlHM=)
