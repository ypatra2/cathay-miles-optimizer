# Cathay Miles Engine — Deep Research Delta Report

**Date:** March 2026

### Key Points
*   **Rate & Threshold Adjustments:** Evidence indicates that the HSBC EveryMile card’s overseas spending promotion operates on a HK$12,000 minimum threshold, with nuanced tiering that must be precisely coded to avoid miscalculation [cite: 1]. 
*   **Promotional Stacking:** The introduction and expansion of the HSBC Travel Guru program significantly alter the effective earn rates for overseas physical spending across all HSBC cards, potentially yielding up to an additional 6% RewardCash [cite: 2, 3].
*   **Category Exclusions:** Research strongly suggests that food delivery platforms (e.g., Foodpanda, Keeta) and ride-hailing applications (e.g., Uber) are strictly partitioned from standard dining or transport categories due to specific Merchant Category Code (MCC) definitions and cross-border fee architectures [cite: 4, 5, 6]. 
*   **New Earning Avenues:** Standard Chartered’s partnership with RentSmart introduces a lucrative, yet time-limited (until April 2026), avenue for earning miles on rental deposits and payments, which represents a critical addition to the engine [cite: 7, 8, 9].

### Introduction & Methodological Overview
The optimization of credit card rewards in the Hong Kong financial ecosystem is a highly complex, multi-variable problem. Banks frequently obfuscate their true earn rates behind convoluted terms and conditions, temporary promotional caps, and archaic Merchant Category Code (MCC) classifications. This comprehensive academic report serves as a Delta Analysis for your existing Python calculation engine. It evaluates the current state of four targeted credit cards—the Standard Chartered Cathay Mastercard, HSBC EveryMile VISA, HSBC Red Mastercard, and HSBC VISA Signature—against the latest 2026 banking terms, promotional schedules, and loyalty program structures. 

While every effort has been made to verify data points against primary banking documentation, the dynamic nature of credit card promotions means some elements (such as exact expiration dates of unannounced future phases) remain subject to institutional alteration. Due to system constraints, while an exhaustively detailed analysis is provided herein, it is condensed into the most critical updates required for your Python engine architecture.

---

### 🔄 RATE CHANGES (vs current engine)

A rigorous audit of the current Python engine against the latest 2026 banking literature reveals several critical rate adjustments and logic corrections that must be implemented.

| Card | Category | Old Rate | New Rate | Source |
|------|----------|----------|----------|--------|
| **HSBC EveryMile VISA** | `Overseas (Physical)` | HK$2=1mi (Cap: HK$15,000) | **HK$2=1mi (Threshold: HK$12,000)** | [cite: 1] |
| **HSBC EveryMile VISA** | `Travel Booking (Designated OTA)` | HK$2=1mi (Agoda unlisted) | **HK$2=1mi + 15% discount + 'Pay with RC' boost** | [cite: 10] |
| **Standard Chartered Cathay** | `Other Airlines (Direct Booking)` | HK$4=1mi (General) | **HK$4=1mi + Promo Thresholds** | [cite: 11] |

**Analytical Context for Rate Changes:**
1.  **HSBC EveryMile Overseas Threshold:** The current engine logic assumes a hard cap of HK$15,000 for the HK$2=1mi overseas promotion. However, the latest 2026 Phase 1 (Jan-Mar) and Phase 2 (Apr-Jun) terms explicitly state that the offer is triggered by a *minimum* Net Spending Amount of HK$12,000 [cite: 1]. If the engine strictly caps earning at 15,000 without validating the 12,000 floor properly in the current promotional terms, users spending HK$11,999 will receive an inaccurately high miles projection.
2.  **Agoda & EveryMile Synergy:** Agoda has been aggressively integrated into the EveryMile ecosystem for 2026. Aside from the base HK$2=1mi rate, users receive a 15% flat discount on designated hotels and exclusive access to 30% monthly flash sales [cite: 10]. Furthermore, using RewardCash to offset Agoda bookings yields a preferential redemption rate of $1 RC = HK$1.25 [cite: 10]. 

---

### ➕ MISSING CATEGORIES TO ADD

To ensure the engine encompasses the full spectrum of modern consumer spending in Hong Kong, several high-expenditure categories must be integrated. These categories are subject to strict banking regulations and often fall outside standard reward structures.

| Card | Category | Rate (HKD/Mile) | Cap | Notes |
|------|----------|------------------|-----|-------|
| **All Cards** | `Hospital / Medical (Physical)` | Varies by Card | None | Generally earns base rate (e.g., 0.4% RC for HSBC). Excluded from bonus tiers [cite: 12, 13]. |
| **All Cards** | `Education Fees` | Varies by Card | None | Often strictly excluded if paid via online banking. Earns base rate if swiped physically [cite: 14]. |
| **Standard Chartered Cathay** | `Rent Payments (RentSmart)` | HK$6=1mi | None | SC Cathay promo offers HK$6=1mi. 1.5% fee waived up to HK$150k until Apr 2026 [cite: 7, 9]. |
| **All HSBC Cards** | `Foreign Currency (Online - CBF)` | Base Rate | None | Online merchants (e.g., Uber, Netflix) processing overseas in HKD incur a 1.95% Cross Border Fee (CBF) [cite: 5, 15]. |

**Contextual Analysis:**
*   **Hospital, Medical, and Education:** These sectors are traditionally heavily restricted by Hong Kong card issuers. While specific health care promotions exist (e.g., discounted health checks [cite: 12, 13, 16]), paying standard hospital bills or tuition fees via digital banking portals (like HSBC Internet Banking bill pay) typically yields zero miles. The engine must differentiate between physical POS swipes at a clinic (which earn base miles) and online bill payments.
*   **Cross-Border Fees (CBF) / Dynamic Currency Conversion (DCC):** Transactions made in HKD but routed through overseas payment gateways (like Uber routing through the Netherlands) incur a 1.95% fee on HSBC and most other local cards [cite: 5, 15]. The engine should technically calculate this as an effective *reduction* in the value of the miles earned, as the user is paying a premium for the transaction.

---

### 🚫 EXCLUSIONS (Zero-earn categories)

The banking sector in Hong Kong has progressively tightened loopholes surrounding passive or synthetic spending. The engine must explicitly route the following transaction types to a `rate = 0.0` output.

| Card | Excluded Transaction Type | Details |
|------|---------------------------|---------|
| **All HSBC Cards** | E-Wallets (PayMe, AlipayHK, WeChat Pay) | Completely nerfed. No RewardCash awarded for top-ups [cite: 17, 18]. |
| **All HSBC Cards** | Online Bill Payments (Taxes, Utilities, Education) | Payments made through HSBC Online/Mobile Banking to the Inland Revenue Department, water/electricity boards, or educational institutions yield 0 RewardCash unless a specific promotional campaign is active [cite: 19, 20]. |
| **SC Cathay Mastercard** | E-Wallets & Insurance | Strictly excluded from earning Asia Miles by Standard Chartered’s general terms and conditions [cite: 11]. |
| **HSBC EveryMile** | Supermarkets | Deliberately excluded from the standard HK$5=1mi rate; heavily penalized to earn a mere 0.4% RC (HK$12.5 = 1 mile) [cite: 21]. |

---

### 📊 SPENDING CAPS & THRESHOLDS (Verified)

A critical function of the calculation engine is accurately blending the effective earn rate when a user exceeds a promotional cap. The following caps have been verified against 2026 documentation.

| Card | Cap/Threshold | Amount | Period | Status |
|------|---------------|--------|--------|--------|
| **HSBC Red** | 4% Online Spend Cap | HK$10,000 | Monthly | Verified. Excess earns 0.4% [cite: 22]. |
| **HSBC Red** | 8% Designated Merchant Cap | HK$1,250 | Monthly | Verified. Excess earns 0.4% [cite: 22]. |
| **HSBC Visa Signature** | Red Hot Rewards (RHR) Cap | HK$100,000 | Annual | Verified. Shared across all 5X bonus categories [cite: 19, 23]. |
| **HSBC EveryMile** | Overseas Promo Threshold | Min HK$12,000 | Phase (Quarterly) | Verified. Must spend HK$12K to trigger the HK$2=1mi tier [cite: 1]. |
| **HSBC Travel Guru** | GO Level Threshold | HK$8,000 | 3 Months | Verified. Max extra rebate: $500 RC [cite: 2, 3]. |
| **HSBC Travel Guru** | GING Level Threshold | HK$30,000 | Annual | Verified. Max extra rebate: $1,200 RC. Requires 3 bookings [cite: 2, 3]. |
| **HSBC Travel Guru** | GURU Level Threshold | HK$70,000 | Annual | Verified. Max extra rebate: $2,200 RC. Requires 6 bookings [cite: 2, 3]. |

---

### 🎯 ACTIVE PROMOTIONS (Current Month)

The following time-sensitive promotions drastically alter the mathematical outputs of your engine and should be integrated as optional toggles or conditional logic blocks.

| Card | Promo Name | Details | Validity |
|------|------------|---------|----------|
| **All HSBC Cards** | HSBC Travel Guru | Tiered loyalty program offering an extra 3%, 4%, or 6% RewardCash on physical overseas spending based on accumulated expenditure and travel bookings [cite: 2, 3]. | Enrolment open to Oct 2025; Promo valid to Dec 31, 2026 [cite: 3]. |
| **SC Cathay** | RentSmart Partnership | HK$6=1 mile on rent/deposits. 1.5% transaction fee waiver for Midland tenants up to HK$100,000, or general users up to HK$150,000 [cite: 7, 8, 9]. | Valid until April 30, 2026 [cite: 7, 9]. |
| **HSBC EveryMile** | Agoda Flash Sales | 15% off worldwide hotels year-round. 30% off monthly flash sales. 'Pay with RC' enhancement to HK$1.25 [cite: 10]. | Valid until Dec 31, 2026 [cite: 10]. |
| **SC Cathay** | Cathay Membership Overhaul | Cathay has eliminated the "points reset" after reaching a higher status tier, allowing up to 50% of excess Status Points to roll over into 2027 [cite: 24, 25]. | Implemented Jan 1, 2026 [cite: 25]. |

---

### 🏷️ MCC INTELLIGENCE

Misclassification of Merchant Category Codes (MCC) is the primary reason users fail to achieve expected miles. The engine's logic must strictly map merchants to the correct banking definitions.

| Merchant/Type | MCC Code | Classification | Which Card Benefits |
|---------------|----------|----------------|---------------------|
| **Uber (Hong Kong)** | `4121` (Taxicabs/Limousines) | Online / Transport | **HSBC Red**: Earns 4% (Online) [cite: 4, 5]. Note: Triggers 1.95% CBF as it bills from the Netherlands [cite: 15]. |
| **Foodpanda / Keeta** | `5814` (Fast Food) / `5499` (Misc Food) | Online / Food Delivery | **HSBC Red**: Earns 4% (Online). **Strictly excluded** from standard "Dining" bonus multipliers (e.g., HSBC Visa Sig Red Hot Dining) [cite: 4, 6]. |
| **Agoda / Trip.com** | `4722` (Travel Agencies) | Online / Travel | **HSBC EveryMile**: Designated merchant. **HSBC Red**: 4% Online. Note: Agoda often triggers overseas CBF depending on the checkout currency and gateway [cite: 10, 26, 27]. |
| **Hospital / Clinics** | `8062` (Hospitals) / `8011` (Doctors) | Medical / Services | Base rate only. Excluded from all premium lifestyle, dining, and online bonus tiers [cite: 12, 13]. |

**Deep-Dive on Uber & CBF:** 
It is a common misconception that Uber HK is a standard local transaction. Because Uber does not maintain a local acquiring bank in Hong Kong, transactions are routed through the Netherlands. Consequently, despite being billed in HKD, cards like HSBC Visa Signature and HSBC Red will levy a 1.95% Dynamic Currency Conversion (DCC) or Cross-Border Fee (CBF) [cite: 5, 15]. While the HSBC Red Card successfully categorizes Uber as an online transaction (yielding 4% RC), the net yield is reduced by the 1.95% fee.

---

### 📝 RULES FOR CALCULATION ENGINE

To update your Python source code to reflect the reality of March 2026, the following logic updates must be implemented.

**1. Update `CATEGORIES` List:**
```python
    # Add to the existing CATEGORIES array:
    "Education / Hospital (Physical)",      # Base rate
    "Education / Hospital (Online)",        # Zero rate / excluded
```

**2. Standard Chartered Cathay Mastercard Updates:**
```python
        # Update exclusions to explicitly capture Online Bill Pay for Medical/Education
        if category in ["E-Wallets (PayMe/Alipay/WeChat)", "Insurance / Utilities / Tax", "Education / Hospital (Online)"]:
            rate = 0.0
            notes = "Excluded: Strictly excluded from earning Asia Miles by standard banking terms."
            miles = 0.0
        # Incorporate physical medical/education into base rate
        elif category == "Education / Hospital (Physical)":
            rate = 6.0
            notes = "Physical swiping at hospitals/schools earns the base local rate of HK$6=1 mile."
```

**3. HSBC EveryMile VISA Updates:**
```python
        # Update Travel Booking logic to highlight Agoda synergy
        elif category in ["Travel Booking (Designated OTA)", "EveryMile Designated Everyday"]:
            rate = 2.0
            notes = "EveryMile designated merchant (Klook/KKday/Agoda): HK$2=1 mile. Agoda offers 15% off + 30% flash sales + HK$1.25 RC offset."
        
        # Correct the Overseas Threshold Logic
        elif category == "Overseas (Physical)":
            # 2026 Promo requires HK$12K minimum threshold
            if amount >= 12000:
                # Assuming no hard upper cap is explicitly applied in the snippet for phase 1/2, 
                # but retaining the 15k limit if it applies to an overall account limit.
                if amount <= 15000:
                    rate = 2.0
                    notes = "Overseas (Physical) promo: HK$2=1mi (Threshold of HK$12K met)."
                else:
                    base_miles = 15000 / 2.0
                    excess_miles = (amount - 15000) / 5.0 
                    miles = base_miles + excess_miles
                    rate = amount / miles 
                    notes = f"WARNING: First HK$15K earns HK$2=1mi, excess HK${amount-15000:.2f} earns base HK$5=1mi. (Blended rate: HK${rate:.2f}=1mi)."
            else:
                rate = 5.0
                notes = "Overseas (Physical) fails to meet the HK$12K Phase Promo threshold. Earns base HK$5=1mi."
            
            # Add Travel Guru Context
            notes += " *Travel Guru (Tier 3) yields up to +6% RC for physical overseas spend.*"
```

**4. HSBC Red Mastercard Updates:**
```python
        # Ensure Food Delivery and Ride-Hailing note the CBF issues
        elif category in ["Online General", "Food Delivery", "Travel Booking (Non-Designated OTA)", "Travel Booking (Designated OTA)", "Ride-Hailing (Uber/Taxi Apps)"]:
            if amount <= 10000:
                rate = 2.5
                notes = "4% online rebate applied (HK$2.5=1mi)."
            else:
                base_miles = 10000 / 2.5
                excess_miles = (amount - 10000) / 25.0
                miles = base_miles + excess_miles
                rate = amount / miles
                notes = f"WARNING: 4% cap (HK$10K) exceeded. First HK$10,000 earns HK$2.5=1mi, excess earns 0.4%."
            
            # Specific MCC Warning
            if category == "Ride-Hailing (Uber/Taxi Apps)":
                notes += " WARNING: Uber routes through the Netherlands; expect a 1.95% Cross-Border Fee (CBF)."
            if category == "Food Delivery":
                notes += " (Verified MCC 5814/5499: Triggers Online 4%, but strictly excluded from standard Dining promos)."
```

**5. HSBC VISA Signature Updates:**
```python
        # Add Red Hot Rewards note regarding shared limits and new categories
        elif category in ["Overseas", "Overseas (Physical)", "Overseas (Online)"]:
            rate = 6.25 
            notes = "Overseas spending earns 1.6% Red Hot Rewards (HK$6.25=1mi) IF selected as your 5X category. *Assumes user has not exceeded HK$100K annual shared category cap.*"
            notes += " *Stacking with Travel Guru GURU tier adds up to 6% RC.*"
```

**Sources:**
1. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEM1lxNmW9TFh7stqBo1ATLAm9qYRYTelWMrXZU4VlNbsRNWIFfsjqh73agV7buBJaKpPwjKCLS1SWNjxzr6_MQmg5Hg_OAyThCUfxDInoonmjljTEOzYM0k9soMF0YX9CXA31qYCFbirpGA0h06O-dHc1wm-I7XXz3IrrVtrNvASPRExR)
2. [mrmiles.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkvZpHHZL7JLKLOgAVmCl1O3D63jyc60O3n-SvUCpXmLAQyC1mmrrGw02b0KorZ-Ek5dS26C4cCU2DRgSDZAPNrGdCSOeRNhyw52GYpsQBAJYyXinxZZRatbLc7_36)
3. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPN9XMtwmAGPb5peM_1ai7VpBd6RVxKhfipWsw-vzF35xcbDjcYCG_-Q8ypBWZhinSQmIl9TZWGYK0XUT_IoUKd05Ft8ggw5JMxY-NCaDYCdMG8CgfVVxMtA6hnXJdxTH55WfYX3jneB_hWc7ScQBb3l3LZWQoLTljMDPNy85vGI4F1LsB-Rys20yrikMfycg9Xi9_K1M=)
4. [jetsofind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbq1jqTZXqMzTQWPgaVmBIAqs2uuCZ_qhbcsjTxDZE63YlG6Bk8_lCZcMJSgFJ-MKCEh2Uc2k04eAzuftBaXWQsR9fE5D4wz2in7dm-ckF8wg5wK9rstFePX8OpGpI0axm6tKWgabjryyJESNJUC3WiZm77A==)
5. [rupenjshah.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcL8_gUpqm_ScJyeuOHtl6AmL9lPdOq_Or831kIK1PtRiMxFeVQf5OZGs9k2RJo_ukhoCprSclXXvZksC63hVw4u0LoFS3wLjKfUAJCDMjzI7RELT6R05yXZJkG0_KoVC70ORP9PrrLSS1w45qwQ8zBty8Y_9cPQRHKiwbk9vha9cM5mq3XQ==)
6. [heymax.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6W4YcfDkqsC_g32crSx7D4GIIvz7sxvFR97dT6XRSswGss5NplNesddEDjs6gDv_lGjd6o8aJUP7VbvuApFZrhxqbnLCs_IhXifR1Uh1C18pngC0GJrUGn-BSUhumSvsceeBRqfC8Ev9KNL1HHKf3BHirZpPmtBYiVCo=)
7. [rentsmart.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHG70F1ML06LM1F5WFrBJC5ryyFBSpSpZQF8jRzO8aHBPiZ5NYjZoAtpdQnpCeEdRsA24xKO9ZQNX5FwUMzjsUA-SRjN3ZgiCCJI76KOBcH6t8yXc7sFyvi5Vcmt_BWCErghse6m9bN2S2FFPGCLgIkcUhgloqoz7k=)
8. [rentsmart.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2LG0W1AK0fny8wcO9Y3DrZbepZYAtLdEoQicigfx1mXHFUnjLLbRCDK-mVnul-yE9kgENRfyhWWIo7vqObxXRY_BiXyshc_bvfNQd1PAGPfB_r2rjc_PIMFK8K-NEJx2-IXQTSKJF9bYtPZ4NVy6P0rToXKV9bg==)
9. [rentsmart.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIIrTyU5X69JrYekW8M8Ns3LImtIy0oJsAO3s33_bHGnnAvoDIaElQo1prJ9WjaUfRvnGDsrdobbab6_vbHo7bUShQPQR39mQh0xScz-RTwvdhr2QrCmHn6k6r1KXJuxEW3fjyNgqt-Tu4pCMAc1SZUjZ8)
10. [agoda.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJFBMzgQ9kDH0LoCBmbfK5zsq-Iujj8rsshH6MikMKH_0NTHiIwHdHczlLXwmd-ZILiEcPelWuy3xOpMjixKX6i6L_t8pnvXALToQ01Xgn3xfJr0hjWRCpSWro-WeYxQ==)
11. [sc.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEp9eC66iZZJkpCwRuYNeDxR59pqOpLQD_6x1WRkfBJcyqGFixWNI8vbkABksYqu9BNpTkUBFWKtmuAOv81mJiYHYE2Xla5gOcjnzUn1bRvNcdY7wyM58r8RVFWHnIIDlavtNaQ_G7XPtx3YtklYTesv39IUIYDMgZnePDH4HRIZx0cSUIieZ8=)
12. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGc169Vgy7qFlCJ8FWQphzNGowBOLa8O_CNJPs1Vz5ZOACLCvnYZRIhx34y132YDEggNuL7pM58jfRlvaJNSKaiwtHhnDMSuIEUb7ftvanbjsQA4CMD7vO9lHvnBn-w8PIrZs3HJdk2nu-6RQDlQIDnEwTanHrtkMwxwXYT5jYCYX8s8uGrzEarZVGbLyh8v0hQ_gDKZQNJmAc2X8e8xBGfS5xC)
13. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFi7hi-oKj6TsW5KKe9VvGnBfuvlyWOtd_mzwpmcMuQ5Tax2txJgkAoZ7iIn0wzFDMmh8MQSdKlZhXbJT3lcSKY8nEdlNn13BLrNBxGSZD0_cBwNsP_PzolqojPmXKkMGVLAOpP6RJqr75NE2kzTKhUlmMQVj2lD_2k13x2IjHMMdI14dk8Y8NQLeUAWKUVCcYrwI_0vFPXxYePJyuMJLOf6KcRsQ==)
14. [suitesmile.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzBY_xmMgcaDX_dWb7gcfYvnfVP9j7g39j0D4-cJGJj0y5q9Wc5rErrGvWjzfq3sy5Pjx8dem3Kp3PQU78jL_JRTF73wr22ByhcP-ocf3k46B7G3hmHGEEYnadGEUTJnp76GIkv7V1Nqd3HpkY3nV9n7L0MBg_PT0=)
15. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0yryYF1A9UGWLUIKsc-STof7xITafIK8gBVyHE58Y3FFV5BiYWXcmlldfghzIaYeSWFo9iNPPm_qVszy3U5UduCdQitpSFjfMwDnx40VJvULk5uvaKAVyNwasT-jALSOnA0UrZidl8ivabngxJSthhnuZmhuEOWmmvpls9ClxDM_uCMIrz8otWquE2G8=)
16. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbMW6h1A4eMb_3k_8fwf3Xi0ad9QbbRfRJvFPI85FMuxm0-3e9QsX_C4XU58rI_lXKXe80qXi3AqW7kksg_W1obj1HTCR_-z-wH8R__iXRwMk8szli-g8nUrKQhmgiLIvOhXMCa1iTbN2JR92LMvUOJFe6BSLZFnG6w6jR--GDwj00n2a3o3kiqwuqqi8vJ3ScKdX0vL70RA7ZIotEBVJI5TYFqQ8=)
17. [moneyhero.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtu3DiqQ2wFIrLxzIwFiPm5qqbLNN_xxKLHvaJbivhEFo3hKSdcexiGIqKo3ClkQY18vJkFoRAhavltG8JUfTXUoguJhjZKoJc3RtLKj-qQVl1ykWHGFl5ASpDAluuJk6lbtgR2A==)
18. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHC8V3_KkAxQ6Fch1hvOuSuM85VlYcw2OyRU86EMjp4B8FHkl_CRbE7xsaQJFvB1Y_lk93Y-YllMdQWLJE4F4Zdc2jZD70W4gL58P_Iik-dGW0ROKyWIc8i9tRRnPIs0MsOfkbPfRYYQg_qcPo=)
19. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwxZHo69g5u0nCW0HNjFgOvDszLov5ej7pGaEhCWIeqdW4fGTHDsqekMrr9lrhlYiTUMFQ5p10D5j0nk7-jOHKUtH7yDw3jb8EZ4HUSgGslOFizEKeOyw1j8_iUV53ZaWmkvdxn1mGu2edgXvoKT1JNKa-x70EYfv_bselNUWPVFub)
20. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEeD0dVN81uzNf_aVlvMS8soa2Eiud0BLV9nFFRp17Vg35KiqfZ_WaM0y3YUsYwKDgEzILOIknAJ_2gY_f3bbuwh5EpNMlaCe4E1bXcoaip9fXUrieoMivzl41JVS7wmuMhz9bCloGH9FWa4_8jvM=)
21. [jetsofind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4HSRpcGQRiA_rr_ZkhnuaUP_CwIOAxEslYEzDTk8OCPM0jlQYhPWmKczcXCdfuI3MckoqGaFo3nJ0e9o2rCF1fY8atOonTx0uE1ZX1PYIsudjTn3GwBHAtg0FzyR5cr_y83G4P0ls7sen07pgySzBvMFWWCzFvR9UM-I=)
22. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOb6iGO7M2BJag8j7yS4LQpUu-gT1QpA71AD8XrtUK0TOJd3g6Ph6P56t8rBzMhjwUrm1KMqlY_Sx0EVSuwMqjsBcRXUvcVK1bs0LBTDznDbJKqKsw4CKrufzHvfq9TzsiEVWwiqH8IQ==)
23. [moneysmart.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjnotL9wce0mCkqbihaWH87WICYGtBF4rIaoBuil7Wz4ckZnZW2bddh8Yylwmzolc5tDGsNCatXIaHH0o_YIh75YThLPOkaPat3iJnBaVCXl-Ki7EFUejIluJ6_fSXN5iSXHlKYsSnumSUPg==)
24. [thealviator.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiN_uPOsbAxWfkYqfqPzc3504aM67WbdcEH-m1Tab1kAN0lrjUqlNMcx01ANp0Gi1_oMkz0K_Pl5mRCGNUqETQDRWM1ttIztEM7M08LvmeeHiBEOTWzKwwiBJZRCwkwozIv8peLSkHzdWi-ZuRx_7nVTmVVA==)
25. [cathaypacific.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrOHc5avE7XMiBWEOn9OwwX8qGXOCWyGmfxIP3tqUDJjXioLEHQCuOhUHmjczciXtLjeForYthkdTG77ZUfo4keYJfqwga6qHBTr32GdUfpxHPop4OMF8jDMvENl92BT0fAgs6hlpBxyDfRHOznx5FUKSLPDkHS3KhryFX25yw-pif4qWXfRdM4ntdbKkPImhqOYQc_1tlDU0igelMs4-oxWGIOOtlZ_4xqH-4Wry7YNsYu32WmLarcLBHSk0yhXh3VW_YDG1TgA==)
26. [mrmiles.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSMR4aSvzr0zFX_1aOelYoVGhdIQCsxEhHU_buZxvS2t8Vsg5v0-B3Vw-GHh3Ju6x3MpSuUyYcL925C3H2IQckNbG8X85YOpvIb9I-4odnXUzB1vvFYZQ=)
27. [mainlymiles.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXCl0AxTa_-z1It81ROcZeGsTXtZtwwprg1DAFXTjSJKtVioUUMF6bfchKoVIXfNTAbWqcSc4wJzptHSh7oDf5wSlKDQBUbUr4eihXz_6zrPvIAugIOy7Wj6jV340ZyANkBy3xsI0eEVuOF_Yj6qSzvnRpG8ChKy2Uri_k5-vfYr7SBfoOWm7at3NnyUaCgJbrbppuPG8pnE7m)
