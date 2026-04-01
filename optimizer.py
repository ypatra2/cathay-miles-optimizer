import math

# Credit Card Definitions
CARDS = [
    "Standard Chartered Cathay Mastercard",
    "HSBC EveryMile VISA",
    "HSBC Red Mastercard",
    "HSBC VISA Signature",
]

# Expanded category list aligned to Cathay_Data_v1.2.md
CATEGORIES = [
    "Cathay Pacific Flights",
    "HK Express Flights",
    "Other Airlines (Direct Booking)",
    "Other Airlines (via OTA)",
    "Travel Booking (Designated OTA)",      # Klook, KKday — EveryMile designated
    "Travel Booking (Non-Designated OTA)",  # Trip.com, Expedia, MakeMyTrip
    "EveryMile Designated Everyday",        # Starbucks, MTR, KMB, Pacific Coffee, etc.
    "Ride-Hailing (Uber/Taxi Apps)",        # Uber, HKTaxi, DiDi — online e-commerce coded
    "Cathay Partner Dining",                # Exclusive SC Cathay HK$4=2 miles
    "Dining (Premium)",                     # Michelin / high-end
    "Dining (Casual)",                      # Regular restaurants
    "Food Delivery",                        # Keeta, Foodpanda — MCC 5814, NOT dining
    "Shopping (Designated 8%)",             # GU, Decathlon, lululemon, Sushiro, TamJai, etc.
    "Online General",                       # Amazon, Taobao, HKTVmall, Zalora, etc.
    "Shopping (In-Store General)",          # Non-designated retail
    "Octopus AAVS",
    "Overseas",
    "Supermarkets",                         # DELTA: New category for specific handling (cite: 2, 3)
    "Insurance / Utilities / Tax",          # DELTA: New category for specific handling (cite: 6, 11, 13, 15)
    "E-Wallets (PayMe/Alipay/WeChat)",      # DELTA: New category for zero-earn handling (cite: 4, 5, 6)
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
        # DELTA: E-wallets, Insurance, and Tax earn ZERO (cite: 5, 6, 11)
        if category in ["E-Wallets (PayMe/Alipay/WeChat)", "Insurance / Utilities / Tax"]:
            rate = 0.0
            notes = "Excluded: Strictly excluded from earning Asia Miles by Standard Chartered terms."
            miles = 0.0
        elif category in ["Cathay Pacific Flights", "HK Express Flights"]:
            rate = 2.0
            notes = "Direct earn HK$2=1mi. +2,667 bonus miles per HK$8K/quarter. +10% award discount."
        elif category == "Cathay Partner Dining":
            rate = 2.0  # HK$4 = 2 miles → effective HK$2 per mile
            notes = "Cathay Partner exclusive: HK$4=2 miles. Check dining.cathaypacific.com."
        elif category in ["Dining (Premium)", "Dining (Casual)", "Overseas"]:
            rate = 4.0
            notes = "Dining/Overseas rate: HK$4=1 mile."
        elif category == "Other Airlines (Direct Booking)":
            rate = 4.0
            notes = "Direct airline booking (MCC 3000-3350) = overseas rate HK$4=1mi."
        # DELTA: Online General, Food Delivery, OTA, Ride-Hailing now HK$4=1mi (cite: 1, 10, MCC intelligence)
        elif category in ["Online General", "Food Delivery", "Travel Booking (Non-Designated OTA)", "Travel Booking (Designated OTA)", "Ride-Hailing (Uber/Taxi Apps)"]:
            rate = 4.0
            notes = "Eligible online retail spending earns HK$4=1 mile."
        elif category == "Octopus AAVS":
            rate = 6.0
            notes = "Automatic monthly conversion. Passive earning, zero effort."
        # DELTA: Supermarkets fall to base rate (cite: 1)
        elif category == "Supermarkets":
            rate = 6.0
            notes = "Supermarkets earn the base local rate of HK$6=1 mile."
        else:
            # Remaining categories like Shopping (In-Store General), EveryMile Designated Everyday
            rate = 6.0
            notes = "Other local spending: HK$6=1 mile."

        miles = amount / rate if rate > 0 else 0

    # ══════════════════════════════════════════════════
    # HSBC EVERYMILE VISA
    # 1 RC = 20 Miles (best HSBC conversion)
    # ══════════════════════════════════════════════════
    elif card == "HSBC EveryMile VISA":
        # DELTA: E-wallets are nerfed to zero (cite: 4)
        if category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            notes = "Excluded: PayMe and other e-wallets no longer earn RewardCash as of July 2025."
            miles = 0.0
        # DELTA: Supermarkets are severely penalized (cite: 2, 3)
        elif category == "Supermarkets":
            rate = 12.5
            notes = "MAJOR EXCLUSION: Supermarkets earn only 0.4% RC (HK$12.5=1mi). Do not use this card."
        # DELTA: Insurance / Utilities / Tax earn 0.4% RC (cite: 12, 13, 14)
        elif category == "Insurance / Utilities / Tax":
            rate = 12.5
            notes = "Online bill payments earn only 0.4% base rate (HK$12.5=1mi)."
        elif category in ["Travel Booking (Designated OTA)", "EveryMile Designated Everyday"]:
            # Klook, KKday, Starbucks, MTR, KMB, Pacific Coffee, etc.
            rate = 2.0
            notes = "EveryMile designated merchant: HK$2=1 mile."
        elif category == "Overseas":
            rate = 2.0
            notes = "Overseas HK$2=1mi IF HK$12K+ promo threshold met (Jan-Jun 2026). Otherwise HK$5=1mi."
        elif category == "Cathay Pacific Flights":
            rate = 5.0
            notes = "Non-designated on EveryMile. Use SC Cathay instead for HK$2=1mi."
        elif category == "Octopus AAVS":
            # Special low-earn: 1 RC per HK$250, × 20 miles = HK$12.5 per mile
            rate = 12.5
            notes = "AAVS low-earn: 1RC/HK$250 (×20mi) = HK$12.5/mi. SC Cathay is far better at HK$6/mi."
        else:
            # General local, OTA (non-designated), airlines, dining, shopping, food delivery
            rate = 5.0
            notes = "General rate: HK$5=1 mile."

        miles = amount / rate if rate > 0 else 0

    # ══════════════════════════════════════════════════
    # HSBC RED MASTERCARD
    # 1 RC = 10 Miles
    # ══════════════════════════════════════════════════
    elif card == "HSBC Red Mastercard":
        # DELTA: E-wallets nerfed to zero (cite: 4)
        if category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            miles = 0.0
            notes = "Excluded: PayMe and other e-wallets no longer earn RewardCash as of July 2025."
        # DELTA: Supermarkets, Insurance/Utilities/Tax earn 0.4% RC (cite: 13, 14, 18)
        elif category in ["Supermarkets", "Insurance / Utilities / Tax"]:
            rate = 25.0
            miles = amount / rate
            notes = "Earns 0.4% base rate (HK$25=1mi)."
        elif category == "Shopping (Designated 8%)":
            # DELTA: Implement HK$1,250 monthly cap for 8% rebate (cite: 7, 19)
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
        elif category in ["Online General", "Food Delivery",
                          "Travel Booking (Non-Designated OTA)", "Travel Booking (Designated OTA)",
                          "Ride-Hailing (Uber/Taxi Apps)"]:
            # DELTA: Implement HK$10,000 monthly cap for 4% online rebate (cite: 7, 8)
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
            # Base 0.4% for everything else (dining, in-store, Octopus, flights)
            rate = 25.0
            notes = "Base 0.4% earn rate."
            miles = amount / rate

    # ══════════════════════════════════════════════════
    # HSBC VISA SIGNATURE
    # 1 RC = 10 Miles. Assumes Red Hot Rewards category = DINING
    # ══════════════════════════════════════════════════
    elif card == "HSBC VISA Signature":
        # DELTA: E-wallets nerfed to zero (cite: 4)
        if category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            miles = 0.0
            notes = "Excluded: PayMe and other e-wallets no longer earn RewardCash as of July 2025."
        # DELTA: Supermarkets, Insurance/Utilities/Tax earn 0.4% RC (cite: 13, 14, 18)
        elif category in ["Supermarkets", "Insurance / Utilities / Tax"]:
            rate = 25.0
            miles = amount / rate
            notes = "Non-bonus/bill payment earns 0.4% base rate (HK$25=1mi)."
        elif category in ["Dining (Premium)", "Dining (Casual)", "Cathay Partner Dining"]:
            # DELTA: Add note about annual HK$100,000 cap for 5X Red Hot Rewards (cite: 8, 9)
            rate = 2.78
            miles = amount / rate
            notes = "3.6% Red Hot Rewards (Dining). *Assumes user has not exceeded HK$100K annual category cap.* B1G1 at Michelin restaurants."
        elif category == "Octopus AAVS":
            # AAVS is special low-earn on VISA Sig: base 0.4% = HK$25 per mile
            rate = 25.0
            notes = "AAVS low-earn category: base 0.4% = HK$25/mi. Use SC Cathay instead."
            miles = amount / rate
        else:
            # 1.6% RC → 1.6 RC per $100 → 16 miles per $100 → HK$6.25 = 1 mile
            rate = 6.25
            notes = "1.6% base for non-dining categories."
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
# PATCH_SUMMARY: {"changes": ["Added 'Supermarkets', 'Insurance / Utilities / Tax', 'E-Wallets (PayMe/Alipay/WeChat)' to CATEGORIES list", "Standard Chartered Cathay Mastercard: 'Online General', 'Food Delivery', 'Travel Booking (Non-Designated OTA)', 'Travel Booking (Designated OTA)', 'Ride-Hailing (Uber/Taxi Apps)' rate changed from HK$6 to HK$4", "Standard Chartered Cathay Mastercard: 'E-Wallets (PayMe/Alipay/WeChat)' and 'Insurance / Utilities / Tax' set to 0 miles", "Standard Chartered Cathay Mastercard: 'Supermarkets' explicitly set to HK$6=1mi", "HSBC EveryMile VISA: 'Supermarkets' rate changed from HK$5 to HK$12.5", "HSBC EveryMile VISA: 'E-Wallets (PayMe/Alipay/WeChat)' set to 0 miles", "HSBC EveryMile VISA: 'Insurance / Utilities / Tax' rate changed from HK$5 to HK$12.5", "HSBC Red Mastercard: Implemented HK$1,250 monthly cap for 'Shopping (Designated 8%)' (excess earns 0.4%)", "HSBC Red Mastercard: Implemented HK$10,000 monthly cap for 'Online General', 'Food Delivery', 'Travel Booking (Non-Designated OTA)', 'Travel Booking (Designated OTA)', 'Ride-Hailing (Uber/Taxi Apps)' (excess earns 0.4%)", "HSBC Red Mastercard: 'E-Wallets (PayMe/Alipay/WeChat)' set to 0 miles", "HSBC Red Mastercard: 'Supermarkets' and 'Insurance / Utilities / Tax' explicitly set to HK$25=1mi", "HSBC VISA Signature: Added note about HK$100,000 annual cap for 'Dining' Red Hot Rewards", "HSBC VISA Signature: 'E-Wallets (PayMe/Alipay/WeChat)' set to 0 miles", "HSBC VISA Signature: 'Supermarkets' and 'Insurance / Utilities / Tax' rate changed from HK$6.25 to HK$25"], "categories_added": ["Supermarkets", "Insurance / Utilities / Tax", "E-Wallets (PayMe/Alipay/WeChat)"], "rates_changed": 9}