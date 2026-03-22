import os
import json
import base64
import requests
from typing import Dict, Any
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables (override allows hot-reloading if users change .env)
load_dotenv(override=True)

# The mapped categories that exist in our rules engine (v1.2)
VALID_CATEGORIES = [
    "Cathay Pacific Flights",
    "HK Express Flights",
    "Other Airlines (Direct Booking)",
    "Other Airlines (via OTA)",
    "Travel Booking (Designated OTA)",
    "Travel Booking (Non-Designated OTA)",
    "EveryMile Designated Everyday",
    "Cathay Partner Dining",
    "Dining (Premium)",
    "Dining (Casual)",
    "Food Delivery",
    "Shopping (Designated 8%)",
    "Online General",
    "Shopping (In-Store General)",
    "Octopus AAVS",
    "Overseas"
]

def parse_transaction_image(image) -> Dict[str, Any]:
    """
    Passes the PIL Image to Gemini Flash via REST API to extract vendor, amount, and best-fit category.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        return {"error": "API Key is missing. Please populate the .env file."}

    prompt = f"""
    You are an expert financial assistant specializing in Hong Kong credit card rewards.
    Analyze this transaction receipt, checkout screenshot, or bill.

    Extract the following details:
    1. 'vendor': The merchant or vendor name. Provide a short, clean name (e.g., "Klook", "Starbucks", "Cathay Pacific").
    2. 'amount': The transaction total amount in HKD as a float. Do not include currency symbols. If it's a foreign currency, extract the raw numeric total anyway.
    3. 'category': The best matching category from the following exact list. You MUST choose exactly one string from this array:
    {json.dumps(VALID_CATEGORIES)}

    Category Decision Logic (CRITICAL — follow strictly):

    FLIGHTS:
    - Cathay Pacific booked on cathay.com or Cathay app → "Cathay Pacific Flights"
    - HK Express booked on hkexpress.com or UO app → "HK Express Flights"
    - Any airline booked DIRECT on the airline's own website (Air India, Indigo, JAL, SQ, etc.) → "Other Airlines (Direct Booking)"
    - Any airline booked via OTA (Trip.com, Expedia, MakeMyTrip, Skyscanner) → "Other Airlines (via OTA)"

    TRAVEL / EXPERIENCES:
    - Klook, KKday → "Travel Booking (Designated OTA)"
    - Trip.com, Expedia, Agoda, Booking.com, Hotels.com, Pelago, Kayak, MakeMyTrip → "Travel Booking (Non-Designated OTA)"

    EVERYDAY (CAFES / TRANSPORT):
    - Starbucks, Pacific Coffee, Pret A Manger, Blue Bottle, Lady M, Tea WG, Green Common, NOC → "EveryMile Designated Everyday"
    - MTR, KMB, Citybus, First Bus, taxi apps (SynCab, Dash, Joie) → "EveryMile Designated Everyday"
    - AVIS, Hertz, Tesla SuperCharger → "EveryMile Designated Everyday"

    DINING:
    - Elephant Grounds, La Rambla, Morty's, The Diplomat, East Hotel restaurants → "Cathay Partner Dining"
    - Michelin-starred or fine dining (Amber, TATE, Écriture, etc.) or bill > HK$800 → "Dining (Premium)"
    - Regular restaurant bill → "Dining (Casual)"

    FOOD DELIVERY:
    - Keeta, Foodpanda, Deliveroo → "Food Delivery" (NOT dining — MCC 5814)

    SHOPPING:
    - GU, Decathlon, lululemon, Sushiro, TamJai SamGor, TamJai Yunnan, The Coffee Academics, NAMCO, TAITO STATION → "Shopping (Designated 8%)"
    - Amazon, Taobao, HKTVmall, Zalora, ASOS, Shopee, Lazada, AEON online → "Online General"
    - Uniqlo, M&S, or any in-store retail not listed above → "Shopping (In-Store General)"

    OTHER:
    - Octopus top-up or AAVS → "Octopus AAVS"
    - Foreign currency transaction or overseas merchant → "Overseas"

    Return the response as a valid JSON object:
    {{
      "vendor": "String",
      "amount": Float,
      "category": "String"
    }}
    Ensure your output is pure, unformatted JSON with no markdown wrapping.
    """

    # Convert PIL Image to Base64
    buffered = BytesIO()
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": img_str
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.0,
            "responseMimeType": "application/json"
        }
    }

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": api_key
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            error_msg = response.text
            if "User location is not supported" in error_msg:
                return {"error": "Google Gemini API is geo-blocked. Make sure your VPN is routing Terminal/Python traffic!"}
            if "not found" in error_msg:
                return {"error": f"Model not found via API. Raw: {error_msg}"}
            return {"error": f"API Error {response.status_code}: {error_msg}"}

        data = response.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        result = json.loads(raw_text)

        # Validation Fallback
        if result.get("category") not in VALID_CATEGORIES:
            result["category"] = "Shopping (In-Store General)"

        return result
    except json.JSONDecodeError:
        return {"error": "Failed to decode Gemini response into JSON."}
    except Exception as e:
        return {"error": str(e)}
