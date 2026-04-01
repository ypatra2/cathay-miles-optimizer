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
    "Hotels (Direct Booking)",              # DELTA: New category for SC Cathay (cite: 1, 2)
    "Overseas (Physical)",                  # DELTA: Split from 'Overseas' for HSBC Travel Guru (cite: 6, 7)
    "Overseas (Online)",                    # DELTA: Split from 'Overseas' for HSBC Travel Guru (cite: 6, 7)
    "Supermarkets",
    "Insurance / Utilities / Tax",
    "Online Bill Payment (e-Banking)",      # DELTA: New category for HSBC 0.4% RC (cite: 8)
    "E-Wallets (PayMe/Alipay/WeChat)",
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
        # DELTA: E-wallets, Insurance, and Tax earn ZERO (cite: 2, 10)
        if category in ["E-Wallets (PayMe/Alipay/WeChat)", "Insurance / Utilities / Tax"]:
            rate = 0.0
            notes = "Excluded: Strictly excluded from earning Asia Miles by Standard Chartered terms."
            miles = 0.0
        # DELTA: Cathay Pacific Flights, HK Express Flights, Cathay Partner Dining remain HK$2=1mi (cite: 1, 2)
        elif category in ["Cathay Pacific Flights", "HK Express Flights", "Cathay Partner Dining"]:
            rate = 2.0
            notes = "Direct earn HK$2=1mi. Cathay Partner exclusive: HK$4=2 miles."
        # DELTA: Dining, Hotels (Direct), Overseas (Physical/Online) earn HK$4=1mi (cite: 1, 2)
        elif category in ["Dining (Premium)", "Dining (Casual)", "Hotels (Direct Booking)", "Overseas (Physical)", "Overseas (Online)"]:
            rate = 4.0
            notes = "Dining/Hotels/Overseas rate: HK$4=1 mile."
        else:
            # DELTA: Online General, Food Delivery, OTA, Ride-Hailing, Supermarkets, Other Airlines, Octopus AAVS, Online Bill Payment, In-Store General revert to HK$6=1mi (cite: 1, 2, 8)
            # This covers: Online General, Food Delivery, Travel Booking (Non-Designated OTA), Travel Booking (Designated OTA),
            # Ride-Hailing (Uber/Taxi Apps), Supermarkets, Octopus AAVS, Other Airlines (Direct Booking),
            # Other Airlines (via OTA), Shopping (In-Store General), EveryMile Designated Everyday, Shopping (Designated 8%), Online Bill Payment (e-Banking)
            rate = 6.0
            notes = "Other local spending, online retail, and bill payments: HK$6=1 mile."

        miles = amount / rate if rate > 0 else 0

    # ══════════════════════════════════════════════════
    # HSBC EVERYMILE VISA
    # 1 RC = 20 Miles (best HSBC conversion)
    # ══════════════════════════════════════════════════
    elif card == "HSBC EveryMile VISA":
        # DELTA: E-wallets earn ZERO (cite: 2, 3, 9, 10)
        if category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            notes = "Excluded: PayMe and other e-wallets no longer earn RewardCash as of July 2025."
            miles = 0.0
        # DELTA: Supermarkets, Insurance/Utilities/Tax, Online Bill Payment, Octopus AAVS earn 0.4% RC (HK$12.5=1mi) (cite: 8, 9, 12, 13, 14)
        elif category in ["Supermarkets", "Insurance / Utilities / Tax", "Online Bill Payment (e-Banking)", "Octopus AAVS"]:
            rate = 12.5
            notes = "Low-earn: 0.4% RC (HK$12.5=1mi). Use other cards for these categories."
        # DELTA: EveryMile designated merchants earn HK$2=1mi (cite: EveryMile T&C)
        elif category in ["Travel Booking (Designated OTA)", "EveryMile Designated Everyday"]:
            rate = 2.0
            notes = "EveryMile designated merchant: HK$2=1 mile."
        # DELTA: Overseas (Physical) with promo threshold and cap (Jan-Mar 2026 Phase) (cite: 13, 14, 15, 16)
        elif category == "Overseas (Physical)":
            if amount >= 12000:
                # Max spend for the extra 1.5% RC is 15000 (cap $225 RC)
                bonus_eligible_amount = min(amount, 15000)
                base_miles = amount / 5.0  # Base 1% RC -> HK$5=1mi
                bonus_miles = bonus_eligible_amount / 3.333  # Extra 1.5% RC -> HK$3.33=1mi
                miles = base_miles + bonus_miles
                rate = amount / miles if miles > 0 else 0
                notes = f"Overseas Promo Triggered: HK$2/mi effective on first HK${bonus_eligible_amount:.2f}, HK$5/mi thereafter. Total miles: {math.floor(miles)}."
            else:
                rate = 5.0
                notes = "Did not meet HK$12k overseas threshold. Base HK$5=1mi applied."
        # DELTA: Overseas (Online) excluded from Travel Guru bonuses, earns base 1% RC (HK$5=1mi) (cite: 6, 7)
        elif category == "Overseas (Online)":
            rate = 5.0
            notes = "Overseas (Online) excluded from Travel Guru bonuses. Base HK$5=1mi."
        else:
            # DELTA: All other categories earn base 1% RC (HK$5=1mi) (cite: EveryMile T&C)
            rate = 5.0
            notes = "General rate: HK$5=1 mile."

        miles = amount / rate if rate > 0 else 0

    # ══════════════════════════════════════════════════
    # HSBC RED MASTERCARD
    # 1 RC = 10 Miles
    # ══════════════════════════════════════════════════
    elif card == "HSBC Red Mastercard":
        # DELTA: E-wallets earn ZERO (cite: 2, 3, 9, 10)
        if category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            miles = 0.0
            notes = "Excluded: PayMe and other e-wallets no longer earn RewardCash as of July 2025."
        # DELTA: Supermarkets, Insurance/Utilities/Tax, Online Bill Payment, Octopus AAVS earn 0.4% RC (HK$25=1mi) (cite: 3, 4, 8, 11)
        elif category in ["Supermarkets", "Insurance / Utilities / Tax", "Online Bill Payment (e-Banking)", "Octopus AAVS"]:
            rate = 25.0
            miles = amount / rate
            notes = "Low-earn: 0.4% base rate (HK$25=1mi)."
        # DELTA: Shopping (Designated 8%) with HK$1,250 monthly cap (cite: 3, 11)
        elif category == "Shopping (Designated 8%)":
            if amount <= 1250:
                rate = 1.25
                miles = amount / rate
                notes = "8% rebate applied (HK$1.25=1mi)."
            else:
                base_miles = 1250 / 1.25
                excess_miles = (amount - 1250) / 25.0
                miles = base_miles + excess_miles
                rate = amount / miles
                notes = f"WARNING: 8% cap (HK$1,250) exceeded. First HK$1,250 earns HK$1.25=1mi, excess HK${amount-1250:.2f} earns base 0.4% (HK$25=1mi)."
        # DELTA: Online General, Food Delivery, OTA, Ride-Hailing, Overseas (Online) with HK$10,000 monthly cap for 4% online rebate (cite: 3, 4, 6, 7)
        elif category in ["Online General", "Food Delivery", "Travel Booking (Non-Designated OTA)", "Travel Booking (Designated OTA)",
                          "Ride-Hailing (Uber/Taxi Apps)", "Overseas (Online)"]:
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
                notes = f"WARNING: 4% cap (HK$10K) exceeded. First HK$10,000 earns HK