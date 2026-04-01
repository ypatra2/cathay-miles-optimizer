import math

# Credit Card Definitions
CARDS = [
    "Standard Chartered Cathay Mastercard",
    "HSBC EveryMile VISA",
    "HSBC Red Mastercard",
    "HSBC VISA Signature",
]

# Expanded category list aligned to Cathay_Data_v1.2.md and March 2026 Delta Report
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
    "Hotels (Direct Booking)",              # DELTA: New category for SC Cathay (cite: 1, 2)
    "Overseas (Physical)",                  # DELTA: Split from 'Overseas' for HSBC Travel Guru (cite: 6, 7)
    "Overseas (Online)",                    # DELTA: Split from 'Overseas' for HSBC Travel Guru (cite: 6, 7)
    "Supermarkets",
    "Insurance / Utilities / Tax",
    "E-Wallets (PayMe/Alipay/WeChat)",
    "Online Bill Payment (e-Banking)",      # DELTA: New category for HSBC (cite: 8)
]


def calculate_miles(card, category, amount):
    """
    Calculates the Asia Miles earned for a specific card, category, and amount.
    All rates sourced from Cathay_Data_v1.2.md and March 2026 Delta Report.
    Returns (miles_earned, effective_rate_hks_per_mile, notes)
    """
    miles = 0.0
    rate = 0.0
    notes = ""

    # ══════════════════════════════════════════════════
    # STANDARD CHARTERED CATHAY MASTERCARD
    # ══════════════════════════════════════════════════
    if card == "Standard Chartered Cathay Mastercard":
        # DELTA: E-wallets, Insurance, Tax, and Online Bill Payment earn ZERO (cite: 2, 8, 9, 10)
        if category in ["E-Wallets (PayMe/Alipay/WeChat)", "Insurance / Utilities / Tax", "Online Bill Payment (e-Banking)"]:
            rate = 0.0
            notes = "Excluded: Strictly excluded from earning Asia Miles by Standard Chartered terms."
            miles = 0.0
        elif category in ["Cathay Pacific Flights", "HK Express Flights", "Cathay Partner Dining"]:
            rate = 2.0
            notes = "Direct earn HK$2=1mi. +2,667 bonus miles per HK$8K/quarter. +10% award discount." # DELTA: Consolidated note
        # DELTA: Hotels (Direct Booking) added to HK$4=1mi tier, Overseas split (cite: 1, 2, 6, 7)
        elif category in ["Dining (Premium)", "Dining (Casual)", "Hotels (Direct Booking)", "Overseas (Physical)", "Overseas (Online)"]:
            rate = 4.0
            notes = "Dining/Hotels/Overseas rate: HK$4=1 mile." # DELTA: Updated note for HK$4=1mi categories
        else:
            # DELTA: Online General, Food Delivery, OTA, Ride-Hailing, Other Airlines (Direct Booking) now HK$6=1mi (cite: 1, 2)
            # Remaining categories like Shopping (In-Store General), EveryMile Designated Everyday, Supermarkets, Octopus AAVS
            rate = 6.0
            notes = "Other local spending, online retail, and non-designated travel: HK$6=1 mile." # DELTA: Updated note for HK$6=1mi categories

        miles = amount / rate if rate > 0 else 0

    # ══════════════════════════════════════════════════
    # HSBC EVERYMILE VISA
    # 1 RC = 20 Miles (best HSBC conversion)
    # ══════════════════════════════════════════════════
    elif card == "HSBC EveryMile VISA":
        # DELTA: E-wallets are nerfed to zero (cite: 9, 10)
        if category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            notes = "Excluded: PayMe and other e-wallets no longer earn RewardCash as of July 2025."
            miles = 0.0
        # DELTA: Supermarkets, Insurance/Utilities/Tax, Online Bill Payment, Octopus AAVS earn 0.4% RC (cite: 8, 9)
        elif category in ["Supermarkets", "Insurance / Utilities / Tax", "Online Bill Payment (e-Banking)", "Octopus AAVS"]:
            rate = 12.5 # 0.4% RC -> 1 RC per 250 -> 20 miles per 250 -> 12.5 HKD/mi
            notes = "Low-earn: 0.4% RC (HK$12.5=1mi). Use other cards for these categories."
            miles = amount / rate
        elif category in ["Travel Booking (Designated OTA)", "EveryMile Designated Everyday"]:
            # Klook, KKday, Starbucks, MTR, KMB, Pacific Coffee, etc.
            rate = 2.0
            notes = "EveryMile designated merchant: HK$2=1 mile."
            miles = amount / rate
        elif category == "Overseas (Physical)": # DELTA: New category for physical overseas spend (cite: 6, 7)
            # DELTA: Evaluate Promo Threshold (Jan-Jun 2026 Phase) (cite: 13, 14, 15)
            if amount >= 12000:
                # DELTA: Max spend for the extra 1.5% RC is 15000 (cap $225 RC) (cite: 14, 15, 16)
                bonus_eligible_amount = min(amount, 15000)
                base_miles = amount / 5.0 # Base 1% RC -> HK$5=1mi
                bonus_miles = bonus_eligible_amount / 3.333 # Extra 1.5% RC -> HK$3.33=1mi
                miles = base_miles + bonus_miles
                rate = amount / miles if miles > 0 else 0
                notes = "Overseas Promo Triggered: HK$2/mi effective on first HK$15K, HK$5/mi thereafter. (Jan-Mar 2026)"
            else:
                rate = 5.0
                notes = "Did not meet HK$12k overseas threshold. Base HK$5=1mi applied."
                miles = amount / rate
        elif category == "Overseas (Online)": # DELTA: New category for online overseas spend (cite: 6, 7)
            rate = 5.0 # Excluded from Travel Guru bonuses and Physical promos (cite: 6, 7)
            notes = "Online overseas spending: HK$5=1 mile (excluded from Travel Guru bonus)."
            miles = amount / rate
        else:
            # General local, OTA (non-designated), airlines, dining, shopping, food delivery, Hotels (Direct Booking)
            rate = 5.0
            notes = "General rate: HK$5=1 mile."
            miles = amount / rate

    # ══════════════════════════════════════════════════
    # HSBC RED MASTERCARD
    # 1 RC = 10 Miles
    # ══════════════════════════════════════════════════
    elif card == "HSBC Red Mastercard":
        # DELTA: E-wallets nerfed to zero (cite: 3, 4, 9, 10)
        if category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            miles = 0.0
            notes = "Excluded: PayMe and other e-wallets no longer earn RewardCash as of July 2025."
        # DELTA: Supermarkets, Insurance/Utilities/Tax, Online Bill Payment, Octopus AAVS earn 0.4% RC (cite: 3, 8)
        elif category in ["Supermarkets", "Insurance / Utilities / Tax", "Online Bill Payment (e-Banking)", "Octopus AAVS"]:
            rate = 25.0
            miles = amount / rate
            notes = "Low-earn: 0.4% RC (HK$25=1mi). Use other cards for these categories."
        elif category == "Shopping (Designated 8%)":
            # DELTA: Implement HK$1,250 monthly cap for 8% rebate (cite: 3, 11)
            if amount <= 1250:
                rate = 1.25
                miles = amount / rate
                notes = "8% rebate applied (HK$1.25=1mi)."
            else:
                base_miles = 1250 / 1.25
                excess_miles = (amount - 1250) / 25.0  # Reverts to 0.4% base
                miles = base_miles + excess_miles
                rate = amount / miles  # Blended effective rate
                notes = f"WARNING: 8% cap (HK$1,250) exceeded. First HK$1,250 earns HK$1.25=1mi, excess HK${amount-1250:.2f} earns base 0.4% (HK$25=1mi)."
        # DELTA: Overseas (Online) added to 4% online category (cite: 6, 7)
        elif category in ["Online General", "Food Delivery",
                          "Travel Booking (Non-Designated OTA)", "Travel Booking (Designated OTA)",
                          "Ride-Hailing (Uber/Taxi Apps)", "Overseas (Online)"]:
            # DELTA: Implement HK$10,000 monthly cap for 4% online rebate (cite: 3, 4)
            if amount <= 10000:
                rate = 2.5
                miles = amount / rate
                notes = "4% online rebate applied (HK$2.5=1mi)."
                if category == "Ride-Hailing (Uber/Taxi Apps)":
                    notes += " +20mi/ride via Cathay partnership!"
            else:
                base_miles = 10000 / 2.5
                excess_miles = (amount - 10000) / 25.0
                miles = base_miles + excess_miles
                rate = amount / miles
                notes = f"WARNING: 4% cap (HK$10K) exceeded. First HK$10,000 earns HK$2.5=1mi, excess HK${amount-10000:.2f} earns base 0.4% (HK$25=1mi)."
                if category == "Ride-Hailing (Uber/Taxi Apps)":
                    notes += " +20mi/ride via Cathay partnership!"
        else:
            # Base 0.4% for everything else (dining, in-store, flights, Hotels (Direct Booking), Overseas (Physical))
            rate = 25.0
            notes = "Base 0.4% earn rate (HK$25=1mi)."
            miles = amount / rate

    # ══════════════════════════════════════════════════
    # HSBC VISA SIGNATURE
    # 1 RC = 10 Miles. Assumes Red Hot Rewards category = DINING
    # ══════════════════════════════════════════════════
    elif card == "HSBC VISA Signature":
        # DELTA: E-wallets nerfed to zero (cite: 9, 10)
        if category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            miles = 0.0
            notes = "Excluded: PayMe and other e-wallets no longer earn RewardCash as of July 2025."
        # DELTA: Food Delivery explicitly bypasses Red Hot Dining, consolidated 0.4% RC categories (cite: 5, 8)
        elif category in ["Food Delivery", "Supermarkets", "Insurance / Utilities / Tax", "Online Bill Payment (e-Banking)", "Octopus AAVS"]:
            rate = 25.0 # Explicitly bypasses Red Hot Dining
            miles = amount / rate
            notes = "Low-earn: 0.4% RC (HK$25=1mi). Food Delivery, Bill Payments, Supermarkets, AAVS."
        elif category in ["Dining (Premium)", "Dining (Casual)", "Cathay Partner Dining"]:
            # DELTA: Implement HK$100,000 annual cap for 5X Red Hot Rewards (cite: 12)
            if amount <= 100000: # Assuming annual cap limit context for this transaction
                rate = 2.78 # 3.6% RC (9X)
                miles = amount / rate
                notes = "3.6% Red Hot Rewards (Dining). *Assumes user has not exceeded HK$100K annual category cap.* B1G1 at Michelin restaurants."
            else:
                rate = 25.0 # Drops to base 0.4% if annual cap exceeded
                miles = amount / rate
                notes = "WARNING: HK$100K annual dining cap exceeded. Base 0.4% (HK$25=1mi) applied."
        elif category in ["Overseas (Physical)"]: # DELTA: New category for physical overseas spend (cite: 6, 7)
            rate = 6.25 # 1.6% RC Base (assuming non-Red Hot allocation, or mention Travel Guru stacking potential)
            miles = amount / rate
            notes = "Overseas (Physical): 1.6% base RC (HK$6.25=1mi). Travel Guru bonus requires registration."
        elif category in ["Overseas (Online)"]: # DELTA: New category for online overseas spend (cite: 6, 7)
            rate = 6.25 # Excluded from Travel Guru bonuses (cite: 6, 7)
            miles = amount / rate
            notes = "Online overseas spending: 1.6% base RC (HK$6.25=1mi). Excluded from Travel Guru bonus."
        else:
            # 1.6% RC for Online General, Shopping, Flights, Hotels (Direct Booking)
            rate = 6.25
            notes = "General 1.6% base earn rate (HK$6.25=1mi)."
            miles = amount / rate

    return math.floor(miles), round(rate, 2), notes


def get_recommendations(category, amount):
    """Returns sorted list of card recommendations for a given category+amount."""
    results = []
    for card in CARDS:
        m, r, n = calculate_miles(card, category, amount)
        results.append({
            "card": card,
            "miles": m,
            "rate": r,
            "notes": n
        })

    # Sort by miles descending (most miles first)
    results.sort(key=lambda x: x['miles'], reverse=True)
    return results
# PATCH_SUMMARY: {"changes": ["Updated CATEGORIES list with new splits and additions.", "Standard Chartered Cathay Mastercard: 'Online General', 'Food Delivery', 'Travel Booking (OTA)', 'Ride-Hailing (Uber/Taxi Apps)', 'Other Airlines (Direct Booking)' rates changed from HK$4 to HK$6.", "Standard Chartered Cathay Mastercard: Added 'Hotels (Direct Booking)' at HK$4=1mi.", "Standard Chartered Cathay Mastercard: Consolidated zero-earn categories to include 'Online Bill Payment (e-Banking)'.", "HSBC EveryMile VISA: 'Supermarkets', 'Insurance / Utilities / Tax' rates changed from HK$5 to HK$12.5.", "HSBC EveryMile VISA: Added 'Online Bill Payment (e-Banking)' at HK$12.5=1mi.", "HSBC EveryMile VISA: Implemented overseas spending promo logic with HK$12K threshold and HK$15K bonus cap for 'Overseas (Physical)'.", "HSBC EveryMile VISA: 'Overseas (Online)' set to HK$5=1mi.", "HSBC Red Mastercard: Added 'Online Bill Payment (e-Banking)' at HK$25=1mi.", "HSBC Red Mastercard: 'Overseas (Online)' added to 4% online category with HK$10K cap.", "HSBC Red Mastercard: 'Overseas (Physical)' set to base 0.4% (HK$25=1mi).", "HSBC VISA Signature: 'Food Delivery' rate changed from HK$2.78 to HK$25.", "HSBC VISA Signature: 'Supermarkets', 'Insurance / Utilities / Tax' rates changed from HK$6.25 to HK$25.", "HSBC VISA Signature: Added 'Online Bill Payment (e-Banking)' at HK$25=1mi.", "HSBC VISA Signature: Implemented HK$100K annual cap for 'Dining' categories.", "HSBC VISA Signature: 'Overseas (Physical)' and 'Overseas (Online)' set to 1.6% base (HK$6.25=1mi)."], "categories_added": ["Hotels (Direct Booking)", "Overseas (Physical)", "Overseas (Online)", "Online Bill Payment (e-Banking)"], "rates_changed": 11}