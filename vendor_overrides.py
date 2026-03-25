"""
Vendor Overrides Registry
=========================
Maps specific vendor names to their verified spending category,
bypassing generic Gemini AI guessing. This ensures vendors with
non-obvious MCC classifications (e.g., Uber coding as online
e-commerce despite being ride-hailing) are routed correctly.

To add a new override:
  1. Research the vendor's actual MCC code and how each card treats it.
  2. Add the vendor (lowercase) as a key with its correct category as value.
  3. Optionally add a note explaining the rationale.

Usage:
  from vendor_overrides import get_vendor_override
  override = get_vendor_override("uber")
  if override:
      category = override  # Use verified category instead of AI guess
"""

# Vendor name (lowercase) → verified category
# Each entry should be backed by statement verification or MCC research
VENDOR_OVERRIDES = {
    # ─── Ride-Hailing ────────────────────────────────────────
    # Uber charges via overseas entities (Uber BV, Netherlands).
    # HSBC treats as online e-commerce → Red 4% applies.
    # NOT on EveryMile designated transport list.
    # Source: uber-hk-asia-miles-report.md
    "uber": "Ride-Hailing (Uber/Taxi Apps)",
    "uber taxi": "Ride-Hailing (Uber/Taxi Apps)",
    "uber hk": "Ride-Hailing (Uber/Taxi Apps)",
    "hktaxi": "Ride-Hailing (Uber/Taxi Apps)",
    "didi": "Ride-Hailing (Uber/Taxi Apps)",

    # ─── EveryMile Designated Transport ──────────────────────
    # These ARE on EveryMile's designated merchant list → HK$2/mi
    "syncab": "EveryMile Designated Everyday",
    "dash": "EveryMile Designated Everyday",
    "joie": "EveryMile Designated Everyday",
    "amigo": "EveryMile Designated Everyday",
    "big bee": "EveryMile Designated Everyday",

    # ─── EveryMile Designated Cafes ──────────────────────────
    "starbucks": "EveryMile Designated Everyday",
    "pacific coffee": "EveryMile Designated Everyday",
    "pret a manger": "EveryMile Designated Everyday",
    "blue bottle": "EveryMile Designated Everyday",
    "blue bottle coffee": "EveryMile Designated Everyday",
    "lady m": "EveryMile Designated Everyday",
    "tea wg": "EveryMile Designated Everyday",
    "green common": "EveryMile Designated Everyday",
    "noc": "EveryMile Designated Everyday",
    "noc coffee": "EveryMile Designated Everyday",

    # ─── EveryMile Designated Transport ──────────────────────
    "mtr": "EveryMile Designated Everyday",
    "kmb": "EveryMile Designated Everyday",
    "citybus": "EveryMile Designated Everyday",
    "first bus": "EveryMile Designated Everyday",

    # ─── Food Delivery (NOT Dining — MCC 5814) ───────────────
    "keeta": "Food Delivery",
    "foodpanda": "Food Delivery",
    "deliveroo": "Food Delivery",

    # ─── Cathay Partner Dining ───────────────────────────────
    "elephant grounds": "Cathay Partner Dining",
    "la rambla": "Cathay Partner Dining",
    "morty's": "Cathay Partner Dining",
    "the diplomat": "Cathay Partner Dining",

    # ─── HSBC Red Designated 8% ──────────────────────────────
    "sushiro": "Shopping (Designated 8%)",
    "tamjai samgor": "Shopping (Designated 8%)",
    "tamjai yunnan": "Shopping (Designated 8%)",
    "the coffee academics": "Shopping (Designated 8%)",
    "gu": "Shopping (Designated 8%)",
    "decathlon": "Shopping (Designated 8%)",
    "lululemon": "Shopping (Designated 8%)",
    "namco": "Shopping (Designated 8%)",
    "taito station": "Shopping (Designated 8%)",

    # ─── Travel (Designated OTA on EveryMile) ────────────────
    "klook": "Travel Booking (Designated OTA)",
    "kkday": "Travel Booking (Designated OTA)",

    # ─── Travel (Non-Designated OTA) ─────────────────────────
    "trip.com": "Travel Booking (Non-Designated OTA)",
    "expedia": "Travel Booking (Non-Designated OTA)",
    "agoda": "Travel Booking (Non-Designated OTA)",
    "booking.com": "Travel Booking (Non-Designated OTA)",
    "hotels.com": "Travel Booking (Non-Designated OTA)",
    "makemytrip": "Travel Booking (Non-Designated OTA)",
    "pelago": "Travel Booking (Non-Designated OTA)",

    # ─── Airlines (Direct) ───────────────────────────────────
    "cathay pacific": "Cathay Pacific Flights",
    "cathay": "Cathay Pacific Flights",
    "hk express": "HK Express Flights",

    # ─── Online Shopping ─────────────────────────────────────
    "amazon": "Online General",
    "taobao": "Online General",
    "hktvmall": "Online General",
    "zalora": "Online General",
    "asos": "Online General",
    "shopee": "Online General",
    "lazada": "Online General",
}


def get_vendor_override(vendor_name: str):
    """
    Check if a vendor has a verified category override.
    Returns the correct category string, or None if no override exists.
    Matching is case-insensitive and tries partial matching.
    """
    if not vendor_name:
        return None

    vendor_lower = vendor_name.strip().lower()

    # Exact match first
    if vendor_lower in VENDOR_OVERRIDES:
        return VENDOR_OVERRIDES[vendor_lower]

    # Partial match: check if any override key is contained in the vendor name
    for key, category in VENDOR_OVERRIDES.items():
        if key in vendor_lower or vendor_lower in key:
            return category

    return None
