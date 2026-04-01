"""
Refresh Metadata — Manages the Supabase `engine_refreshes` table
for tracking all agentic refresh activity.

Falls back to local JSON if Supabase is unavailable.
"""

import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# Local fallback path
_LOCAL_LOG = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "engine_deltas",
    "refresh_log.json",
)


def _get_supabase():
    """Returns a Supabase client or None if unavailable."""
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None


def log_refresh(
    trigger_source: str,
    status: str,
    pr_url: str = "",
    branch_name: str = "",
    research_summary: str = "",
    patch_summary: str = "",
    delta_report: str = "",
) -> bool:
    """
    Logs a refresh run to Supabase (primary) or local JSON (fallback).

    Args:
        trigger_source: "manual" | "cron" | "github_actions"
        status: "pr_created" | "merged" | "rejected" | "failed"
        pr_url: GitHub PR URL
        branch_name: Git branch name
        research_summary: Brief summary of findings
        patch_summary: Brief summary of code changes
        delta_report: Full markdown report

    Returns:
        True if logged successfully
    """
    record = {
        "refreshed_at": datetime.now(timezone.utc).isoformat(),
        "trigger_source": trigger_source,
        "status": status,
        "pr_url": pr_url,
        "branch_name": branch_name,
        "research_summary": research_summary[:500],
        "patch_summary": patch_summary[:500],
        "delta_report": delta_report[:10000],  # Cap at 10K chars for Supabase
    }

    # Try Supabase first
    sb = _get_supabase()
    if sb:
        try:
            sb.table("engine_refreshes").insert(record).execute()
            return True
        except Exception as e:
            print(f"⚠️ Supabase insert failed ({e}), falling back to local log")

    # Fallback to local JSON
    return _log_local(record)


def _log_local(record: dict) -> bool:
    """Append a record to the local JSON log file."""
    try:
        os.makedirs(os.path.dirname(_LOCAL_LOG), exist_ok=True)
        data = []
        if os.path.exists(_LOCAL_LOG):
            with open(_LOCAL_LOG, "r") as f:
                data = json.load(f)
        data.append(record)
        with open(_LOCAL_LOG, "w") as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception:
        return False


def get_last_refresh() -> dict:
    """
    Returns the most recent refresh record from Supabase or local JSON.

    Returns:
        dict with keys: refreshed_at, trigger_source, status, pr_url,
        patch_summary. Empty dict if no records exist.
    """
    sb = _get_supabase()
    if sb:
        try:
            result = (
                sb.table("engine_refreshes")
                .select("*")
                .order("refreshed_at", desc=True)
                .limit(1)
                .execute()
            )
            if result.data:
                return result.data[0]
        except Exception:
            pass

    # Fallback to local
    if os.path.exists(_LOCAL_LOG):
        try:
            with open(_LOCAL_LOG, "r") as f:
                data = json.load(f)
            if data:
                return data[-1]
        except Exception:
            pass

    return {}


def get_refresh_history(limit: int = 10) -> list:
    """
    Returns the last N refresh records, newest first.
    """
    sb = _get_supabase()
    if sb:
        try:
            result = (
                sb.table("engine_refreshes")
                .select("*")
                .order("refreshed_at", desc=True)
                .limit(limit)
                .execute()
            )
            if result.data:
                return result.data
        except Exception:
            pass

    # Fallback
    if os.path.exists(_LOCAL_LOG):
        try:
            with open(_LOCAL_LOG, "r") as f:
                data = json.load(f)
            return list(reversed(data[-limit:]))
        except Exception:
            pass

    return []
