import math

# Credit Card Definitions
CARDS = [
    "Standard Chartered Cathay Mastercard",
    "HSBC EveryMile VISA",
    "HSBC Red Mastercard",
    "HSBC VISA Signature",
]

# DELTA: Updated CATEGORIES list to include new splits and exclusions (cite: 7A)
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
    "Overseas (Physical In-Store)",         # DELTA: Split to handle Travel Guru (cite: 2, 7A)
    "Overseas (Online)",                    # DELTA: Split to handle Travel Guru (cite: 2, 7A)
    "Supermarkets",
    "Hospital / Medical",                   # DELTA: New exclusion handling (cite: 2, 7A)
    "Education Fees",                       # DELTA: New exclusion handling (cite: 2, 7A)
    "Utilities (Direct)",                   # DELTA: Separated from Tax/Insurance (cite: 2, 7A)
    "Insurance / Tax",                      # DELTA: Renamed/Split (cite: 2, 7A)
    "E-Wallets (PayMe/Alipay/WeChat)",
    "Rent (via RentSmart/CardUp)"           # DELTA: New category (cite: 2, 7A)
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
        # DELTA: E-wallets completely excluded (cite: 3, 19, 20)
        # DELTA: Hospitals, Education, Utilities excluded as of Sep 2024 (cite: 1, 2, 3, 18)
        if category in ["E-Wallets (PayMe/Alipay/WeChat)", "Hospital / Medical", "Education Fees", "Utilities (Direct)"]:
            rate = 0.0
            notes = "Excluded: Strictly excluded from earning Asia Miles by Standard Chartered terms (Sep 2024 update)."
            miles = 0.0
        elif category in ["Cathay Pacific Flights", "HK Express Flights"]:
            rate = 2.0
            notes = "Direct earn HK$2=1mi. +2,667 bonus miles per HK$8K/quarter."
        elif category == "Cathay Partner Dining":
            rate = 2.0  # HK$4 = 2 miles → effective HK$2 per mile
            notes = "Cathay Partner exclusive: HK$4=2 miles. Check dining.cathaypacific.com."
        # DELTA: HK$4/mi is strictly for Dining, Hotels, Overseas, and Food Delivery (cite: 1, 5, 6)
        elif category in ["Dining (Premium)", "Dining (Casual)", "Food Delivery", "Overseas (Physical In-Store)", "Overseas (Online)"]:
            rate = 4.0
            notes = "Eligible Dining, Food Delivery, and Foreign Currency spend earns HK$4=1 mile."
        elif category == "Other Airlines (Direct Booking)":
            rate = 4.0
            notes = "Direct airline booking (MCC 3000-3350) = overseas rate HK$4=1mi (if foreign currency)."
        # DELTA: Online General, Non-Designated OTA, Ride-Hailing are NOT HK$4/mi. They are HK$6/mi (cite: 1, 6)
        # DELTA: Supermarkets, Insurance/Tax, Rent (via RentSmart/CardUp) also fall to base rate (cite: 1, 2, 5, 6)
        elif category in ["Octopus AAVS", "Online General", "Travel Booking (Non-Designated OTA)", "Ride-Hailing (Uber/Taxi Apps)", "Supermarkets", "Insurance / Tax", "Rent (via RentSmart/CardUp)"]:
            rate = 6.0
            notes = "Base local HKD rate of HK$6=1 mile. (RentSmart promos also guarantee HK$6/mi)."
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
        # DELTA: PayMe/E-wallets nerfed to zero effective July 1, 2025 (cite: 3, 4)
        if category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            notes = "Excluded: PayMe and e-wallets no longer earn RewardCash effective July 2025."
            miles = 0.0
        # DELTA: Penalized categories earning base 0.4% RC (HK$12.5=1mi) (cite: 2, 3, 15, 16)
        elif category in ["Supermarkets", "Hospital / Medical", "Education Fees", "Utilities (Direct)", "Insurance / Tax"]:
            rate = 12.5
            notes = "MAJOR EXCLUSION: Category earns only base 0.4% RC (HK$12.5=1mi)."
        elif category in ["Travel Booking (Designated OTA)", "EveryMile Designated Everyday"]:
            # Klook, KKday, Starbucks, MTR, KMB, Pacific Coffee, etc.
            rate = 2.0
            notes = "EveryMile designated merchant (Agoda, cafes, transport): HK$2=1 mile."
        # DELTA: Overseas split into Physical and Online, notes updated for Travel Guru (cite: 2, 9, 10, 17, 22)
        elif category == "Overseas (Physical In-Store)":
            rate = 2.0
            notes = "Overseas HK$2=1mi IF HK$12K promo threshold met. **TRAVEL GURU BONUS:** Can reach HK$0.59/mi if GURU tier!"
        elif category == "Overseas (Online)":
            rate = 2.0
            notes = "Overseas HK$2=1mi IF HK$12K promo threshold met. (Excluded from Travel Guru physical bonuses)."
        elif category == "Octopus AAVS":
            # Special low-earn: 1 RC per HK$250, × 20 miles = HK$12.5 per mile
            rate = 12.5
            notes = "AAVS low-earn: 1RC/HK$250 (×20mi) = HK$12.5/mi. SC Cathay is far better at HK$6/mi."
        # DELTA: Rent (via RentSmart/CardUp) earns general rate (cite: 2)
        elif category == "Rent (via RentSmart/CardUp)":
            rate = 5.0
            notes = "General rate: HK$5=1 mile."
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
        # DELTA: PayMe/E-wallets nerfed to zero effective July 1, 2025 (cite: 3, 4)
        if category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            miles = 0.0
            notes = "Excluded: PayMe and e-wallets no longer earn RewardCash effective July 2025."
        # DELTA: Supermarkets, Hospitals, Education, Utilities, Insurance/Tax, Rent earn 0.4% RC (cite: 2, 13, 14, 15, 16, 18)
        elif category in ["Supermarkets", "Hospital / Medical", "Education Fees", "Utilities (Direct)", "Insurance / Tax", "Rent (via RentSmart/CardUp)"]:
            rate = 25.0
            miles = amount / rate
            notes = "Earns 0.4% base rate (HK$25=1mi)."
        elif category == "Shopping (Designated 8%)":
            # DELTA: Implement HK$1,250 monthly cap for 8% rebate (cite: 4, 11, 12)
            if amount <= 1250:
                rate = 1.25
                miles = amount / rate
                notes = "8% rebate applied (HK$1.25=1mi) at designated merchants (e.g., Sushiro, GU)."
            else:
                base_miles = 1250 / 1.25
                excess_miles = (amount - 1250) / 25.0  # Reverts to 0.4% base
                miles = base_miles + excess_miles
                rate = amount / miles  # Blended effective rate
                notes = f"WARNING: 8% cap (HK$1,250) exceeded. First HK$1,250 earns HK$1.25=1mi, excess HK${amount-1250:.2f} earns base 0.4% (HK$25=1mi)."
        # DELTA: Online General, Food Delivery, OTA, Ride-Hailing, Overseas (Online) now under 4% online rebate (cite: 4, 7, 8, 11, 13)
        elif category in ["Online General", "Food Delivery",
                          "Travel Booking (Non-Designated OTA)", "Travel Booking (Designated OTA)",
                          "Ride-Hailing (Uber/Taxi Apps)", "Overseas (Online)"]:
            # DELTA: Implement HK$10,000 monthly cap for 4% online rebate (cite: 4, 7, 8, 11, 13)
            if amount <= 10000:
                rate = 2.5
                miles = amount / rate
                notes = "4% online rebate applied (HK$2.5=1mi)."
            else:
                base_miles = 10000 / 2.5
                excess_miles = (amount - 10000) / 25.0
                miles = base_miles + excess_miles
                rate = amount / miles
                notes = f"WARNING: 4% cap (HK$10K) exceeded. First HK$10,000 earns HK$2.5=1mi, excess HK${amount-10000:.2f} earns base 0.4% (HK$25=1mi)."
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
        # DELTA: PayMe/E-wallets nerfed to zero effective July 1, 2025 (cite: 3, 4)
        if category == "E-Wallets (PayMe/Alipay/WeChat)":
            rate = 0.0
            miles = 0.0
            notes = "Excluded: PayMe and e-wallets no longer earn RewardCash effective July 2025."
        # DELTA: Supermarkets, Hospitals, Education, Utilities, Insurance/Tax, Rent earn 0.4% RC (cite: 2, 13, 14, 15, 16, 18)
        elif category in ["Supermarkets", "Hospital / Medical", "Education Fees", "Utilities (Direct)", "Insurance / Tax", "Rent (via RentSmart/CardUp)"]:
            rate = 25.0
            miles = amount / rate
            notes = "Non-bonus/bill payment earns 0.4% base rate (HK$25=1mi)."
        # DELTA: Food Delivery added to 3.6% Red Hot Rewards (Dining) (cite: 6, 12, 14, 21, 28)
        elif category in ["Dining (Premium)", "Dining (Casual)", "Cathay Partner Dining", "Food Delivery"]:
            rate = 2.78
            miles = amount / rate
            notes = "3.6% Red Hot Rewards (Dining). Foodpanda qualifies; other delivery apps may default to 0.4%. Cap: HK$100K/yr."
        # DELTA: Overseas split into Physical and Online, notes updated for Travel Guru (cite: 2, 10, 17, 26)
        elif category == "Overseas (Physical In-Store)":
            rate = 6.25  # Assumes user chose Dining for 5X.
            miles = amount / rate
            notes = "1.6% base for non-chosen categories. IF user chose Overseas 5X, rate is HK$2.78/mi (up to 9.6% RC with Travel Guru)."
        elif category == "Overseas (Online)":
            rate = 6.25
            miles = amount / rate
            notes = "1.6% base for non-chosen categories. (Excluded from Travel Guru physical bonuses)."
        elif category == "Octopus AAVS":
            # AAVS is special low-earn on VISA Sig: base 0.4% = HK$25 per mile
            rate = 25.0
            notes = "AAVS low-earn category: base 0.4% = HK$25/mi. Use SC Cathay instead."
            miles = amount / rate
        else:
            # 1.6% RC → 1.6 RC per $100 → 16 miles per $100 → HK$6.25 = 1 mile
            rate = 6.25
            notes = "1.6% base for non-5X categories."
            miles = amount / rate

    # DELTA GLOBAL RULE: Universal Uber x Cathay Partnership Addition (cite: 2, 5, 7, 8, 23, 24)
    if category == "Ride-Hailing (Uber/Taxi Apps)":
        # DELTA: Uber bonus is card-agnostic, applies to all cards (cite: 5, 7, 8, 23, 24)
        notes += " [GLOBAL BONUS: Link Cathay app to Uber to earn a direct +20 Miles per ride (+40 for airport), regardless of card used!]"

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
# PATCH_SUMMARY: {"changes": ["Updated CATEGORIES list with new splits and exclusions", "Standard Chartered Cathay Mastercard: 'Online General', 'Travel Booking (Non-Designated OTA)', 'Ride-Hailing (Uber/Taxi Apps)' rates changed from HK$4 to HK$6", "Standard Chartered Cathay Mastercard: 'Hospital / Medical', 'Education Fees', 'Utilities (Direct)', 'E-Wallets (PayMe/Alipay/WeChat)' set to 0 miles", "Standard Chartered Cathay Mastercard: 'Rent (via RentSmart/CardUp)' added at HK$6/mi", "Standard Chartered Cathay Mastercard: 'Overseas' split into 'Overseas (Physical In-Store)' and 'Overseas (Online)'", "HSBC EveryMile VISA: 'E-Wallets (PayMe/Alipay/WeChat)' set to 0 miles", "HSBC EveryMile VISA: 'Supermarkets', 'Hospital / Medical', 'Education Fees', 'Utilities (Direct)', 'Insurance / Tax' explicitly set to HK$12.5/mi", "HSBC EveryMile VISA: 'Overseas' split into 'Overseas (Physical In-Store)' and 'Overseas (Online)', notes updated for Travel Guru", "HSBC EveryMile VISA: 'Rent (via RentSmart/CardUp)' added at HK$5/mi", "HSBC Red Mastercard: 'E-Wallets (PayMe/Alipay/WeChat)' set to 0 miles", "HSBC Red Mastercard: 'Supermarkets', 'Hospital / Medical', 'Education Fees', 'Utilities (Direct)', 'Insurance / Tax', 'Rent (via RentSmart/CardUp)' explicitly set to HK$25/mi", "HSBC Red Mastercard: 'Shopping (Designated 8%)' and 'Online General' (etc.) cap logic confirmed/re-implemented with notes", "HSBC Red Mastercard: 'Overseas (Online)' added to 4% online rebate category", "HSBC VISA Signature: 'E-Wallets (PayMe/Alipay/WeChat)' set to 0 miles", "HSBC VISA Signature: 'Supermarkets', 'Hospital / Medical', 'Education Fees', 'Utilities (Direct)', 'Insurance / Tax', 'Rent (via RentSmart/CardUp)' explicitly set to HK$25/mi", "HSBC VISA Signature: 'Food Delivery' added to 3.6% dining category", "HSBC VISA Signature: 'Overseas' split into 'Overseas (Physical In-Store)' and 'Overseas (Online)', notes updated for Travel Guru", "Global: 'Ride-Hailing (Uber/Taxi Apps)' note updated to include universal Uber x Cathay bonus"], "categories_added": ["Hospital / Medical", "Education Fees", "Utilities (Direct)", "Rent (via RentSmart/CardUp)", "Overseas (Physical In-Store)", "Overseas (Online)"], "rates_changed": 9}