"""
Python Dev Agent — LangGraph node that uses Gemini 2.5 Flash to generate
an updated optimizer.py based on the Deep Research delta report.

Uses the google-genai SDK directly (no langchain dependency) for
maximum compatibility with Python 3.9.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a senior Python developer specializing in financial calculation engines.
You are given:
1. The CURRENT source code of a credit card miles calculation engine (optimizer.py)
2. A DELTA REPORT from a research agent containing verified rate changes, new categories, exclusions, spending caps, and MCC intelligence

YOUR TASK: Generate an UPDATED version of optimizer.py that incorporates ALL changes from the delta report.

## STRICT RULES — VIOLATION MEANS FAILURE:
1. **Preserve ALL existing function signatures**: `calculate_miles(card, category, amount)` and `get_recommendations(category, amount)` MUST NOT change signatures.
2. **Preserve the CARDS list**: Only ADD new cards, NEVER remove existing ones.
3. **Preserve the CATEGORIES list**: Only ADD new categories, NEVER remove existing ones.
4. **Add inline comments** citing the delta report for EVERY change you make. Format: `# DELTA: [description]`
5. **Do NOT hallucinate rates**: Only apply changes that are EXPLICITLY documented in the delta report. If the report says a rate is [UNVERIFIED], do NOT change it.
6. **Do NOT add imports** that aren't already used unless absolutely necessary.
7. **Output ONLY the complete Python file content** — no markdown fences, no explanations, no preamble. Just pure Python code that can be saved directly as optimizer.py.
8. **Preserve the existing code style**: Same indentation (4 spaces), same comment format, same structure.
9. **For EXCLUSIONS (zero-earn)**: Return (0, 0.0, "Excluded: [reason]") — do NOT return negative miles.
10. **For NEW CATEGORIES**: Add them to the CATEGORIES list AND add handling in calculate_miles for each card.

## CHANGE SUMMARY FORMAT:
After the complete Python file, on the VERY LAST LINE, add a Python comment starting with `# PATCH_SUMMARY: ` followed by a brief JSON-encoded summary of changes made. Example:
# PATCH_SUMMARY: {"changes": ["Updated SC Cathay food delivery rate from HK$6 to HK$4", "Added Insurance exclusion for all cards"], "categories_added": ["Insurance", "Supermarket"], "rates_changed": 3}
"""


def run_dev_agent(state: dict) -> dict:
    """
    LangGraph node: Takes the research report and current engine code,
    generates an updated optimizer.py via Gemini 2.5 Flash (REST API).
    """
    import requests

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "patch_status": "failed",
            "error": "GEMINI_API_KEY not found in environment"
        }

    research_report = state.get("research_report", "")
    engine_code = state.get("current_engine_code", "")

    if not research_report:
        return {
            "patch_status": "failed",
            "error": "No research report available to generate patch from"
        }

    # ── Build the prompt ────────────────────────────────────────
    user_message = f"""## CURRENT optimizer.py

```python
{engine_code}
```

## DELTA REPORT FROM RESEARCH AGENT

{research_report}

## INSTRUCTION
Generate the complete updated optimizer.py incorporating ALL verified changes from the delta report above. Follow the rules in your system prompt exactly. Output ONLY the Python code.
"""

    # ── Call Gemini 2.5 Flash via REST API ───────────────────────
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_message}]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 16384,
        }
    }

    try:
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()

        # Extract text from response
        raw_output = ""
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            for part in parts:
                if "text" in part:
                    raw_output += part["text"]

        if not raw_output:
            return {
                "patch_status": "failed",
                "error": "Gemini returned empty response",
            }

        # Clean up: strip markdown code fences if the model adds them
        cleaned = raw_output.strip()
        if cleaned.startswith("```python"):
            cleaned = cleaned[len("```python"):].strip()
        if cleaned.startswith("```"):
            cleaned = cleaned[3:].strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

        # Extract patch summary from the last line
        patch_summary = "Changes generated by Dev Agent"
        lines = cleaned.split("\n")
        for line in reversed(lines):
            if line.strip().startswith("# PATCH_SUMMARY:"):
                try:
                    summary_json = line.strip().replace("# PATCH_SUMMARY: ", "")
                    summary_data = json.loads(summary_json)
                    patch_summary = "; ".join(summary_data.get("changes", []))
                except (json.JSONDecodeError, KeyError):
                    patch_summary = line.strip().replace("# PATCH_SUMMARY: ", "")
                break

        # Validate: try to compile the generated code
        try:
            compile(cleaned, "optimizer.py", "exec")
        except SyntaxError as e:
            return {
                "patch_status": "failed",
                "error": f"Generated code has syntax error: {str(e)}",
                "proposed_patch": cleaned,
                "patch_summary": "FAILED: Syntax error in generated code",
            }

        # Save to engine_deltas/
        month_tag = datetime.now().strftime("%Y-%m")
        deltas_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "engine_deltas"
        )
        os.makedirs(deltas_dir, exist_ok=True)
        patch_path = os.path.join(deltas_dir, f"engine_patch_{month_tag}.py")
        with open(patch_path, "w") as f:
            f.write(cleaned)

        return {
            "proposed_patch": cleaned,
            "patch_summary": patch_summary,
            "patch_status": "generated",
            "completed_at": datetime.now().isoformat(),
        }

    except Exception as e:
        return {
            "patch_status": "failed",
            "error": f"Dev Agent failed: {str(e)}",
        }
