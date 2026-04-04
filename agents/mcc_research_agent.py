import os
import json
import requests
from typing import Dict, Any

from db_manager import save_mcc_mapping
from optimizer import CATEGORIES

def research_mcc_for_vendor(vendor_name: str, context: str = "") -> Dict[str, Any]:
    """
    Spins up a synchronous Gemini Pro agent to fetch factual MCC codes for a new vendor in Hong Kong 
    and map it to our internal CATEGORIES. It uses raw requests REST API to bypass Python protobuf issues.
    """
    print(f"\\n[MCC Research Agent] Initiating research for unknown vendor: '{vendor_name}'")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[MCC Research Agent] Error: Missing GEMINI_API_KEY.")
        return {"error": "Missing GEMINI_API_KEY for research agent."}
    
    system_instruction = f"""
    You are an elite Hong Kong credit card rewards analyst.
    Your job is to determine the Merchant Category Code (MCC) for a specific vendor in Hong Kong.
    You must intelligently map that MCC to ONE of the exact strings in our internal system CATEGORIES array:
    {json.dumps(CATEGORIES)}
    
    Instructions:
    1. Determine the predominant MCC associated with the vendor in Hong Kong. (e.g., Mannings is 5912).
    2. Determine if the vendor predominantly processes as "online" or "offline" in a retail context. If it is a hybrid major retailer (like Apple Store), output "both".
    3. Choose the absolute best match from the exact CATEGORIES array based on your MCC findings. If platform is "both", heavily weigh the User Context below to decide the specific category (e.g. Shopping (In-Store General) vs Online General).
    4. Provide a brief 1-sentence analytical reason based on factual internet knowledge.
    
    Return EXACTLY valid JSON with no markdown wrapping. Format:
    {{
      "mcc": "4 digit string or 'UNKNOWN'",
      "platform_type": "online" | "offline" | "both",
      "mapped_category": "Exact string from array",
      "reason": "String explaining the choice."
    }}
    """
    
    prompt = f"Vendor: {vendor_name}\\nUser Context describing the purchase: {context}\\nFind the Hong Kong MCC and credit card category mapping for this specific vendor!"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}"
    
    payload = {
        "system_instruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.1
        },
        "tools": [
            {
                "googleSearch": {}
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"[MCC Research Agent] API Error: {response.text}")
            raise Exception(f"API Error {response.status_code}")

        data = response.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        
        # Cleanup markdown formatting if GEMINI ignores responseMimeType
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            
        result = json.loads(raw_text)
        
        mcc = result.get("mcc", "UNKNOWN")
        platform_type = result.get("platform_type", "offline")
        mapped_category = result.get("mapped_category")
        reason = result.get("reason", "")
        
        # Guardrail
        if mapped_category not in CATEGORIES:
            print(f"[MCC Research Agent] Warning: Return invalid category '{mapped_category}'. Defaulting.")
            mapped_category = "Shopping (In-Store General)"
            
        print(f"[MCC Research Agent] Success! '{vendor_name}' is MCC {mcc} ({mapped_category}).")
        
        save_mcc_mapping(vendor_name, mcc, platform_type, mapped_category)
        
        return {
            "vendor": vendor_name,
            "category": mapped_category,
            "mcc_rationale": reason
        }

    except Exception as e:
        print(f"[MCC Research Agent] Failed: {e}")
        return {
            "vendor": vendor_name,
            "category": "Shopping (In-Store General)",
            "mcc_rationale": "Fallback applied due to Research Agent failure.",
            "error": str(e)
        }

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(override=True)
    res = research_mcc_for_vendor("Yakiniku Like")
    print("\\nResult:", res)
