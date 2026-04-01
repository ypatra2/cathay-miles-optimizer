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
    "Hotels (Direct Booking)",              # DELTA: New category for SC Cathay (cite: 1, 2)
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
    "Overseas (Physical)",                  # DELTA: Split from 'Overseas' for HSBC Travel Guru rules (cite: 6, 7)
    "Overseas (Online)",                    # DELTA: Split from 'Overseas' for HSBC Travel Guru rules (cite: 6, 7)
    "Supermarkets",
    "Insurance / Utilities / Tax",
    "Online Bill Payment (e-Banking)",      # DELTA: New category for HSBC (cite: 8)
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
        # DELTA: E-wallets, Insurance, Tax, and Online Bill Payment earn ZERO (cite: 2, 3, 8, 9, 10)
        if category in ["E-Wallets (PayMe/Alipay/WeChat)", "Insurance / Utilities / Tax", "Online Bill Payment (e-Banking)"]:
            rate = 0.0
            notes = "Excluded: Strictly excluded from earning Asia Miles by Standard Chartered terms."
            miles = 0.0
        elif category in ["Cathay Pacific Flights", "HK Express Flights", "Cathay Partner Dining"]:
            rate = 2.0
            notes = "Direct earn HK$2=1mi. +2,667 bonus miles per HK$8K/quarter. +10% award discount."
        # DELTA: Added Hotels (Direct Booking) to HK$4=1mi tier, split Overseas (cite: 1, 2)
        elif category in ["Dining (Premium)", "Dining (Casual)", "Hotels (Direct Booking)", "Overseas (Physical)", "Overseas (Online)"]:
            rate = 4.0
            notes = "Dining/Hotels/Overseas rate: HK$4=1 mile."
        else:
            # DELTA: Online General, Food Delivery, OTA, Ride-Hailing, Other Airlines (Direct Booking) now HK$6=1mi (cite: 1, 2)
            # This 'else' covers: Other Airlines (Direct Booking), Other Airlines (via OTA), Travel Booking (Designated OTA), Travel Booking (Non-Designated OTA), EveryMile Designated Everyday, Ride-Hailing (Uber/Taxi Apps), Food Delivery, Shopping (Designated 8%), Online General, Shopping (In-Store General), Octopus AAVS, Supermarkets
            rate = 6.0
            notes = "Other local spending, online retail, and non-designated travel: HK$6=1 mile."

        miles = amount / rate if rate > 0 else 0

    # ══════════════════════════════════════════════════
    # HSBC EVERYMILE VISA
    # 1 RC = 20 Miles (best HSBC conversion)
    # ══════════════════════════════════════════════════
    elif card == "HSBC EveryMile VISA":
        # DELTA: E-wallets are nerfed to zero (cite: 4, 9, 10)
        if category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            notes = "Excluded: PayMe and other e-wallets no longer earn RewardCash as of July 2025."
            miles = 0.0
        # DELTA: Supermarkets, Insurance/Utilities/Tax, Online Bill Payment, Octopus AAVS earn 0.4% RC (HK$12.5=1mi) (cite: 2, 3, 8, 9, 12, 13, 14)
        elif category in ["Supermarkets", "Insurance / Utilities / Tax", "Online Bill Payment (e-Banking)", "Octopus AAVS"]:
            rate = 12.5
            notes = "Low-earn: 0.4% RC (HK$12.5=1mi). Use other cards for better rates."
        elif category in ["Travel Booking (Designated OTA)", "EveryMile Designated Everyday"]:
            rate = 2.0
            notes = "EveryMile designated merchant: HK$2=1 mile."
        # DELTA: Overseas (Physical) now has promo threshold and cap (cite: 13, 14, 15, 16)
        elif category == "Overseas (Physical)":
            # Overseas Promo Threshold (Jan-Mar 2026 Phase)
            if amount >= 12000:
                # Max spend for the extra 1.5% RC is 15000 (cap $225 RC)
                bonus_eligible_amount = min(amount, 15000)
                # Base 1% RC = 1 RC per 100 = 20 miles per 100 = HK$5=1mi
                # Bonus 1.5% RC = 1.5 RC per 100 = 30 miles per 100 = HK$3.333=1mi
                miles_from_bonus_portion = bonus_eligible_amount * (0.01 + 0.015) * 20 # Total 2.5% RC
                miles_from_base_portion = (amount - bonus_eligible_amount) * 0.01 * 20 # Base 1% RC for excess
                miles = miles_from_bonus_portion + max(0, miles_from_base_portion)
                rate = amount / miles if miles > 0 else 0
                notes = f"Overseas Promo Triggered: First HK${bonus_eligible_amount:.2f} earns HK$2/mi effective, excess HK${max(0, amount - bonus_eligible_amount):.2f} earns HK$5/mi."
            else:
                rate = 5.0
                notes = "Did not meet HK$12k overseas threshold. Base HK$5=1mi applied."
        # DELTA: Overseas (Online) excluded from Travel Guru bonuses, earns base 1% RC (cite: 6, 7)
        elif category == "Overseas (Online)":
            rate = 5.0
            notes = "Overseas (Online) earns base 1% RC (HK$5=1mi), excluded from Travel Guru bonuses."
        else:
            # This 'else' covers: Cathay Pacific Flights, HK Express Flights, Other Airlines (Direct Booking), Other Airlines (via OTA), Travel Booking (Non-Designated OTA), Hotels (Direct Booking), Ride-Hailing (Uber/Taxi Apps), Cathay Partner Dining, Dining (Premium), Dining (Casual), Food Delivery, Shopping (Designated 8%), Online General, Shopping (In-Store General)
            rate = 5.0
            notes = "General rate: HK$5=1 mile."

        miles = amount / rate if rate > 0 else 0

    # ══════════════════════════════════════════════════
    # HSBC RED MASTERCARD
    # 1 RC = 10 Miles
    # ══════════════════════════════════════════════════
    elif card == "HSBC Red Mastercard":
        # DELTA: E-wallets nerfed to zero (cite: 4, 9, 10)
        if category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            miles = 0.0
            notes = "Excluded: PayMe and other e-wallets no longer earn RewardCash as of July 2025."
        # DELTA: Supermarkets, Insurance/Utilities/Tax, Online Bill Payment, Octopus AAVS earn 0.4% RC (HK$25=1mi) (cite: 3, 4, 8, 11, 13, 14, 18)
        elif category in ["Supermarkets", "Insurance / Utilities / Tax", "Online Bill Payment (e-Banking)", "Octopus AAVS"]:
            rate = 25.0
            miles = amount / rate
            notes = "Low-earn: 0.4% RC (HK$25=1mi). Use other cards for better rates."
        # DELTA: Shopping (Designated 8%) cap of HK$1,250 monthly (cite: 3, 11)
        elif category == "Shopping (Designated 8%)":
            if amount <= 1250:
                rate = 1.25 # 8% RC
                miles = amount / rate
                notes = "8% rebate applied (HK$1.25=1mi)."
            else:
                miles = (1250 / 1.25) + ((amount - 1250) / 25.0)
                rate = amount / miles
                notes = f"WARNING: 8% cap (HK$1,250) exceeded. First HK$1,250 earns HK$1.25=1mi, excess HK${amount-1250:.2f} earns base 0.4% (HK$25=1mi)."
        # DELTA: Online General, Food Delivery, OTA, Ride-Hailing, Overseas (Online) cap of HK$10,000 monthly (cite: 3, 4, 7, 8)
        elif category in ["Online General", "Food Delivery", "Travel Booking (Non-Designated OTA)", "Travel Booking (Designated OTA)", "Ride-Hailing (Uber/Taxi Apps)", "Overseas (Online)"]:
            if amount <= 10000:
                rate = 2.5 # 4% RC
                miles = amount / rate
                notes = "4% online rebate applied (HK$2.5=1mi)."
                if category == "Ride-Hailing (Uber/Taxi Apps)":
                    notes += " +20mi/ride via Cathay partnership!"
            else:
                miles = (10000 / 2.5) + ((amount - 10000) / 25.0)
                rate = amount / miles
                notes = f"WARNING: 4% cap (HK$10K) exceeded. First HK$10,000 earns HK$2.5=1mi, excess HK${amount-10000:.2f} earns base 0.4% (HK$25=1mi)."
                if category == "Ride-Hailing (Uber/Taxi Apps)":
                    notes += " +20mi/ride via Cathay partnership!"
        else:
            # This 'else' covers: Cathay Pacific Flights, HK Express Flights, Other Airlines (Direct Booking), Other Airlines (via OTA), Hotels (Direct Booking), EveryMile Designated Everyday, Cathay Partner Dining, Dining (Premium), Dining (Casual), Shopping (In-Store General), Overseas (Physical)
            rate = 25.0 # DELTA: Base 0.4% for dining, in-store general, physical overseas (cite: 3)
            notes = "Base 0.4% earn rate."
            miles = amount / rate

    # ══════════════════════════════════════════════════
    # HSBC VISA SIGNATURE
    # 1 RC = 10 Miles. Assumes Red Hot Rewards category = DINING
    # ══════════════════════════════════════════════════
    elif card == "HSBC VISA Signature":
        # DELTA: E-wallets nerfed to zero (cite: 4, 9, 10)
        if category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            miles = 0.0
            notes = "Excluded: PayMe and other e-wallets no longer earn RewardCash as of July 2025."
        # DELTA: Food Delivery, Supermarkets, Insurance/Utilities/Tax, Online Bill Payment, Octopus AAVS earn 0.4% RC (HK$25=1mi) (cite: 5, 8, 12, 13, 14, 18)
        elif category in ["Food Delivery", "Supermarkets", "Insurance / Utilities / Tax", "Online Bill Payment (e-Banking)", "Octopus AAVS"]:
            rate = 25.0
            miles = amount / rate
            notes = "Low-earn: 0.4% RC (HK$25=1mi). Explicitly bypasses Red Hot Dining for Food Delivery."
        # DELTA: Dining categories have an annual HK$100,000 cap for 3.6% RC (cite: 12)
        elif category in ["Dining (Premium)", "Dining (Casual)", "Cathay Partner Dining"]:
            # DELTA: The delta report's rule implies if a single transaction exceeds 100k, it drops to base.
            # This is an interpretation for a single 'amount' parameter in a function designed for cumulative annual caps.
            if amount <= 100000: # Assuming this transaction does not exceed the annual cap
                rate = 2.78 # 3.6% RC (9X)
                miles = amount / rate
                notes = "3.6% Red Hot Rewards (Dining). *Assumes user has not exceeded HK$100K annual category cap.* B1G1 at Michelin restaurants."
            else:
                # If a single transaction is > 100k, it's likely the entire transaction falls to base or only 100k gets bonus.
                # Following the delta report's explicit rule for the 'amount' parameter.
                rate = 25.0 # Drops to base 0.4% if annual cap exceeded by this transaction
                miles = amount / rate
                notes = "WARNING: HK$100K annual cap for Red Hot Rewards (Dining) exceeded by this transaction. Base 0.4% (HK$25=1mi) applied."
        # DELTA: Overseas (Physical) earns 1.6% RC (HK$6.25=1mi) (cite: 6, 7)
        elif category in ["Overseas (Physical)"]:
            rate = 6.25
            miles = amount / rate
            notes = "Overseas (Physical) earns 1.6% RC (HK$