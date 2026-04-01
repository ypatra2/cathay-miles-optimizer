"""
Pipeline Runner — Entry point for the agentic engine refresh pipeline.

Can be called from:
1. Streamlit UI (manual trigger)
2. CLI (refresh_cron.py)
3. GitHub Actions workflow
"""

import os
from datetime import datetime, timezone

from agents.graph import build_refresh_graph
from agents.git_manager import create_refresh_branch, create_github_pr
from agents.refresh_metadata import log_refresh


def run_refresh_pipeline(
    trigger_source: str = "manual",
    progress_callback=None,
) -> dict:
    """
    Runs the full agentic refresh pipeline:
    1. Read current optimizer.py
    2. Run Deep Research Agent
    3. Run Python Dev Agent
    4. Create Git branch + push
    5. Open GitHub PR
    6. Log to Supabase

    Args:
        trigger_source: "manual" | "cron" | "github_actions"
        progress_callback: Optional callable(step: str, detail: str)
                          for Streamlit progress updates.

    Returns:
        dict with keys: success, pr_url, branch_name,
        patch_summary, research_report, error
    """

    def _progress(step: str, detail: str = ""):
        if progress_callback:
            progress_callback(step, detail)

    # ── Step 1: Read current engine ─────────────────────────
    _progress("reading", "Reading current optimizer.py...")
    project_root = os.path.dirname(os.path.dirname(__file__))
    optimizer_path = os.path.join(project_root, "optimizer.py")

    try:
        with open(optimizer_path, "r") as f:
            engine_code = f.read()
    except FileNotFoundError:
        return {"success": False, "error": "optimizer.py not found"}

    # ── Step 2: Build and run the LangGraph pipeline ────────
    _progress("research", "🔬 Deep Research Agent is working...")

    initial_state = {
        "current_engine_code": engine_code,
        "trigger_source": trigger_source,
        "research_report": "",
        "research_status": "pending",
        "research_interaction_id": "",
        "proposed_patch": "",
        "patch_summary": "",
        "patch_status": "pending",
        "branch_name": "",
        "pr_url": "",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "error": None,
    }

    graph = build_refresh_graph()
    final_state = graph.invoke(initial_state)

    # ── Check research result ───────────────────────────────
    if final_state.get("research_status") != "completed":
        error_msg = final_state.get("error", "Research failed with no error message")
        log_refresh(
            trigger_source=trigger_source,
            status="failed",
            research_summary=error_msg,
        )
        return {
            "success": False,
            "error": f"Research Agent failed: {error_msg}",
            "research_report": final_state.get("research_report", ""),
        }

    _progress("dev_agent", "🧑‍💻 Python Dev Agent is generating code...")

    # ── Check dev agent result ──────────────────────────────
    if final_state.get("patch_status") != "generated":
        error_msg = final_state.get("error", "Dev Agent failed with no error message")
        log_refresh(
            trigger_source=trigger_source,
            status="failed",
            research_summary=final_state.get("research_report", "")[:200],
            patch_summary=error_msg,
        )
        return {
            "success": False,
            "error": f"Dev Agent failed: {error_msg}",
            "research_report": final_state.get("research_report", ""),
        }

    _progress("git", "🌿 Creating Git branch and pushing changes...")

    # ── Step 3: Create Git branch ───────────────────────────
    proposed_code = final_state["proposed_patch"]
    delta_report = final_state["research_report"]

    # For GitHub Actions, we skip branch/PR creation (handled by the workflow)
    if trigger_source == "github_actions":
        # Just write the files, the workflow YAML handles branching
        _progress("complete", "✅ Files updated. GitHub Actions will create the PR.")
        log_refresh(
            trigger_source=trigger_source,
            status="pr_created",
            research_summary=delta_report[:200],
            patch_summary=final_state.get("patch_summary", ""),
            delta_report=delta_report,
        )
        return {
            "success": True,
            "pr_url": "",
            "branch_name": "",
            "patch_summary": final_state.get("patch_summary", ""),
            "research_report": delta_report,
        }

    # For manual/cron triggers, create branch + PR ourselves
    branch_result = create_refresh_branch(proposed_code, delta_report)

    if not branch_result["success"]:
        log_refresh(
            trigger_source=trigger_source,
            status="failed",
            research_summary=delta_report[:200],
            patch_summary=f"Git branch failed: {branch_result['error']}",
            delta_report=delta_report,
        )
        return {
            "success": False,
            "error": f"Git branch creation failed: {branch_result['error']}",
            "research_report": delta_report,
            "patch_summary": final_state.get("patch_summary", ""),
        }

    _progress("pr", "📋 Opening GitHub Pull Request...")

    # ── Step 4: Create GitHub PR ────────────────────────────
    branch_name = branch_result["branch_name"]
    patch_summary = final_state.get("patch_summary", "")

    pr_result = create_github_pr(branch_name, patch_summary)

    _progress("logging", "📊 Logging to Supabase...")

    # ── Step 5: Log to Supabase ─────────────────────────────
    log_refresh(
        trigger_source=trigger_source,
        status="pr_created",
        pr_url=pr_result.get("pr_url", ""),
        branch_name=branch_name,
        research_summary=delta_report[:200],
        patch_summary=patch_summary,
        delta_report=delta_report,
    )

    _progress("complete", "✅ Pipeline complete! PR ready for review.")

    return {
        "success": True,
        "pr_url": pr_result.get("pr_url", ""),
        "branch_name": branch_name,
        "patch_summary": patch_summary,
        "research_report": delta_report,
        "pr_note": pr_result.get("note", ""),
        "error": pr_result.get("error"),
    }
