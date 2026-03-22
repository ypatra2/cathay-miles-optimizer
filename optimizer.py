import math

# Credit Card Definitions and Base Earn Rates (HK$ per 1 Mile)
# Note: Lower is better (fewer HK$ needed to earn 1 mile)

CARDS = [
    "Standard Chartered Cathay Mastercard",
    "HSBC EveryMile VISA",
    "HSBC Red Mastercard",
    "HSBC VISA Signature",
]

def calculate_miles(card, category, amount, is_partner_promo=False):
    """
    Calculates the Asia Miles earned for a specific card, category, and amount.
    Returns (miles_earned, effective_rate_hks_per_mile, notes)
    """
    miles = 0.0
    rate = 0.0
    notes = ""

    if card == "Standard Chartered Cathay Mastercard":
        if category in ["Cathay Pacific Flights", "HK Express Flights"]:
            rate = 2.0
            notes = "Direct earn + 10% award redemption discount."
        elif is_partner_promo and category in ["Dining (Casual)", "Food Delivery"]:
            rate = 2.0
            notes = "Cathay Partner Promo applied (HK$4=2 miles)."
        elif category in ["Dining (Casual)", "Dining (Premium)", "Overseas", "Online General"]:
            # Note: The database says HK$4=1 Mile for Dining/Online/Overseas
            rate = 4.0
        elif category == "Octopus AAVS":
            rate = 6.0
            notes = "Automatic mileage conversion."
        else:
            rate = 6.0 # All other local spending
            
        miles = amount / rate if rate > 0 else 0

    elif card == "HSBC EveryMile VISA":
        # 1 RC = 20 Miles
        if category in ["Travel Booking (Klook/Agoda)", "Other Airlines", "Overseas"]:
            # If standard EveryMile designated, rate is HK$2=1 mile
            rate = 2.0
            notes = "Condition: requires HK$12,000+ total overseas spend for full overseas promo." if category == "Overseas" else "Designated travel/everyday spend."
        else:
            # General local/overseas
            rate = 5.0
        
        miles = amount / rate if rate > 0 else 0

    elif card == "HSBC Red Mastercard":
        # 1 RC = 10 Miles
        if category == "Shopping (Designated 8%)":
            # 8% RC -> 8 RC per $100 -> 80 Miles per $100 -> HK$1.25 = 1 Mile
            rate = 1.25
            notes = "8% RC equivalent. Capped at first HK$1,250/month."
            # calculate exact miles: 
            miles = amount / rate
        elif category in ["Online General", "Food Delivery"]:
            # 4% RC -> 4 RC per $100 -> 40 Miles per $100 -> HK$2.5 = 1 Mile
            rate = 2.5
            notes = "4% RC equivalent. Capped at first HK$10,000/month."
            miles = amount / rate
        else:
            # 0.4% RC -> 0.4 RC per $100 -> 4 Miles per $100 -> HK$25 = 1 Mile
            rate = 25.0
            notes = "Base 0.4% earn rate."
            miles = amount / rate

    elif card == "HSBC VISA Signature":
        # 1 RC = 10 Miles
        # Assuming Red Hot Rewards category is DINING
        if category in ["Dining (Premium)", "Dining (Casual)"]:
            # 3.6% RC -> 3.6 RC per $100 -> 36 Miles per $100 -> HK$2.78 = 1 Mile
            rate = 2.78
            notes = "Using Red Hot Rewards 3.6% in Dining. Good for Michelin promos."
            miles = amount / rate
        else:
            # Base 1.6% RC if selected category is dining but spend is general? No, base is 0.4% outside 5X category unless standard 1.6% applies.
            # Using 1.6% RC -> 1.6 RC per $100 -> 16 Miles per $100 -> HK$6.25 = 1 Mile
            rate = 6.25
            notes = "Assumes 1.6% RC rate for non-core Red Hot category."
            miles = amount / rate

    return math.floor(miles), round(rate, 2), notes

def get_recommendations(category, amount, is_partner_promo=False):
    results = []
    for card in CARDS:
        m, r, n = calculate_miles(card, category, amount, is_partner_promo)
        results.append({
            "card": card,
            "miles": m,
            "rate": r,
            "notes": n
        })
    
    # Sort by miles descending
    results.sort(key=lambda x: x['miles'], reverse=True)
    return results

CATEGORIES = [
    "Cathay Pacific Flights",
    "HK Express Flights",
    "Other Airlines",
    "Travel Booking (Klook/Agoda)",
    "Dining (Premium)",
    "Dining (Casual)",
    "Food Delivery",
    "Shopping (Designated 8%)",
    "Online General",
    "Shopping (In-Store General)",
    "Octopus AAVS",
    "Overseas"
]
