#!/usr/bin/env python3
"""
Refresh Cron — Standalone CLI script for running the agentic engine
refresh pipeline headlessly.

Usage:
    # Manual run from terminal:
    python refresh_cron.py

    # Via GitHub Actions (see .github/workflows/engine_refresh.yml):
    python refresh_cron.py --github-actions
"""

import sys
import os

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.dirname(__file__))

from agents.runner import run_refresh_pipeline


def main():
    trigger = "github_actions" if "--github-actions" in sys.argv else "cron"

    print("🔬 Cathay Miles Engine — Agentic Refresh Pipeline")
    print("━" * 60)
    print(f"   Trigger: {trigger}")
    print(f"   Mode: {'GitHub Actions (files only)' if trigger == 'github_actions' else 'Full (branch + PR)'}")
    print("━" * 60)

    def cli_progress(step, detail):
        print(f"   [{step}] {detail}")

    result = run_refresh_pipeline(
        trigger_source=trigger,
        progress_callback=cli_progress,
    )

    print("\n" + "═" * 60)
    if result["success"]:
        print("✅ Pipeline completed successfully!")
        if result.get("pr_url"):
            print(f"📋 PR URL: {result['pr_url']}")
        if result.get("branch_name"):
            print(f"🌿 Branch: {result['branch_name']}")
        if result.get("patch_summary"):
            print(f"📝 Summary: {result['patch_summary']}")
    else:
        print(f"❌ Pipeline failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)

    print("═" * 60)


if __name__ == "__main__":
    main()
