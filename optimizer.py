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
]


def calculate_miles(card, category, amount):
    """
    Calculates the Asia Miles earned for a specific card, category, and amount.
    All rates sourced from Cathay_Data_v1.2.md.
    Returns (miles_earned, effective_rate_hks_per_mile, notes)
    """
    miles = 0.0
    rate = 0.0
    notes = ""

    # ══════════════════════════════════════════════════
    # STANDARD CHARTERED CATHAY MASTERCARD
    # ══════════════════════════════════════════════════
    if card == "Standard Chartered Cathay Mastercard":
        if category in ["Cathay Pacific Flights", "HK Express Flights"]:
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
        elif category == "Octopus AAVS":
            rate = 6.0
            notes = "Automatic monthly conversion. Passive earning, zero effort."
        elif category == "Ride-Hailing (Uber/Taxi Apps)":
            rate = 6.0
            notes = "HK$6=1mi. TIP: Link Cathay in Uber app for +20mi/ride (+40mi airport) on top!"
        else:
            # Food Delivery, Online General, Shopping, OTA bookings, EveryMile Designated = all HK$6
            rate = 6.0
            notes = "Other local spending: HK$6=1 mile."

        miles = amount / rate if rate > 0 else 0

    # ══════════════════════════════════════════════════
    # HSBC EVERYMILE VISA
    # 1 RC = 20 Miles (best HSBC conversion)
    # ══════════════════════════════════════════════════
    elif card == "HSBC EveryMile VISA":
        if category in ["Travel Booking (Designated OTA)", "EveryMile Designated Everyday"]:
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
        if category == "Shopping (Designated 8%)":
            # 8% RC → 8 RC per $100 → 80 miles per $100 → HK$1.25 = 1 mile
            rate = 1.25
            notes = "8% rebate (first HK$1,250/month). Merchants: GU, Decathlon, lululemon, Sushiro, TamJai."
            miles = amount / rate
        elif category in ["Online General", "Food Delivery",
                          "Travel Booking (Non-Designated OTA)", "Other Airlines (via OTA)",
                          "Travel Booking (Designated OTA)",
                          "Ride-Hailing (Uber/Taxi Apps)"]:
            # 4% RC → 4 RC per $100 → 40 miles per $100 → HK$2.5 = 1 mile
            # Uber processed overseas as online e-commerce; Red 4% captures it
            rate = 2.5
            if category == "Ride-Hailing (Uber/Taxi Apps)":
                notes = "4% online (Uber coded as online e-commerce). +20mi/ride via Cathay partnership!"
            else:
                notes = "4% online rebate (first HK$10K/month). MCC 4722 OTA captured."
            miles = amount / rate
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
        if category in ["Dining (Premium)", "Dining (Casual)", "Cathay Partner Dining"]:
            # 3.6% RC → 3.6 RC per $100 → 36 miles per $100 → HK$2.78 = 1 mile
            rate = 2.78
            notes = "3.6% Red Hot Rewards (Dining). B1G1 at Michelin restaurants."
            miles = amount / rate
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
