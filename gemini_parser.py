import os
import json
import base64
import requests
from typing import Dict, Any
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables (override allows hot-reloading if users change .env)
load_dotenv(override=True)

# The mapped categories that exist in our rules engine
VALID_CATEGORIES = [
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

def parse_transaction_image(image) -> Dict[str, Any]:
    """
    Passes the PIL Image to Gemini 1.5 Flash via REST API to extract vendor, amount, and best-fit category in strict JSON.
    This bypasses protobuf environment issues completely.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        return {"error": "API Key is missing. Please populate the .env file."}

    prompt = f"""
    You are an expert financial assistant. Analyze this transaction receipt, checkout screenshot, or bill.
    Extract the following details:
    1. 'vendor': The merchant or vendor name. Provide a short, clean name (e.g., if it says Klook Hong Kong, just return Klook).
    2. 'amount': The transaction total amount in HKD as a float. Do not include currency symbols. If it's a foreign currency, extract the raw numeric total anyway.
    3. 'category': The best matching category for this transaction from the following exact list. You MUST choose exactly one string from this array:
    {json.dumps(VALID_CATEGORIES)}
    
    Category Guessing Logic:
    - If the merchant is Klook, Agoda, or Expedia use 'Travel Booking (Klook/Agoda)'.
    - If the merchant is Keeta, Foodpanda or Deliveroo, use 'Food Delivery'.
    - If it's a restaurant bill, use 'Dining (Casual)' or 'Dining (Premium)' depending on the apparent cost/prestige.
    - If it's Cathay Pacific flights, use 'Cathay Pacific Flights'.
    - If it's an online store like Taobao or Amazon, use 'Online General'.
    - If it's an in-store shop like Uniqlo or M&S, use 'Shopping (In-Store General)'.
    
    Return the response as a valid JSON object matching this schema:
    {{
      "vendor": "String",
      "amount": Float,
      "category": "String"
    }}
    Ensure your output is pure, unformatted JSON with no markdown wrapping (no ```json).
    """

    # Convert PIL Image to Base64
    buffered = BytesIO()
    # Convert image format if necessary (some screenshots are RGBA/PNG)
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
                     