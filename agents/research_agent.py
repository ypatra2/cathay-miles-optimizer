"""
Deep Research Agent — LangGraph node that uses the Gemini Deep Research
REST API to find deltas against the current optimizer.py engine.

Uses the same REST-based approach proven in testing (Interactions API).
"""

import os
import time
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
POLL_INTERVAL = 30   # seconds
MAX_TIMEOUT = 1200   # 20 minutes


def _build_research_prompt(engine_code: str) -> str:
    """
    Constructs the Deep Research prompt by embedding the current engine
    state. This ensures the prompt always reflects the latest optimizer.py.
    """
    return f"""
You are a Hong Kong credit card rewards research analyst. I have an existing Python calculation engine for Cathay (Asia) Miles optimization that covers 4 cards. Your job is to perform deep, exhaustive research and produce a DELTA REPORT — focusing ONLY on what needs to be ADDED, CORRECTED, or UPDATED versus the current engine state I provide below.

## CURRENT ENGINE STATE (Python source code)

```python
{engine_code}
```

## YOUR RESEARCH TASKS

For each of the 4 cards in the engine above, research and report:

### 1. RATE VERIFICATION
- Verify every earn rate in the code against the latest official bank pages.
- Flag any rate that has CHANGED.
- Check if any promotional rates or thresholds have been updated or expired.

### 2. MISSING CATEGORY GAPS
- Are there any earn rate categories NOT captured? For example:
  - Insurance premium payments
  - Government / tax payments (IRD eTAX)
  - PayMe / AlipayHK / WeChat Pay top-ups
  - Utilities (CLP, HK Electric, Towngas)
  - Education fees, Hospital / medical
  - Supermarkets (especially for EveryMile)
  - Hotel bookings
- Which of these earn ZERO miles (exclusions) vs reduced rates?

### 3. SPENDING CAPS & THRESHOLDS
- Verify the exact monthly/quarterly/annual spending caps for bonus tiers on each card.
- Check if any caps have changed or new ones have been introduced.

### 4. ACTIVE PROMOTIONS (Current Month)
- Any "Travel Guru" promotions on EveryMile?
- Any "Red Hot Rewards" seasonal category changes on VISA Signature?
- Any limited-time multiplier offers on SC Cathay?
- Any new designated merchants added to EveryMile or Red's 8% list?

### 5. MERCHANT CODE (MCC) INTELLIGENCE
- Uber Hong Kong: current MCC classification and which card benefits?
- Food delivery apps (Keeta, Foodpanda): Confirm MCC — "dining" or "online"?
- Confirm if bill payments via online banking trigger online bonuses or are excluded.

## OUTPUT FORMAT

Structure your report as follows:

```markdown
# Cathay Miles Engine — Deep Research Delta Report
## Date: [Current Date]

### 🔄 RATE CHANGES (vs current engine)
| Card | Category | Old Rate | New Rate | Source |
|------|----------|----------|----------|--------|
(Only list items that CHANGED. If nothing changed, state "All rates verified — no changes detected.")

### ➕ MISSING CATEGORIES TO ADD
| Card | Category | Rate (HKD/Mile) | Cap | Notes |
|------|----------|------------------|-----|-------|

### 🚫 EXCLUSIONS (Zero-earn categories)
| Card | Excluded Transaction Type | Details |
|------|---------------------------|---------|

### 📊 SPENDING CAPS & THRESHOLDS (Verified)
| Card | Cap/Threshold | Amount | Period | Status |
|------|---------------|--------|--------|--------|

### 🎯 ACTIVE PROMOTIONS (Current Month)
| Card | Promo Name | Details | Validity |
|------|------------|---------|----------|

### 🏷️ MCC INTELLIGENCE
| Merchant/Type | MCC Code | Classification | Which Card Benefits |
|---------------|----------|----------------|---------------------|

### 📝 RULES FOR CALCULATION ENGINE
(Provide Python-parseable logic updates. Example:)
- "For HSBC Red: if category == 'Insurance' → rate = 0 (excluded)"
- "For EveryMile: add new designated merchant 'XYZ' to HK$2=1mi tier"
```

Be thorough. Cite your sources. If you cannot verify a specific data point, mark it as [UNVERIFIED].
"""


def run_deep_research(state: dict) -> dict:
    """
    LangGraph node: Launches a Deep Research task and polls for results.
    Returns updated state with the research report.
    """
    api_key_raw = os.getenv("GEMINI_API_KEY")
    if not api_key_raw:
        return {
            "research_status": "failed",
            "error": "GEMINI_API_KEY not found in environment"
        }
    
    # Strip quotes and spaces (common mistake when copy-pasting from TOML to GitHub Secrets)
    api_key = api_key_raw.strip(' \n\r"\'')

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    # Build prompt from current engine code
    engine_code = state.get("current_engine_code", "")
    prompt = _build_research_prompt(engine_code)

    # ── Launch the research task ────────────────────────────────
    payload = {
        "input": prompt,
        "agent": "deep-research-pro-preview-12-2025",
        "background": True,
    }

    try:
        r = requests.post(BASE_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        launch = r.json()
    except Exception as e:
        return {
            "research_status": "failed",
            "error": f"Failed to launch Deep Research: {str(e)}"
        }

    interaction_id = launch.get("id", "unknown")

    # ── Poll for results ────────────────────────────────────────
    start = time.time()

    while time.time() - start < MAX_TIMEOUT:
        try:
            poll_r = requests.get(
                f"{BASE_URL}/{interaction_id}",
                headers=headers,
                timeout=30
            )
            poll_r.raise_for_status()
            data = poll_r.json()
        except Exception:
            time.sleep(POLL_INTERVAL)
            continue

        status = data.get("status", "unknown")

        if status == "completed":
            outputs = data.get("outputs", [])
            report = ""
            if outputs and outputs[-1].get("text"):
                report = outputs[-1]["text"]
            else:
                report = json.dumps(data, indent=2, default=str)

            # Save to engine_deltas/
            month_tag = datetime.now().strftime("%Y-%m")
            deltas_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "engine_deltas"
            )
            os.makedirs(deltas_dir, exist_ok=True)
            report_path = os.path.join(deltas_dir, f"engine_delta_{month_tag}.md")
            with open(report_path, "w") as f:
                f.write(report)

            return {
                "research_report": report,
                "research_status": "completed",
                "research_interaction_id": interaction_id,
            }

        elif status == "failed":
            return {
                "research_status": "failed",
                "research_interaction_id": interaction_id,
                "error": f"Deep Research task failed: {json.dumps(data, indent=2, default=str)[:500]}"
            }

        time.sleep(POLL_INTERVAL)

    # Timed out
    return {
        "research_status": "failed",
        "research_interaction_id": interaction_id,
        "error": f"Deep Research timed out after {MAX_TIMEOUT}s"
    }
