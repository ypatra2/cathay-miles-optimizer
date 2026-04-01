"""
AgentState — Shared state definition for the LangGraph agentic pipeline.
All nodes read from and write to this state.
"""

from typing import TypedDict, Optional


class AgentState(TypedDict):
    # ── Input ──────────────────────────────────────────────────
    current_engine_code: str          # Full text of optimizer.py
    trigger_source: str               # "manual" | "cron" | "github_actions"

    # ── Deep Research Agent output ─────────────────────────────
    research_report: str              # Markdown delta report
    research_status: str              # "pending" | "completed" | "failed"
    research_interaction_id: str      # Gemini interaction ID for tracing

    # ── Python Dev Agent output ────────────────────────────────
    proposed_patch: str               # The modified optimizer.py code
    patch_summary: str                # Human-readable summary of changes
    patch_status: str                 # "pending" | "generated" | "failed"

    # ── Git Integration ────────────────────────────────────────
    branch_name: str                  # e.g. "engine-refresh/2026-04"
    pr_url: str                       # GitHub PR URL

    # ── Metadata ───────────────────────────────────────────────
    started_at: str                   # ISO timestamp
    completed_at: Optional[str]       # ISO timestamp
    error: Optional[str]              # Error message if any step fails
