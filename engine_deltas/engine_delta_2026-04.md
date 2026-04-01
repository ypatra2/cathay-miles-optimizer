# Cathay Miles Engine — Deep Research Delta Report
## Date: Current 2025/2026 Analytical Review

### Executive Summary & Leading Paragraph
The landscape of Hong Kong credit card rewards has undergone a paradigm shift moving into 2025 and 2026, characterized by aggressive targeted spend bonuses coupled with sweeping exclusions on low-margin transactions. This report serves as a definitive **Delta Analysis** of the current Python-based Cathay (Asia) Miles optimization engine. 

**Key Findings:**
*   **The War on Arbitrage and Low-Margin Spend:** Standard Chartered has drastically expanded its zero-earn exclusion list, entirely eliminating miles generation for Hospital, Education, and Utility payments effective September 2024 [cite: 1, 2]. Concurrently, HSBC is terminating all RewardCash earning on PayMe top-ups across its entire portfolio effective July 1, 2025 [cite: 3, 4].
*   **Correction of Standard Chartered Online Rates:** The current engine erroneously assumes all online general retail and ride-hailing (Uber) earns the accelerated HK$4/mile rate on the SC Cathay Mastercard. Official terms confirm that only Online Dining/Food Delivery, Hotels, and Overseas spend trigger the HK$4/mile tier, while general local online spend (including OTA non-hotel bookings and Uber) falls to the base HK$6/mile rate [cite: 5, 6].
*   **The Uber x Cathay Symbiosis:** A new, card-agnostic partnership directly awards 20 to 40 Asia Miles per Uber ride simply by linking the user's Cathay and Uber accounts [cite: 7, 8]. The calculation engine must decouple this bonus from the HSBC Red card and apply it universally to the Ride-Hailing category.
*   **Travel Guru Complexity:** HSBC's multi-tiered Travel Guru program fundamentally alters the mathematics of overseas spending. The highest tier (GURU) pushes the effective earn rate on the EveryMile card to an unprecedented 8.5% RewardCash (HK$0.59/mile) for *physical* overseas spend, while strictly excluding online foreign currency transactions [cite: 9, 10]. 

This comprehensive academic and technical report delineates the exact modifications required to bring the current calculation engine into absolute alignment with current banking regulations, promotional caps, and Merchant Category Code (MCC) intelligence.

---

### 🔄 1. RATE CHANGES & CORRECTIONS (vs. Current Engine State)

A meticulous audit of the provided Python calculation engine against the latest bank terms and conditions reveals several critical inaccuracies in how earn rates are currently modeled. The following table isolates the specific rates that must be corrected.

| Card | Category | Old Rate | New Rate | Source / Rationale |
|------|----------|----------|----------|--------------------|
| **Standard Chartered Cathay** | `Online General` | HK$4/mi | **HK$6/mi** | Engine incorrectly assumes all online spend is HK$4/mi. SCB terms explicitly state HK$6=1mi for online categories posted in HKD, reserving HK$4=1mi strictly for dining, food delivery, hotels, and overseas [cite: 5, 6]. |
| **Standard Chartered Cathay** | `Travel Booking (Non-Designated OTA)` | HK$4/mi | **HK$6/mi** | Unless the OTA transaction specifically triggers the "Hotel" MCC or is processed in a foreign currency, standard flight or package bookings via OTAs in HKD earn the base HK$6/mi rate [cite: 6]. |
| **Standard Chartered Cathay** | `Ride-Hailing (Uber/Taxi Apps)` | HK$4/mi | **HK$6/mi** | Ride-hailing is processed as local HKD online retail. It does not qualify as "Dining" or "Overseas", thus reverting to the base HK$6=1mi rate [cite: 6]. |
| **Standard Chartered Cathay** | `Insurance / Utilities / Tax` | 0.0 (Excluded) | **0.0 (Verified)** | Verified as correct. Note that Utilities (MCC 4900) were formally added to the total exclusion list on Sept 3, 2024 [cite: 1, 2]. |
| **HSBC Red Mastercard** | `Shopping (Designated 8%)` | HK$1.25/mi | **HK$1.25/mi** | Verified as correct. The monthly cap is indeed HK$1,250 in *spend* to max out the HK$100 RewardCash cap for this category [cite: 11, 12]. |
| **HSBC Red Mastercard** | `Online General` | HK$2.5/mi | **HK$2.5/mi** | Verified as correct. The monthly spend cap of HK$10,000 for the 4% rebate remains active [cite: 11, 13]. |
| **HSBC Visa Signature** | `Dining (Premium/Casual)` | HK$2.78/mi | **HK$2.78/mi** | Verified. Assumes allocation of all Red Hot Rewards multipliers to the "Dining" category, yielding 3.6% RC [cite: 12, 14]. |

**Deep Dive on Standard Chartered Corrections:**
The current engine state features a substantial flaw in its handling of the Standard Chartered Cathay Mastercard. The code currently reads:
```python
elif category in ["Online General", "Food Delivery", "Travel Booking (Non-Designated OTA)", "Travel Booking (Designated OTA)", "Ride-Hailing (Uber/Taxi Apps)"]:
    rate = 4.0
```
This is mathematically and procedurally incorrect based on the latest SCB product literature. The accelerated HK$4 = 1 Asia Mile rate is highly restrictive. It applies exclusively to eligible spending in foreign currencies (Overseas), Dining, Food Delivery Platforms, and Hotels [cite: 5, 6]. General e-commerce (such as Amazon or HKTVmall), ride-hailing applications (Uber HK), and non-hotel OTA bookings processed in Hong Kong Dollars are unequivocally classified under the base rate of HK$6 = 1 Asia Mile [cite: 6]. The engine must be updated to decouple "Food Delivery" (which remains at HK$4) from the other online categories (which must drop to HK$6).

---

### ➕ 2. MISSING CATEGORIES TO ADD

The current `CATEGORIES` array in the Python engine is insufficient for modern credit card optimization. It fails to account for massive household expenditures that are subject to unique, highly restrictive earn rates. The engine must be expanded to include the following distinct categories.

| Card | Category to Add | Rate (HKD/Mile) | Cap | Notes |
|------|-----------------|------------------|-----|-------|
| **All Cards** | `Hospital / Medical` | Varies | N/A | SCB explicitly excludes MCC 8062 (Hospitals) and 5047 (Medical Equipment) as of Sept 2024 (Zero earn) [cite: 1, 2]. HSBC cards earn base 0.4% (HK$25/mi or HK$12.5/mi for EveryMile) [cite: 15, 16]. |
| **All Cards** | `Education Fees` | Varies | N/A | SCB explicitly excludes MCC 8211, 8220, 8241, 8244, 8249, 8299 (Schools and Universities) as of Sept 2024 (Zero earn) [cite: 2]. HSBC cards earn base 0.4% [cite: 15, 16]. |
| **All Cards** | `Utilities (Direct)` | Varies | N/A | MCC 4900 (Electric, Gas, Water) is totally excluded by SCB (Zero earn) [cite: 1, 2]. HSBC earns base 0.4% [cite: 15, 16]. |
| **All Cards** | `Rent (via RentSmart/CardUp)` | Varies | N/A | SCB offers a dedicated HK$6=1mi rate for rent paid via RentSmart [cite: 5]. |
| **All Cards** | `Overseas (Physical In-Store)` | Varies | Varies | Must be separated from `Overseas (Online)` to accurately model HSBC's Travel Guru program, which strictly excludes online foreign currency spend [cite: 10, 17]. |
| **All Cards** | `Overseas (Online)` | Varies | N/A | Excluded from HSBC Travel Guru bonuses [cite: 10, 17]. Red Card earns 4% (HK$2.5/mi) up to HK$10k cap [cite: 11, 13]. |

**Architectural Rationale for Category Expansion:**
1.  **The Great Medical and Educational Purge:** Historically, analysts grouped "Insurance, Utilities, and Tax" into a single low-earn category. However, Standard Chartered's sweeping devaluation in September 2024 necessitates the creation of dedicated `Hospital / Medical` and `Education Fees` categories. Transactions under MCCs 8062 (Hospitals), 5047 (Medical Supplies), and 8211/8220 (Schools/Universities) now yield exactly zero miles on the SC Cathay Mastercard [cite: 1, 2, 18]. Conversely, HSBC continues to award base RewardCash (0.4%) for these exact same MCCs [cite: 15, 16]. If the engine groups these into "Other Local Spending", it will falsely promise SCB users HK$6/mile on massive hospital bills.
2.  **The Physical vs. Online Overseas Schism:** The engine currently has a monolithic `Overseas` category. This is fatal to accurate modeling in 2026. HSBC's flagship "Travel Guru" program (which offers up to 6% extra RewardCash) amended its terms to strictly mandate *physical, in-store overseas spending*. Online foreign currency transactions are excluded from this massive multiplier [cite: 10, 17]. Therefore, an accurate engine *must* ask the user whether their foreign currency spend is physical or online.

---

### 🚫 3. EXCLUSIONS (Zero-Earn Categories)

Banks have grown increasingly hostile to transactions that generate low interchange fees or facilitate closed-loop cash recycling. The following exclusions must be hard-coded into the engine returning a `0.0` rate.

| Card | Excluded Transaction Type | Details & Effective Dates |
|------|---------------------------|---------------------------|
| **All HSBC Cards** | `E-Wallets (PayMe)` | **CRITICAL UPDATE:** Effective July 1, 2025, HSBC will entirely remove PayMe reload spending from earning RewardCash across all its credit cards (including Visa Signature, Red, and EveryMile) [cite: 3, 4]. AlipayHK and WeChat Pay were already excluded or heavily nerfed. |
| **SC Cathay Mastercard** | `Hospital / Medical` | Effective September 3, 2024, MCC 8062 (Hospitals) and MCC 5047 (Medical/Dental/Ophthalmic Equipment) generate 0 miles [cite: 1, 2]. |
| **SC Cathay Mastercard** | `Utilities (Direct)` | Effective September 3, 2024, MCC 4900 (Electric, Gas, Water) generates 0 miles [cite: 1, 2]. |
| **SC Cathay Mastercard** | `Education Fees` | Effective September 3, 2024, MCCs 8211, 8220, 8241, 8244, 8249, 8299 (Colleges, Universities, Professional Schools) generate 0 miles [cite: 2]. |
| **SC Cathay Mastercard** | `E-Wallets / Stored Value` | Strictly excluded. Explicitly blocks Alipay, WeChat Pay, PayMe, Tap&Go, and Octopus mobile top-ups (excluding designated AAVS) [cite: 19, 20]. |

**Contextualizing the Exclusions:**
The July 2025 PayMe devaluation is a watershed moment in Hong Kong credit card optimization. For years, users utilized HSBC cards to top up PayMe, effectively manufacturing free RewardCash (up to 0.4% base rate). By closing this loophole [cite: 3, 4], HSBC aligns itself with the broader industry trend of cracking down on quasi-cash transactions. In the engine, the `E-Wallets` category for all HSBC cards must explicitly return 0 miles.
Similarly, Standard Chartered's September 2024 purge of MCCs 4900, 8062, and 8220 reflects a systemic refusal to subsidize rewards on transactions where the merchant acquirer (hospitals, governments, utility monopolies) dictates near-zero interchange fees to the issuing bank [cite: 1, 2]. 

---

### 📊 4. SPENDING CAPS & THRESHOLDS (Verified)

To prevent the engine from outputting mathematically impossible mile yields for high-net-worth spenders, the strict enforcement of spending caps is paramount.

| Card | Cap/Threshold | Amount | Period | Status & Engine Implementation |
|------|---------------|--------|--------|--------------------------------|
| **HSBC Red** | 4% Online Cap | HK$10,000 | Monthly | **Verified.** First HK$10k earns 4% (HK$2.5/mi). Excess reverts to 0.4% (HK$25/mi) [cite: 11, 13]. The engine's blended rate logic is mathematically sound. |
| **HSBC Red** | 8% Designated Cap | HK$1,250 | Monthly | **Verified.** First HK$1,250 spent at designated merchants (e.g., Sushiro, GU, Decathlon) earns 8% (HK$1.25/mi). Excess earns 0.4% [cite: 11, 12]. |
| **HSBC Visa Signature** | 5X Red Hot Rewards Cap | HK$100,000 | Annual | **Verified.** The extra 5X multiplier (yielding 3.6% total) applies only to the first HK$100,000 spent annually in the chosen category (e.g., Dining) [cite: 12, 14, 21]. Engine currently handles this via a text note, which is acceptable, but a warning flag should be triggered if single inputs exceed this. |
| **HSBC EveryMile** | Overseas Promos | HK$12,000 | Period (e.g., Jan-Mar) | **Verified.** To achieve the advertised HK$2=1mi overseas rate, the user must accumulate a minimum of HK$12,000 in eligible overseas spend during the promotional phase (e.g., Phase 1: Jan-Mar 2026) [cite: 22]. If the user fails to hit this threshold, the rate remains at the base HK$5=1mi. |

**Mathematical Modeling Note:** 
The engine's current implementation for the HSBC Red card caps is excellent:
```python
base_miles = 10000 / 2.5
excess_miles = (amount - 10000) / 25.0
```
This elegantly computes a blended effective rate for the user. However, for the HSBC EveryMile overseas promo, the logic is binary, not blended. If the user spends HK$11,999, the entire amount earns HK$5/mile. If the user spends HK$12,000, the *entire* amount triggers the bonus up to the promotional maximum [cite: 22]. 

---

### 🎯 5. ACTIVE PROMOTIONS (Current Month & 2026 Outlook)

Promotions dramatically alter the baseline math of credit card miles. The engine must account for these, either via direct rate adjustments or highly visible user notes.

| Card | Promo Name | Details & Mechanics | Validity |
|------|------------|---------------------|----------|
| **ALL CARDS** | Uber x Cathay Partnership | Card-agnostic direct miles earning. Earn **+20 Asia Miles** per standard Uber ride in HK, and **+40 Asia Miles** for trips to/from HKIA. First-time linkage bonus of 500 miles [cite: 7, 8, 23]. | Ongoing |
| **HSBC (All)** | Travel Guru (Phase 3) | A tiered membership offering up to **6% extra RewardCash** on overseas physical spend. <br>• **GO Level:** +3% RC (Max $500 RC/mo). <br>• **GING Level:** +4% RC (Max $1,200 RC/mo). <br>• **GURU Level:** +6% RC (Max $2,200 RC/mo) [cite: 10, 17]. | Promos run through Dec 31, 2026 |
| **SC Cathay** | RentSmart Promo | First-time service fee waiver and a guaranteed HK$6=1mi for settling rental deposits and advance payments via RentSmart using the SC Cathay card [cite: 5]. | Until April 30, 2026 |

**The Uber x Cathay Paradigm:**
The current engine mistakenly associates the Uber bonus exclusively with the HSBC Red card:
```python
if category == "Ride-Hailing (Uber/Taxi Apps)":
    notes += " +20mi/ride via Cathay partnership!"
```
This is a fundamental misunderstanding of the promotion. The Cathay/Uber partnership functions via account linkage within the Uber app itself [cite: 8, 24]. The user receives these 20-40 miles regardless of whether they pay with an HSBC Red, an SC Cathay, or cash. The calculation engine must append this note to the output of *all* recommendations when the `Ride-Hailing` category is selected. 

**Deconstructing HSBC Travel Guru:**
The Travel Guru program is the most potent, yet complex, overseas spending multiplier in the Hong Kong market for 2025/2026 [cite: 10, 25]. 
*   **The Math:** If a user reaches GURU status, they receive an extra 6% RewardCash on physical foreign currency spend. 
*   **EveryMile Synergy:** Base (1%) + EveryMile Promo (1.5%) + GURU (6%) = **8.5% RewardCash**. Because 1 RC = 20 Miles on the EveryMile card, 8.5% RC equates to an astonishing **HK$0.59 per Asia Mile** [cite: 9, 10].
*   **Visa Signature Synergy:** Base (0.4%) + Red Hot World (2%) + Red Hot Promo (1.2%) + GURU (6%) = **9.6% RewardCash** (HK$1.04/mile) [cite: 10, 26].
*   *Engine Recommendation:* Because achieving GURU requires accumulating HK$70,000 in foreign spend and making 6 flight/hotel bookings [cite: 25, 27], it is highly variable. The engine should explicitly state the base rate in the math, but the `notes` string MUST highlight: *"Travel Guru member? Add +3% to +6% RC on physical overseas spend (up to HK$0.59/mi effective rate on EveryMile)."*

---

### 🏷️ 6. MCC INTELLIGENCE & CLASSIFICATION

Accurate MCC (Merchant Category Code) mapping is the difference between earning a massive bonus and earning a baseline 0.4% penalty rate.

| Merchant/Type | MCC Code | Classification | Which Card Benefits |
|---------------|----------|----------------|---------------------|
| **Uber (HK)** | 3990 / 4121 (Processed Online) | Local Online E-commerce | **HSBC Red:** Earns 4% (HK$2.5/mi) [cite: 11, 13]. <br>**SC Cathay:** Drops to base HK$6/mi (Not classified as dining/hotel/overseas) [cite: 6]. |
| **Foodpanda / Keeta** | 5814 / 5499 | Food Delivery (Online) | **SC Cathay:** Earns HK$4/mi (explicitly included in food delivery platform terms) [cite: 6]. <br>**HSBC Visa Signature:** Foodpanda specifically is whitelisted under HSBC's "Red Hot Happy Days Rewards - Dining" [cite: 28], but Keeta generally falls to base 0.4% unless paid via specific online gateways. <br>**HSBC Red:** 4% online [cite: 11]. |
| **Agoda / Trip.com** | 4722 / 7011 | Travel Agency / Hotel | **HSBC EveryMile:** Agoda is a designated merchant (up to 15% off) [cite: 22]. <br>**SC Cathay:** If billed directly by a hotel (7011), earns HK$4/mi. If billed as general OTA (4722), drops to HK$6/mi unless in foreign currency [cite: 5, 6]. |
| **Public Utilities** | 4900 | Utilities | **SC Cathay:** Excluded (0 miles) [cite: 1, 2]. <br>**HSBC:** Base 0.4% [cite: 15, 16]. |
| **Hospitals** | 8062 | Hospitals | **SC Cathay:** Excluded (0 miles) [cite: 1, 2]. <br>**HSBC:** Base 0.4% [cite: 15]. |

**The Food Delivery Conundrum:**
Foodpanda and Keeta represent a unique challenge. General consumer wisdom assumes food delivery is "Dining". It is not. Merchant acquirers classify these as MCC 5814 (Fast Food) or 5499 (Miscellaneous Food Stores) processed via online e-commerce gateways [cite: 29]. 
*   For the **HSBC Visa Signature** (with Red Hot Dining selected), standard food delivery does *not* trigger the 3.6% dining multiplier. However, HSBC has secured specific promotional partnerships where **Foodpanda** is explicitly named as an eligible merchant under their dining promotions [cite: 28]. 
*   For the **Standard Chartered Cathay**, the terms explicitly carve out an exception, defining "dining/food delivery platform" as eligible for the HK$4/mile tier [cite: 6]. 
*   *Engine Implementation:* The `Food Delivery` category must return HK$4/mi for SC Cathay, HK$2.5/mi for HSBC Red (online), and a heavily caveated base rate for Visa Signature unless it is Foodpanda.

---

### 📝 7. RULES FOR CALCULATION ENGINE (Python Logic Updates)

Based on the exhaustive research above, the following exact logic replacements are required to update the Python engine to its 2026 accurate state.

#### A. Update the `CATEGORIES` List
Replace the existing categories list to accommodate the necessary exclusions and splits:
```python
CATEGORIES = [
    "Cathay Pacific Flights",
    "HK Express Flights",
    "Other Airlines (Direct Booking)",
    "Other Airlines (via OTA)",
    "Travel Booking (Designated OTA)",      
    "Travel Booking (Non-Designated OTA)",  
    "EveryMile Designated Everyday",        
    "Ride-Hailing (Uber/Taxi Apps)",        
    "Cathay Partner Dining",                
    "Dining (Premium)",                     
    "Dining (Casual)",                      
    "Food Delivery",                        
    "Shopping (Designated 8%)",             
    "Online General",                       
    "Shopping (In-Store General)",          
    "Octopus AAVS",
    "Overseas (Physical In-Store)",         # DELTA: Split to handle Travel Guru
    "Overseas (Online)",                    # DELTA: Split to handle Travel Guru
    "Supermarkets",                         
    "Hospital / Medical",                   # DELTA: New exclusion handling
    "Education Fees",                       # DELTA: New exclusion handling
    "Utilities (Direct)",                   # DELTA: Separated from Tax/Insurance
    "Insurance / Tax",                      
    "E-Wallets (PayMe/Alipay/WeChat)",      
    "Rent (via RentSmart/CardUp)"           # DELTA: New category
]
```

#### B. Standard Chartered Cathay Mastercard Logic
*Replace the SC Cathay `if/elif` block with the following:*

```python
    if card == "Standard Chartered Cathay Mastercard":
        # DELTA: E-wallets completely excluded [cite: 19, 20]
        # DELTA: Hospitals, Education, Utilities excluded as of Sep 2024 [cite: 1, 2]
        if category in ["E-Wallets (PayMe/Alipay/WeChat)", "Hospital / Medical", "Education Fees", "Utilities (Direct)"]:
            rate = 0.0
            notes = "Excluded: Strictly excluded from earning Asia Miles by Standard Chartered terms (Sep 2024 update)."
            miles = 0.0
        elif category in ["Cathay Pacific Flights", "HK Express Flights"]:
            rate = 2.0
            notes = "Direct earn HK$2=1mi. +2,667 bonus miles per HK$8K/quarter."
        elif category == "Cathay Partner Dining":
            rate = 2.0
            notes = "Cathay Partner exclusive: HK$4=2 miles."
        # DELTA: Online General and Non-Designated OTA are NOT HK$4/mi. They are HK$6/mi [cite: 6].
        # HK$4/mi is strictly for Dining, Hotels, Overseas, and Food Delivery [cite: 5, 6].
        elif category in ["Dining (Premium)", "Dining (Casual)", "Food Delivery", "Overseas (Physical In-Store)", "Overseas (Online)"]:
            rate = 4.0
            notes = "Eligible Dining, Food Delivery, and Foreign Currency spend earns HK$4=1 mile."
        elif category == "Other Airlines (Direct Booking)":
            rate = 4.0
            notes = "Direct airline booking (MCC 3000-3350) = overseas rate HK$4=1mi (if foreign currency)."
        elif category in ["Octopus AAVS", "Online General", "Travel Booking (Non-Designated OTA)", "Ride-Hailing (Uber/Taxi Apps)", "Supermarkets", "Insurance / Tax", "Rent (via RentSmart/CardUp)"]:
            rate = 6.0
            notes = "Base local HKD rate of HK$6=1 mile. (RentSmart promos also guarantee HK$6/mi)."
        else:
            rate = 6.0
            notes = "Other local spending: HK$6=1 mile."

        miles = amount / rate if rate > 0 else 0
```

#### C. HSBC EveryMile VISA Logic
*Replace the HSBC EveryMile `elif` block with the following:*

```python
    elif card == "HSBC EveryMile VISA":
        # DELTA: PayMe/E-wallets nerfed to zero effective July 1, 2025 [cite: 3, 4]
        if category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            notes = "Excluded: PayMe and e-wallets no longer earn RewardCash effective July 2025."
            miles = 0.0
        # DELTA: Penalized categories earning base 0.4% RC [cite: 15, 16]
        elif category in ["Supermarkets", "Hospital / Medical", "Education Fees", "Utilities (Direct)", "Insurance / Tax"]:
            rate = 12.5
            notes = "MAJOR EXCLUSION: Category earns only base 0.4% RC (HK$12.5=1mi)."
        elif category in ["Travel Booking (Designated OTA)", "EveryMile Designated Everyday"]:
            rate = 2.0
            notes = "EveryMile designated merchant (Agoda, cafes, transport): HK$2=1 mile."
        elif category == "Overseas (Physical In-Store)":
            rate = 2.0
            notes = "Overseas HK$2=1mi IF HK$12K promo threshold met. **TRAVEL GURU BONUS:** Can reach HK$0.59/mi if GURU tier!"
        elif category == "Overseas (Online)":
            rate = 2.0
            notes = "Overseas HK$2=1mi IF HK$12K promo threshold met. (Excluded from Travel Guru physical bonuses)."
        elif category == "Octopus AAVS":
            rate = 12.5
            notes = "AAVS low-earn: 1RC/HK$250 (×20mi) = HK$12.5/mi."
        else:
            rate = 5.0
            notes = "General rate: HK$5=1 mile."

        miles = amount / rate if rate > 0 else 0
```

#### D. HSBC Red Mastercard Logic
*Replace the HSBC Red `elif` block with the following:*

```python
    elif card == "HSBC Red Mastercard":
        if category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            miles = 0.0
            notes = "Excluded: PayMe and e-wallets no longer earn RewardCash effective July 2025."
        elif category in ["Supermarkets", "Hospital / Medical", "Education Fees", "Utilities (Direct)", "Insurance / Tax", "Rent (via RentSmart/CardUp)"]:
            rate = 25.0
            miles = amount / rate
            notes = "Earns 0.4% base rate (HK$25=1mi)."
        elif category == "Shopping (Designated 8%)":
            if amount <= 1250:
                rate = 1.25
                miles = amount / rate
                notes = "8% rebate applied (HK$1.25=1mi) at designated merchants (e.g., Sushiro, GU)."
            else:
                base_miles = 1250 / 1.25
                excess_miles = (amount - 1250) / 25.0
                miles = base_miles + excess_miles
                rate = amount / miles
                notes = f"WARNING: 8% cap (HK$1,250) exceeded. Excess HK${amount-1250:.2f} earns base 0.4%."
        elif category in ["Online General", "Food Delivery", "Travel Booking (Non-Designated OTA)", "Travel Booking (Designated OTA)", "Ride-Hailing (Uber/Taxi Apps)", "Overseas (Online)"]:
            if amount <= 10000:
                rate = 2.5
                miles = amount / rate
                notes = "4% online rebate applied (HK$2.5=1mi)."
            else:
                base_miles = 10000 / 2.5
                excess_miles = (amount - 10000) / 25.0
                miles = base_miles + excess_miles
                rate = amount / miles
                notes = f"WARNING: 4% cap (HK$10K) exceeded. Excess HK${amount-10000:.2f} earns base 0.4%."
        else:
            rate = 25.0
            notes = "Base 0.4% earn rate."
            miles = amount / rate
```

#### E. HSBC Visa Signature Logic & Global Post-Processing
*Replace the HSBC VS `elif` block and append the Universal Uber logic:*

```python
    elif card == "HSBC VISA Signature":
        if category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            miles = 0.0
            notes = "Excluded: PayMe and e-wallets no longer earn RewardCash effective July 2025."
        elif category in ["Supermarkets", "Hospital / Medical", "Education Fees", "Utilities (Direct)", "Insurance / Tax", "Rent (via RentSmart/CardUp)"]:
            rate = 25.0
            miles = amount / rate
            notes = "Non-bonus/bill payment earns 0.4% base rate (HK$25=1mi)."
        elif category in ["Dining (Premium)", "Dining (Casual)", "Cathay Partner Dining", "Food Delivery"]:
            rate = 2.78
            miles = amount / rate
            notes = "3.6% Red Hot Rewards (Dining). Foodpanda qualifies; other delivery apps may default to 0.4%. Cap: HK$100K/yr."
        elif category == "Overseas (Physical In-Store)":
            rate = 6.25  # Assumes user chose Dining for 5X.
            miles = amount / rate
            notes = "1.6% base for non-chosen categories. IF user chose Overseas 5X, rate is HK$2.78/mi (up to 9.6% RC with Travel Guru)."
        elif category == "Octopus AAVS":
            rate = 25.0
            notes = "AAVS low-earn category: base 0.4% = HK$25/mi."
        else:
            rate = 6.25
            notes = "1.6% base for non-5X categories."
            miles = amount / rate

    # DELTA GLOBAL RULE: Universal Uber x Cathay Partnership Addition
    if category == "Ride-Hailing (Uber/Taxi Apps)":
        notes += " [GLOBAL BONUS: Link Cathay app to Uber to earn a direct +20 Miles per ride (+40 for airport), regardless of card used!]"

    return math.floor(miles), round(rate, 2), notes
```

**Final Research Analyst Assessment:**
By injecting these exact Python logic blocks into the current calculation engine, the tool will leapfrog from a generic 2023-era calculator to a highly precise, 2026-compliant optimization engine. It explicitly protects users from the aggressive Sept 2024 SCB exclusions (Hospitals/Utilities/Education) and the looming July 2025 HSBC PayMe exclusions, while accurately modeling the nuance of physical vs. online overseas spend necessary for the HSBC Travel Guru program.

**Sources:**
1. [milelion.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFigDdzV714nojWfG456h8JOYyplYuYVS8o6m_dM3fZMci4Lvq_2huMBDe8BvPkZyew6ky1GiyXvk689uNNIqMi_gxUpD8HiNJKRtJtOcFsmvoETpYhIOS_6vAbche5AGqXfMm4MhE47O63mzIAhyy7Fwt1QjL2Jw3G6zL9-spbBHb0Ken1pjVLl-Nn9MgN8n2jm9MaMkbR4xbwyJPp4N4Mtas=)
2. [mainlymiles.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG17bUW6ivO1ZrywJoNUr2M7IxzP6xbcPopf_9pJlkntutooMdLPGo0q-AnofPzeb6IGgC5jRihPTiWmqFakMIoR11YTJNjUdt7WMsXzOWSIMNNjAMJZJv8YUnk29MinaIy9QmgQycFTx857_I_Sf-OuGNHIQExILPseeZUSs2Nim5sursY3192XrjIUxHrTgdH2cw=)
3. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8MuVfoia6S66vjTHnhXQOIeI2rnNwz-xlDEb8UVldicrLcOmZ7qkTTq9XXV38f8OSDNoIzXBHQpcXqUZyWPEe1V_1R-gGoK96I4YErqnpmDalTBlebIjm71kSu3hJTByknbMyEskR715Kky8=)
4. [flyertalk.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHF7lS9t_aRwuEDQvsRaYuWjP8h56-UbFlWHVyP-BIyqBn-7MGHsjje1_KidMM5mWIt2wCD5E6Iiy3-kptlw7eMe4fn68PoZ0-WjdX94WKj2u15iVG-ftWueZ8Qtaa3B2aIcOqbGudYbw-cOd8f89dv07APifc0s0RLTJ4nBf7UtrnNMdvab9qJXoLzSifhDWpbio5-NYuTtrrSAfRHbnRMcZGp3KNnAa3ZmstHG0lH2piqbMJoHV_iZA==)
5. [sc.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHG8SoTaquUwYLZ3Ba6EUI0vmR24nmwW3odxrMLnmCFcwxG0kxpAahIMQa_hMmYn7peuZ-QLT8vTQwlBuaZeAR4jkDHq8hfQvb2Ow17v88nDAf_zv-Tc_9JGY0SpJBWrdQ=)
6. [cathaypacific.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlmad2Bbd-AI4GPODZBH-51ubJ--pT1yhPv5q9ijyiNAb4KSZgiCwAt5TQFn_t0cYlrHIBt8XDzyYfJpcJjLjRxEAbcmGDbT-FXgWm4vkuJQIsghSIxw4HcY7GHRUOfvMCuDOO0pDzMVXCcVZS-0LDNiSFklCf8A60RIzRjFkkt5U4hA==)
7. [marketing-interactive.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKgLK6pN9XkTs2beMLWcfpIgUY-fXFRNmGc_oQEw77x-jXZ8rNun4LQZjQpV6Kj0kIm5_dzFEInxnkxMOIKXZyvZRtRn_pxXZzwY0UN0ltNCrLSlkUhYVdXkS_Ya6BIOuzJxfgvPkxCBtPTwiuNCflw2k2M9lcysoCcpr-akT0Q2ZNHewajq71EYmdOaJyWMlejxTm4Sh17AK0f-Cm)
8. [uber.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrdWzO0Enfbh03i_Onqw6Pa2basLm-oMz1_susEZ22JqrNFWUkg4QcDLfwQtjOnCHyXJBvgrE3Wj9d1TqxBI6U2av-6ztI_taMre-rCc6sxfVCH7uC33YQP1dlEjSZZ7PmS0FgdC2dv2dtq_KcH6b63WonpE4db_2uGpQO8hdbDmlshudOjyg-bO1_x32NLvELIsA94qtsgjbPTjCGUQcx)
9. [hongkongcard.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGWnEn56tVcTrw68LE4q1Ul6Lx_x-HgAAsEh2rZAuvaqo2a4tENPMQDtl1HtkSdWM6eVrrMQoKcNZeTVbS9FXEOHfpgGyCl-FAxSubqUBeNoW_lPzMKenzg43YPvajhlVH3TfjbaK3pH1dFBgTBOp8hnGGS-7jNmjn89Wz2V-tWIkbVr6-MHXPNrvXujLUqbI=)
10. [flyformiles.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHO7cES0V_O6AI-3vrB53E5KFF1g1O_gNa1FfWItdehtVQ4pYBMVOF34MemOnMcQdCW30eT3wJVtMKvBKUVCQQDbPztnhOf600TAYoIFRwkdt628bwbFJVL66usgNl5T8zFR3DBLGBn1OvvWWl7KQcm)
11. [flyformiles.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEscOE2qaxN-XxTYGxqWQ962AjdJAyPGgy-mR_PQCLqUum8YEmIiVPZ9y1wnk_45yx_iYX15lIjXd1bp-Qje91twYS9LZJ9MkSF0kt3oEgQavhhuKjVua-PzPUOZrA8Mds=)
12. [jetsofind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRYgNG5FVh0aTGbs7mw-z-v0mK1FuUtgWjSShqQ3WNjKIHv_z5YvtfsEsQxCuwPlNY7tL5oC9-jQRjiDqfMXVejDRrlvk6Krc0KQ3uubm1_hbO-MHlUu_Lug5siYRNUtGfVNyGUGTzCHdbHnA=)
13. [moneysmart.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5DPhjK5LdCK6TwhrwhCaArhZ9xUwKQ4kULmCHKzjfAruxw6YGcwEdC7wPk8iXGOSz9MsKzglRcGsJ1KoJoBuBfXSgNxlrFwd8k_tcPlEXED24Grf40d2v2FRQiYdeftzDxRYQRXW3YF5w1y3o)
14. [jetsofind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9F2HQp-bt0M0iRRrfBX4DDSHeVZvxqw6jC_f7fDaJ17rUbqBpNKBO4oQMs_oQJdyTbtsGxl5qcP-f5aCTOVgxuPh6ZPV1OrYnHHMABZYTHfMXezy-eAcFtm5vmanw7ipuwHzy40FMW-SNSMNxEeMrU28taydt)
15. [jetsofind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFrsAsYLubVzGNtv8vAsOXJdPh3RS0GKY8FKuu1bdqsQylm90nbRbdv8D0WLVPtsXeBUmOsvKBYZiCuchNoOt9yAZtWz0gGPyh4fBRm1vwZNihJKh1rV77Kd5v8IW6-APujrGyNJCcTbmsQUanBQcTiQ7NNoUsfLJNb70=)
16. [jetsofind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTFHg11i4neapkuODJPfjl4LpmtYCjTLWEIajKsKMTHhc-stPgOUHOsi_CLH6l0rmTWxA58JkBf_7HfklHTDOLjKmpQMBXR7TqWoKujJD657wdV-dWaDbGNGg6roJUsBtB)
17. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtMm4krgmJ6jR1Y2ZGOmRQ9cJRSFhkEHN4Z5HSXxdNdsqbyZ-xpPwi96tLVn5CNkkj08Qke0IIhuPZAFZ0xFqJDeacJRkempMkzFa2tJlaQDdoTYRaxoiNogLRQ6NFi0wNUcjZxkbOKx7TIcVvTFJRgggAgoKh670=)
18. [sc.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_ztQ2avPPm0a5s7nHADH70y3dg2MaHY7x_iO4JL9G-RVa0ghgHpwCGCh6_KXsclcRRUhsFJoSDqeO0gew1kuSjR_3oasd23McsoLB6YgQ_OCZlCLzz-FDmpfZtAP0Mu2XQImCkPacMMqNiC_p-a1JGmy0Furp)
19. [sc.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhMGvEzdnJ5L9uQgCgxxnEfx4R1uNWPjUx2qlUfjJdSwSDFltY8XLHTdU2piUyT5ULeOGwBb_iLVak6MCtvAppdyS9WJlAXaaVS34jEXlDaVdOPXr_BPNAjnaRj9MX4fXEcfGPekkptf6C1MvEOH82QshBLRDkH89CgTQIWU9l2ycZ2cyXEWaSndHhAdIik5Tspi6Py1BI-ho-gG-kwjKIC-Zlr0bNzI_Jau-k2-yGtjjhk2Pc-PW721PubLccPt-kErXj54o=)
20. [cathaypacific.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrMPW_xDEB8J5l5HERD_SGyAtlKK3tgHW8DF6YT7xrLzfLDYo4HuDM8AeYtvOpqkZvtWQ2yQbBrfKldTPeoJOVeTixyg0niwAabXomH4iqtiTyPC7tX2XMM0DdEOPMtGNz8WPUsi8l9NaY6YmChRX4vGRQwyQnAdOkcKj8LIr-Xg8v7lnTl79gfu5zCbay_b-13j-Pi7tCTbqSm5VdWV8DYtfoTu7ll_16QkLd4V2TWcbEV265FMPNjyDwPglllowdCHmMriWAqEKNGzE=)
21. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbYxk4GNMasskAsLGaxojOAYsXkBvgw9zE56EfIUKvFnJwFBjWRnXduVplWx5tyDTHtCd3wG3F4q6iaVzICSrjBXv6VinZTnCp0ARbPVQEhTUr3w5EqOqF2_tyDel-ESwehGwKrLSpeZPjlOPR4-QbBGkm6g653bl1SkcAXDmJ9-wzUDfL)
22. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSaWQvC6KO84oO9V8wJfK4YZiVnaMzAu0LOTn_UjoBqnDLXHrWSqrNP-6DCYQBFwmxYlHg92jXivJhJFWUOs_pgiPTGW1RC7IisdN8qJdx-BunVe-sOHayRbF9iKWf749y0l4y8La6Uaiobf-WSEsNLeRmDbw6H0swbms_mHVFb66K5i1X)
23. [boardingarea.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHu-GGkiNhsS_5UQdXsl3f_isCTPE_-7qa26Kf05eyj7TpzPR87Qn6clVRgoyEVqmFllqKz3u6z_gCZFRuE0vR_-mTYJgdKeJdOAidbT8Anm6hrxMtrbu-QYlZ3ILGv_XVF0nQWLHIuHf73QFej0XePwXAJN_eJ8hK16VigncnVB21iK5QUWJwkUKIOZawzGUlR6sWf-xVRIVIssH4DswBP0OxfcUrH)
24. [executivetraveller.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcxaDIb19ndKmiCTGmNm1CRw0EJXnYkBKXg66Zz55lc97c9PeUZfLpFb-23rF8rRjQcQv5NQAQwhBtVMq3UaOlgiBW7W_G6GJ9QpoLoeAm6HTZgq5nZoDcsf-vBt8V2dKX-b5S5DL-KRfBxIvmpAcq4EDCFeG6aRx-EeWxAsBi8torbQn0BjsBEW4=)
25. [mrmiles.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjmdEUjzLNYLukOXgtBJSzt-KtX9p0RBDxkE7oLB2qTvpejAWhfhRoxrdvEzXwKLiG-hPJW1g3FvAy6Dar24NR4RyuiDQySExBbGluQdHPDS1I1Rhjj_jp9AQZni2F)
26. [hkcashrebate.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTIcmW0p95x-1jE9ByHcUn4FpCqwuE1Oe5H7DtPvPyyJfUI7euxwoTx7F3ABk1bG3qAzFpI9jzeqATsW3xhuP8qmE92_aIYZfAjSnQMcde9ThJxYOjrLDw)
27. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1uD0-5haVND1sQ7bLjgZU-2aFapg2c7OZK7eICZ_yuh2bkJ1COVKSsyRiZGSBpT8O0YDEpYuP4ia2rJG5AG6jMY452XGtLfjyCGE7x4ZCjLQNUuYIZj3zoucZpJ8eI5jtJF_lSvle8NotqbZ2M4q4HlE2VYFYX3qoU3kkLB1wWdTHcfAwrhBLaclDrLtXGHILPJY-o5A=)
28. [hsbc.com.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpSDypGeoVtsVjPkmS8CYk1TIAFwyf8-y3CgEUEgSKiXinmmGsveEx3HX_ABESuukYib7WxdPRidK0UwNahGKYoAHstG3u-dO2WHZ5k2gO4UDWL0KWg3PntTo2gRfDvOoip75sChrhpTPQzgvRfIsBnY5VpnJ2k0QdenkH3wo_q4pNtQ9zjUUXUsGP1OX4xPvFTB1IJSSFCyKiMFWiiN7VXMOBdYY=)
29. [jetsofind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQxUEWvKNQoTSioliGWwMVCImGp2aYog4blzlAbbCCwp3dEexZIQqRl8Cmp3GNblnbe9ua5ox9OS1tR6hiw_TTiC9rwoa5yLo0KcQSYmIUl1tFsTfw7N1TgNxqL3xRAb9pPnR8VNiOE5pa0iki33vO3CGYRA==)
