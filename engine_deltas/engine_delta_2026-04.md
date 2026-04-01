# Cathay Miles Engine — Deep Research Delta Report

## Date: March 2026

### Executive Summary and Key Findings

*   **SC Cathay Online Rate Correction:** The engine currently assumes a flat HK$6=1 mile for general online spending. Research confirms SC Cathay actually earns an elevated HK$4=1 mile for eligible online retail transactions [cite: 1]. 
*   **The EveryMile Supermarket Trap:** The HSBC EveryMile card explicitly penalizes supermarket spending, reducing the earn rate from the base 1% RewardCash (RC) down to a mere 0.4% RC. This yields an abysmal HK$12.5=1 mile [cite: 2, 3]. Your engine currently defaults this to the HK$5=1 mile category, which is a critical over-calculation.
*   **The Great E-Wallet Nerf (2025):** The era of passive mile generation via e-wallets is officially over. As of July 1, 2025, HSBC entirely eliminated RewardCash earning for PayMe top-ups [cite: 4]. SC Cathay has strictly excluded PayMe, AlipayHK, and WeChat Pay from its eligible transaction definitions [cite: 5, 6]. 
*   **Hard Spending Caps:** The HSBC Red card's 4% online rate is strictly capped at HK$10,000 per month, and its 8% designated merchant rate is capped at HK$1,250 per month [cite: 7, 8]. The HSBC VISA Signature Red Hot Rewards 5X multiplier is hard-capped at HK$100,000 per year [cite: 8, 9]. The engine currently does not track these accumulation thresholds, risking severe theoretical over-estimation for high spenders.

The landscape of Hong Kong credit card rewards is highly dynamic, characterized by frequent unannounced revisions to Merchant Category Code (MCC) processing and restrictive promotional thresholds. While the foundational logic of your existing Python calculation engine is sound, it suffers from several critical rate inaccuracies, glaring omissions of zero-earn ("nerfed") transaction categories, and a lack of threshold awareness. This Delta Report synthesizes recent banking terms, active 2026 promotional frameworks, and MCC coding realities to provide the exact logic necessary to patch the calculation engine. The evidence leans heavily toward banks aggressively closing loopholes (such as e-wallets and tax payments) while shifting bonus structures toward distinct, highly regulated online and travel categories.

---

## 🔄 RATE CHANGES (vs current engine)

The following tables and analyses highlight the exact discrepancies between your current Python source code and the verified 2026 banking terms.

| Card | Category | Old Rate (Engine) | New Rate (Verified) | Source |
|------|----------|-------------------|---------------------|--------|
| **Standard Chartered Cathay** | `Online General` | HK$6.0 = 1 mi | **HK$4.0 = 1 mi** | [cite: 1, 10] |
| **HSBC EveryMile** | `Shopping (Supermarkets)` *New* | HK$5.0 = 1 mi (Base) | **HK$12.5 = 1 mi** | [cite: 2, 3] |
| **HSBC Red** | `PayMe / E-wallets` *New* | HK$25.0 = 1 mi (Base) | **0 mi (Excluded)** | [cite: 4] |
| **HSBC VISA Signature** | `PayMe / E-wallets` *New* | HK$25.0 = 1 mi (Base) | **0 mi (Excluded)** | [cite: 4] |
| **HSBC EveryMile** | `PayMe / E-wallets` *New* | HK$12.5 = 1 mi (Base) | **0 mi (Excluded)** | [cite: 4] |

### Detailed Analysis of Rate Corrections

**Standard Chartered Cathay Mastercard (Online Spending):** 
Your current engine places "Online General" into the default `else` block, assigning it a rate of HK$6=1 mile. This is mathematically incorrect. Standard Chartered official terms dictate that eligible online spending earns up to 2,000 basic miles for every HK$8,000 spent, which directly translates to **HK$4 = 1 Asia Mile** [cite: 1]. This elevated rate applies to general e-commerce, making the SC Cathay card highly competitive for non-travel online purchases alongside the HSBC Red card.

**HSBC EveryMile (The Supermarket Exclusion):**
Your engine currently allows supermarket spending to fall into the general local spending catch-all (`rate = 5.0`). However, HSBC explicitly classifies supermarkets as "other eligible transactions" rather than everyday spending. Consequently, supermarket transactions on the EveryMile card earn only the base 0.4% RewardCash rebate, rather than the 1% general retail rate [cite: 2, 3]. At the EveryMile conversion rate of $1 RC = 20 miles, 0.4% yields an effective rate of **HK$12.5 = 1 mile**. This is a trap that catches many consumers off guard, and the engine must explicitly isolate this category [cite: 2].

---

## ➕ MISSING CATEGORIES TO ADD

To ensure the engine is exhaustively accurate, you must expand the `CATEGORIES` array to include the following distinct transaction types, as banks have explicitly carved them out for reduced or zero earning.

| Card | Category | Rate (HKD/Mile) | Cap / Limit | Notes |
|------|----------|------------------|-------------|-------|
| **All Cards** | `Supermarkets` | *Varies* | N/A | **EveryMile:** HK$12.5/mi (0.4%) [cite: 2, 3]. **Red:** HK$25/mi in-store. **SC Cathay:** HK$6/mi [cite: 1]. |
| **All Cards** | `E-Wallets (PayMe/Alipay/WeChat)` | **0** | N/A | SC Cathay excludes all P2P/E-wallet top-ups [cite: 5, 6]. HSBC ceased RewardCash for PayMe on July 1, 2025 [cite: 4]. |
| **All Cards** | `Insurance Premiums` | **0** or *Low* | N/A | **SC Cathay:** 0 (Excluded) [cite: 6, 11]. **HSBC:** HK$12.5/mi (EveryMile) or HK$25/mi (Red/VS) via online bill pay, often 0 if paid directly depending on MCC [cite: 12, 13]. |
| **All Cards** | `Utilities & Bills` | **0** or *Low* | N/A | **SC Cathay:** 0 for online bill payment [cite: 6]. **HSBC:** 0.4% RC via online banking (HK$12.5/mi to HK$25/mi) [cite: 13, 14]. |
| **All Cards** | `Government / Tax (IRD)` | **0** | N/A | Inherently excluded across all standard earn rates [cite: 6, 15]. Only earns during targeted, short-term tax promos [cite: 16, 17]. |
| **HSBC Cards**| `Education / Hospital` | *Low* | N/A | Usually treated as 0.4% base rate (HK$25/mi for VS/Red) [cite: 13, 18]. |

---

## 🚫 EXCLUSIONS (Zero-earn categories)

The following transactions yield strictly **ZERO miles** and must be programmatically forced to `rate = 0` in the Python engine to prevent users from falsely assuming they will earn base rewards.

| Card | Excluded Transaction Type | Details & Sources |
|------|---------------------------|-------------------|
| **SC Cathay Mastercard** | **E-Wallets & P2P** | Octopus Wallet (O!ePay), AlipayHK, WeChat Pay, and Faster Payment System (FPS) transfers are explicitly excluded from Eligible Transactions [cite: 6]. |
| **SC Cathay Mastercard** | **Insurance** | Insurance payments are strictly excluded from earning miles [cite: 6, 11]. |
| **SC Cathay Mastercard** | **Tax & Utilities** | Tax payments, utilities, and tuition/examination fees paid via Internet/Phone Banking/ATMs are excluded [cite: 6, 11]. |
| **HSBC (All Cards)** | **PayMe Top-ups** | Effective July 1, 2025, HSBC removed all RewardCash earnings for PayMe top-ups [cite: 4]. |
| **HSBC (All Cards)** | **Tax Payments** | Settle tax to IRD yields zero RewardCash unless a specific seasonal promotion is actively registered [cite: 15]. |
| **HSBC (All Cards)** | **Crypto / Quasi-Cash** | Transactions at non-financial institutions for foreign currency, money orders, and traveler's cheques earn zero [cite: 15]. |

---

## 📊 SPENDING CAPS & THRESHOLDS (Verified)

Your current engine calculates absolute miles without respecting the mathematical ceilings imposed by the banks. High-net-worth users inputting large amounts will receive mathematically impossible recommendations if caps are not modeled.

| Card | Cap/Threshold | Amount | Period | Status & Impact |
|------|---------------|--------|--------|-----------------|
| **HSBC Red** | 4% Online Spend Cap | **HK$10,000** | Monthly | **VERIFIED.** Spending above HK$10,000 reverts to 0.4% base rate (HK$25 = 1 mile) [cite: 7, 8]. |
| **HSBC Red** | 8% Designated Cap | **HK$1,250** | Monthly | **VERIFIED.** Spending above HK$1,250 at Sushiro, GU, Decathlon, etc., reverts to 0.4% base rate [cite: 7, 19]. |
| **HSBC VISA Signature** | Red Hot Rewards 5X | **HK$100,000** | Annually | **VERIFIED.** The 3.6% Dining (or chosen category) rate is capped at the first HK$100,000 spent per calendar year. Beyond this, it reverts to the 0.4% base rate [cite: 8, 9]. |
| **HSBC EveryMile** | Overseas Promo Tier | **HK$12,000** | Phase | **ACTIVE (Jan-Jun 2026).** Must accumulate a minimum of HK$12,000 in overseas spend in a phase to unlock the HK$2=1mi rate. Maximum bonus RC is capped at $225 RC (approx HK$15,000 spend ceiling for the bonus) [cite: 20, 21]. |
| **SC Cathay** | Qtrly Bonus Threshold | **HK$8,000** | Quarterly | **VERIFIED.** Must spend HK$8,000 cumulatively on Cathay/HK Express to trigger the extra 2,000 miles, bringing the effective rate to HK$2=1mi [cite: 1]. |

---

## 🎯 ACTIVE PROMOTIONS (Current Month: March 2026)

To provide an accurate optimization engine, temporary modifiers must be applied. These are valid as of the current 2026 operational environment.

| Card | Promo Name | Details | Validity |
|------|------------|---------|----------|
| **HSBC EveryMile** | **Overseas Spending Offer** | HK$2 = 1 mile on overseas transactions if the net spending amount exceeds HK$12,000. Phase 1 runs Jan-Mar 2026; Phase 2 runs Apr-Jun 2026. Requires Reward+ registration [cite: 20]. | Ends 30 Jun 2026 |
| **HSBC EveryMile** | **Agoda Flash Sales** | 15% off worldwide hotel bookings year-round. Plus, monthly 30% off flash deals on the 15th of every month [cite: 22]. | Ends 31 Dec 2026 |
| **SC Cathay** | **Overseas Extra Rewards** | Earn an extra 2,500 miles upon accumulating HK$10,000 equivalent in non-HKD currency overseas. Requires registration [cite: 11, 23]. | Ends 3 Mar 2026 |
| **HSBC (All)** | **Travel Guru Membership** | Tiered travel rewards. Level 1 (GO), Level 2 (GING), Level 3 (GURU). Provides up to 6% extra RewardCash on foreign currency. *Note: The specific EveryMile tandem offer under Guru was discontinued April 2025, but the core Guru FX rebate remains active* [cite: 4, 24, 25]. | Ends 31 Dec 2026 |
| **SC Cathay** | **Time Deposit Bonus** | Up to 38,000 extra miles for setting up a 12-month Asia Miles Time Deposit with new funds of HK$1,000,000 [cite: 26]. | Ends 31 Mar 2026 |

---

## 🏷️ MCC INTELLIGENCE

Correctly routing spending into the correct engine category relies heavily on understanding how Mastercard and Visa code specific digital merchants.

| Merchant/Type | MCC Code | Classification | Which Card Benefits |
|---------------|----------|----------------|---------------------|
| **Foodpanda / Keeta** | 5814 / 5499 | Fast Food / Convenience. **NOT** processed as standard Dining (5812) [cite: 27]. | **HSBC Red:** Captures 4% (HK$2.5/mi) because it is processed as an Online e-commerce transaction [cite: 7]. **SC Cathay:** Captures HK$4=1mi as Online spend [cite: 10]. |
| **Uber / Uber Taxi** | 3990 / 4121 | Online E-Commerce / Transportation [cite: 28, 29]. | **HSBC Red:** Coded as online spend, yielding 4% RC (HK$2.5=1mi) [cite: 7]. |
| **HKTVmall** | 5311 | Department Store / Online [cite: 30, 31]. | **HSBC Red:** 4% RC. HKTVmall is the quintessential online shopping portal [cite: 7, 32]. |
| **Trip.com / Agoda** | 4722 | Travel Agencies / Online [cite: 22, 33]. | **HSBC Red:** 4% RC. **EveryMile:** Explicitly designated for Agoda promos [cite: 22, 34]. |

*Note on Bill Payments:* Paying utilities or insurance via a merchant's website (e.g., entering credit card details on the FWD or CLP portal) sometimes triggers "Online" MCCs, but banks actively filter these using specific backend exclusion lists to prevent them from earning 4% online bonuses, forcing them down to 0.4% or 0% [cite: 12, 35].

---

## 📝 RULES FOR CALCULATION ENGINE (Python Delta Updates)

To bridge the gap between your current engine and the verified 2026 landscape, the following Python-parseable logic updates must be integrated into the `calculate_miles` function.

### 1. Update the `CATEGORIES` Master List
```python
# ADD the following to the CATEGORIES array:
"Supermarkets", 
"Insurance / Utilities / Tax",
"E-Wallets (PayMe/Alipay/WeChat)"
```

### 2. Standard Chartered Cathay Mastercard Delta
```python
    # ══════════════════════════════════════════════════
    # STANDARD CHARTERED CATHAY MASTERCARD - UPDATES
    # ══════════════════════════════════════════════════
    if card == "Standard Chartered Cathay Mastercard":
        # ... existing flight/dining code ...
        
        # [DELTA 1: E-wallets, Insurance, and Tax earn ZERO]
        elif category in ["E-Wallets (PayMe/Alipay/WeChat)", "Insurance / Utilities / Tax"]:
            rate = 0.0
            notes = "Strictly excluded from earning Asia Miles by Standard Chartered terms."
            miles = 0.0

        # [DELTA 2: Online General explicitly earns HK$4 = 1 mi]
        elif category in ["Online General", "Food Delivery", "Travel Booking (Non-Designated OTA)", "Travel Booking (Designated OTA)"]:
            rate = 4.0
            notes = "Eligible online retail spending earns HK$4=1 mile."

        # [DELTA 3: Supermarkets fall to base rate]
        elif category == "Supermarkets":
            rate = 6.0
            notes = "Supermarkets earn the base local rate of HK$6=1 mile."
```

### 3. HSBC EveryMile VISA Delta
```python
    # ══════════════════════════════════════════════════
    # HSBC EVERYMILE VISA - UPDATES
    # ══════════════════════════════════════════════════
    elif card == "HSBC EveryMile VISA":
        # ... existing designated/overseas code ...

        # [DELTA 1: Supermarkets are severely penalized]
        elif category == "Supermarkets":
            rate = 12.5
            notes = "MAJOR EXCLUSION: Supermarkets earn only 0.4% RC (HK$12.5=1mi). Do not use this card."

        # [DELTA 2: E-wallets are nerfed to zero]
        elif category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            notes = "PayMe and other e-wallets no longer earn RewardCash as of July 2025."

        # [DELTA 3: Insurance / Utilities]
        elif category == "Insurance / Utilities / Tax":
            rate = 12.5
            notes = "Online bill payments earn only 0.4% base rate (HK$12.5=1mi)."
```

### 4. HSBC Red Mastercard Delta (Implementing Caps)
```python
    # ══════════════════════════════════════════════════
    # HSBC RED MASTERCARD - UPDATES
    # ══════════════════════════════════════════════════
    elif card == "HSBC Red Mastercard":
        if category == "Shopping (Designated 8%)":
            # [DELTA 1: Implement HK$1,250 Cap]
            if amount <= 1250:
                rate = 1.25
                miles = amount / rate
                notes = "8% rebate applied (HK$1.25=1mi)."
            else:
                base_miles = 1250 / 1.25
                excess_miles = (amount - 1250) / 25.0  # Reverts to 0.4% base
                miles = base_miles + excess_miles
                rate = amount / miles  # Blended effective rate
                notes = "WARNING: 8% cap (HK$1,250) exceeded. Excess earns base 0.4% (HK$25=1mi)."

        elif category in ["Online General", "Food Delivery", "Travel Booking (Non-Designated OTA)", "Travel Booking (Designated OTA)", "Ride-Hailing (Uber/Taxi Apps)"]:
            # [DELTA 2: Implement HK$10,000 Cap]
            if amount <= 10000:
                rate = 2.5
                miles = amount / rate
                notes = "4% online rebate applied (HK$2.5=1mi)."
            else:
                base_miles = 10000 / 2.5
                excess_miles = (amount - 10000) / 25.0
                miles = base_miles + excess_miles
                rate = amount / miles
                notes = "WARNING: 4% cap (HK$10K) exceeded. Excess earns base 0.4% (HK$25=1mi)."

        # [DELTA 3: E-wallets Nerfed]
        elif category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            miles = 0.0
            notes = "PayMe and other e-wallets no longer earn RewardCash as of July 2025."

        # [DELTA 4: Supermarkets and Bills]
        elif category in ["Supermarkets", "Insurance / Utilities / Tax"]:
            rate = 25.0
            miles = amount / rate
            notes = "Earns 0.4% base rate (HK$25=1mi)."
```

### 5. HSBC VISA Signature Delta
```python
    # ══════════════════════════════════════════════════
    # HSBC VISA SIGNATURE - UPDATES
    # ══════════════════════════════════════════════════
    elif card == "HSBC VISA Signature":
        if category in ["Dining (Premium)", "Dining (Casual)", "Cathay Partner Dining"]:
            # [DELTA 1: Implement Annual HK$100,000 Cap Warning]
            rate = 2.78
            miles = amount / rate
            notes = "3.6% Red Hot Rewards. *Assumes user has not exceeded HK$100K annual category cap.*"

        # [DELTA 2: E-wallets Nerfed]
        elif category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            miles = 0.0
            notes = "PayMe and other e-wallets no longer earn RewardCash as of July 2025."

        # [DELTA 3: Supermarkets, Bills, and General]
        elif category in ["Supermarkets", "Insurance / Utilities / Tax"]:
            rate = 25.0
            miles = amount / rate
            notes = "Non-bonus/bill payment earns 0.4% base rate (HK$25=1mi)."
```

**Sources:**
1. [moneyhero.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9ECFZgYkm1i5PleaYxKEV9b4O0DwFLsfFCsRlQcKbk8I-cGf3MTc2_597ZnXxrZfFK0oQoKGDc5GY-VruGBZa7Lx31BDVuiUSV2nCl43VjbwUgsV6qVszQnqIm81AVAoOlxtxeKKKttkaBlmplfoMZhOR-g==)
2. [jetsofind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfvnQs4tn9SSD9jmd8_Ab2nM13YbzKwbtOQjbbQtLLhNSLXbbSkVbhd3IROlHi9jQQ-G2gHed4btfQr8wmvNtxGvRmPep72vqRrJeOwYakDIm4xRHXC-cBk8AdxpefeBVZXA2mXYtRAQN2dLdnnFtrEmRkNX0J60XYWw==)
3. [jetsofind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLd3ECJVhpuGYmdVYAu_xxLnJcQBQjmyocrcQG3ipNSpCPTY1Fj3cxD29cnWsGtJ-qTpgNaksdgsMxt-OfiZaHq6y4LnTc_62Y-MyLgS5sl8EVyJFdCt1bbxokTzn4ZTY=)
4. [flyertalk.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7GO3mF2JVOBovarZ8NT6IA7H_C_6O8kaj_S7PkL_KUdlLrAsHn6hZMeK-Wuhu4ed2DmuCN_G7hc0fJrSAYaz0DspmCwrReJV_Rhp81xX8TdSgF9Jb8xBEzNoIb8f-8vMG7BESzPSrx0MwOpj35IZ9FAF92gmfNuv79XdeSZCyvctf_0pg3rFR9r7h82F6aoZT3Uu4nkd_k4DOL0rvCJpa4VIG-vEdZ4I6MjMZqot4gVim-NVJXvd8)
5. [flyformiles.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKaRwnwsk6IK1TZhyFxXeM2EOlT9qiw7kYAdp5ORpscbFAlJ5pWBEeun6AFPqN3_EhIrXbl0ul8jl4kKW0geXoEANa43APy2KnGaEdjT4473IhsKdgN4--1lx3BShBxQWx8x-dwyU1FoeYR03ZQ77xzEfxe5lyUkWmtuv9IKCWyaonWl5UQ84mNBBPq9jjQLgevX6X2tmLX6r2)
6. [sc.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvkIvScG__fw7GYjM9GIBZWSmmX4ixqoPkMT4OsxL-yQPlTIbV4PCnGi5gIUM3UMysQBw134b7dZhZ6sSvYE7pyQXdVEwhPFtLi0OjgE6UJgMvTlgQZNHbJ132JQ3Jj1xGgpV-Aw1GhYvNtIZou979ceBJQaZSiJy2ZesBVk6TZf0pJ9ReoQ==)
7. [moneysmart.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCQmvkNfXAXJW2O4bmEn6PWhuUn907CvGzUValDF2sXVU3su0HWYiiEmb7A-XQRw2qTg0x83vFlEai1y2wqnFmmGeKGKFH9A_q3QDGGLiSPX97XeA32Xb-KNZMXYFH3LIZAqXxckTs-iKLIuk=)
8. [jetsofind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdMluWMttSNnzGPRDRKUubBDMyphbuHm25kAI4AoMv4gVrcg46JuRQKgYoPqopvhMeV9A9kmb1jjPHqoT6yoCyArfWNvqY9Kue0edemNSGPHpSu2FpnsMLIFvLmZ4VbvVVSY4IqmPSfeKpRw==)
9. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2SENqDvpcPMhnhcFtwW2RohPk3-41UnSJh4EKJankNo29I8v2TacEv1Huu_Du9zRZ4JBcnZxbyQeUtYJCV8PFqSKJwM6zAcZ9ZLOna3ERGe-D8f_eCKhFGpCU_n8dCYIMFp5NIqPrOMd6jnIidTyUmhG4sdN0ofGytcY57IO7e9B1kDE=)
10. [wise.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEg8iVz3Y34IakYH-GkgopPJZ8YKQvQx2OT6eagU5EFqIdKGc86Sj6Yq78RG8OISEtVtnk1BoB6ARM3Ear-Rn2587OiaHEhXiLfGtJdYIFNNpLhhr_b5JkvxrHyQqIv8YJxBoQHxv6J)
11. [sc.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzk965f66T1kSx0o9ey-oeAUzuvUBfMg2tWgWeB1ntCxbIJt81Ky18IBC9-1d-kBOEk0BOsFZzAkapY9F_z7rhoXbLBuDBVRCKbSCn8Y2l66NllEbnqsVTbdzRdU9UsPlMfD6kSMqXOczB5PY8JMoyOsKjEjI_4saJWQBsiKpxT3lFzvuM6PVA2XYjsVU9SUfXgw57Cr9bbH5900497K3WduQ_JCT0bH1dGMICpB1Ci2CxkRE3rROFUYdt81YRVv9FUrplFor8WTuKSHp0Lg==)
12. [bowtie.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDppNiRMSWqLGVbBjw88UPJnEpSrp887hjfOQOIuMN-t88HrIjNqADbWcRKxY9otZxfujM0UgKb_SFDriYFRSt0iiETfCuUkfzeCa-ogqGCgoSrhFHSRk6hnDgkQgcBalCaFJ_jQvqTLisVN3v_f260PRXGypch18OOhSk8VWOmRVIM7jjgIKTHEs=)
13. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfT7GnqDyGHmBAfoZXlqxJ4dVS0O-lpvb2G1lMTzK_Q-DiDmordncSGhbP6xApS7mbHQDp78aYjEx0wLjIHCv2PPRIQQ8YlkQqRwT8MTN4YUzNSkZ8bUwM878Rj98VkVsw1LrqhPVllA==)
14. [moneysmart.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTiOk7vYeswjRdYsB87hujUmKzk7ccBvEtz0qJrbH1cz3smKE49V_3EXRq0FSao-FinyC-FR9mWNnvt_boEy3ZBpaH66l22sVfQCe4hzBYzK11QOEVMGoX4QFHdzdpl8HQHjHj4nlqnn-LqIKwAGmT-5EhjAwrhScD4FGC3sZePTdh)
15. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyTPXhiRMNSSCjGopTzZmd483gSgReuUzneDjhwNHPVZxJt7vlCgkTT0XscY51fgeEOraAX-ONYSVP70vWGLY2GCfqfykfm8JJ4hKbnIXUj2UZvY05SpRlLjTErk2npCeX6gL7fhPzJftHTzn4FTzJnC1UlHcsmeMfT43URu_GwmQ=)
16. [longbridge.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbKSCT6P52oKG9yboc7W96mMyS9XCRninj0ZX8hrmwR1XqsgJyMacQRlnimMtoHv011o2j2plDNs5Txs5i1Qd9IgFZNo5hS9TBRHwBIfflEqLwJV763D1iukklJL8=)
17. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJkjgPx1tFntuPsD-Wgv547lrrG-N26nMBlAyzY55odPECSEL3Xx7XLoOo7sJB_QD7sqf5U8MQroccEbFJuHZiNaF3OGuaGujTAIlQ-xeAivqEPbg3XXBo-yG0u04D5ayt51-G441A4ewPazQNOQta7Q_qGA==)
18. [flyertalk.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhjkkEN3K_nBE0p-HVTujrUxFa_3NX1H6IFt-wjR0kEF9JgUrKo79goOG0piIQpGjjTkoALRTrntRGIoaLkXSKZgM2iA9TP-ulAovG7Q_HkcZF5vMXhg-wuAbvkVY1R8em7GWC_VmkUeWPVusHDnbMzUtdu2vDjAiBvK16ImzNGOcD0LyKkhluizJWzUzJ1MSSAz31ddWQTeNhYaLwH9429M9Rl13TgdnL5Pq4uWahM-YmqKvEBg1WMQ==)
19. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXacNaU_VhVWUGeUop7fRBofgb2HnHyhza43LuHh_VNvuLFiz-9NT2YTJr7gx2rlrXQ7ujxX8YBrnCxm82G6SifoPbUTtsRecvKlKds1VUbZDPwmVQXSZ1AT9UekY0WWckxt-yO6zV)
20. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFX4-YgKRUMiyYaePIkqqsI4KmJACgRysaNqS0oXI5mT-Fx53Ku4G_d6kpPjT-BG6hx1a4drHtKUkpXgXiYaa92g968rhqJT43KJ8ZFhJnwCuh4-fIwiipslJNnQTGnG32vaL39YnBKlCjatfeysGVZC0uS3XIjF271z0nkb5PSW3_7bvY=)
21. [flyformiles.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGX0QYlqev47L1tV_kuP60OEihPOCjZ7G4Ac43Ree9VItNfGDjm8oJqYiPFSS_saBcM-qtgIb3OSEvg5sth9h4xBhLzcDDxL-fSarp-paxsOQ2tdiCJDIVBl8yw9x7MUGIWOG4TWM8fiGCHuro4TG5zeoLaUT2N)
22. [agoda.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJ0i6d9pPNAmIBHJcNdNTZqhmKbgECog3GCkcZD3WB-L7ySZi5_fA5GJfwjrpyHb6BMlpShxXSGqwKM2yaNWf5qmeZ432S2VxyiWE8i9NxW8NdVqKcj3BM)
23. [cathaypacific.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESxlvUiby3TWf8PQjUVJAYh_Z67C7eKp2LmUlqUXwlqnafkt7MqwwoWR4qv_1ZJdeSLCG0NcdTcKehDnXedXesQLdBCJQgkeUyaJvGYWDqUwSf55umOpvShz6rmrjD45E23Zln7F1ZijCjUP2AioNuaEUpqCaU9k4qlWgSX4ozSg==)
24. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGY-quOi3Xr7Fv-CDrkd6bRKflSMBfO4DMEIMqCgzSbLzFakcoQ7dxEsBPu9YxmmZeV0OSHKSeO4RqitEcpUUPWCXvoh5VRtYbORBHJAI16SMY6zjcZw53-4oerSnTL-VaH1Oe-KSZLr9BdJsELrB8rZHjXBuzJQ==)
25. [flyertalk.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7DklWKGXx8uhoNt2ABGNYrbZZWF65QK6ybT9kgGRksRnrAVunjbviXMQ3WoK7rtnTR-WfW95R4NKDUCMISWAVotM7pHi2q1qHqlD4Nwnl0pKxNiVZu3HXhfV9R2hMLyCXO5owSezTu9Eg)
26. [sc.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAOIOh0iKxCdXLWJcpeWL1EAd-vuX7GLlJhNGAtK3vx_I1fOAigcd3np9XNsbhqs0SB-poj_e4IZ0sJXSDERath_6qlFIPLqAgoMR50be085XPbre5iZsJaab66fZb2U-ZpXC8QWk4SzNUFxs=)
27. [heymax.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFun9xZsoQyXTdhcxko6OcOJUcux7dDY-X4vIzvYCw21rjvi9pRehggpjfju6b4fZrOozZXdVHGTNeAUiXR1FopDMq8v1Z0_PwWt55t_t1VW0S__KS1bQ47ol6upZRM9dEFD38CP49larY6C1hz7aDrIfqRCvr4GQ4g9Q==)
28. [mastercard.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG81A0TMrb_a21CNOccdU1OT0xrmH_ck97U_m3YuCInDf15GNBpldZlQN_NKxRZhDp4IQQDtXN6M_YkujnXJcr33C0pqMynLpje-Unxa4mR5CZmSV_JctskFPQcj_lJ2wbduUjGMQBtFzQakD5pf7v-rH5KtvNR27edFKKyM7j0PUtMBWeAnRrlI01AHeCwMrifai7tHL2EumpR-tyaCnhZO2n1epYnpMaanHw=)
29. [dbs.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHa2XvMoPIaL2aepqjvJefbeIsJ1g1nU7Iz9_Z3oAwje8YCfVVCp44NWOW4vyHu_5GIN6RjtvU4cXClaovi94TaMO1PzwTr7Pc2U31OuQw0sZaJEaGUVQ0ytE7xEn2mrg1Da8ZD3wVIXgtKv2r9os1B-BBQj_usQr9-gts8Qbh2BLbkVRZpw3P1x0_w-w==)
30. [hongkongcard.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGd9IqHI3nGa0kRhaRzjaqtJcySLrY2asvP6UnJMmasLbTsJOYtbSS5oVy35e3mS28rhL2lzXIYiCw8WgvgNn8bHFE_VyVTlQyWVgWT3bC9-w5acdvNLFNCJya8NTiV21f0dWuQB9W7cjQn42yM5Qv3CwLDVp6mziK9MUzM415nJv0SIzSu6AcAR2t4egyaoyCyuGJIONDdAGKgkzppOMMJ2G2eBw==)
31. [moneyhero.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_D6xVqwsav-W2zWLdxFZabyro2EPChULaqQBguekVcDL8lIHqoE8MjhvI6xFo4V68NiZCfzAzYZFOUmvo3nq0DxPbjC3qS4bomhWUyub6uzgcFj4wT3_ixay1aQp62imDhfDoFtFxUwWd6Yc8YqfyGPcXwWrcNiwgA0c=)
32. [moneyhero.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmKLTYQ2HtyrBadtsauofDR0WPwif2lu2FnZrmCiKBm6p9BeGdOl6FcTDPljCbrFgoqSRpq6_KhNqYOpXygaVznmTMmzQCQJKNJPeJD4JMfnmLw_4iIAHhIXrb0CT6AuTT4PaXBnx9XDIoLGWjIg5lUaqMTfRp-A1sSlu2tKQ=)
33. [agoda.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiLJvS-WnOPRiVVW_lj_05OBXCZsQBqU7RemWsLHn4LBFm3xiPf9QAjvktiY4VGoiYBCE7X5-MTY4vu_RIwIH6moSADWAXKrH4YAkiZX_qABatbLGY7meu)
34. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDweYjnh6vH2qPZh2oxj_jvIExIJrCrSpv92O1jZ8lJR-XN2JpdKB14Cx4VuBUSg3HlnKizaFgJmnFi68wl47cHsAbDn9wb4b2KLuWudUoLheOWjkq9LgtaN_qkOpKQ8W2UX4nnc7weiHvyenitHU2ivDXkzxhaLKGzpB9_KhujvbtHSF_qLF88BIoYe1WIpk=)
35. [jetsofind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVhTi51eZ4wJRtolfaYVnh5yFproHcDkK-8Mb1xxE3qkckRGC-NvnMo_YhRAFeSUCuuORUJjdcsz_hIlwMC8SgToksnm1_d5mSfTf6FD1uykvGZ-PWodAEI6g=)
