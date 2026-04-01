"""
LangGraph StateGraph — Wires the Deep Research Agent and Python Dev Agent
into a deterministic sequential pipeline.

Flow: deep_research → (if success) → dev_agent → END
                     → (if failed)  → END
"""

from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.research_agent import run_deep_research
from agents.dev_agent import run_dev_agent


def _route_after_research(state: dict) -> str:
    """Route to dev_agent if research succeeded, else END."""
    if state.get("research_status") == "completed":
        return "dev_agent"
    return END


def build_refresh_graph():
    """
    Builds and compiles the agentic refresh pipeline.

    Graph:
        START → deep_research → (conditional) → dev_agent → END
                                              → END (on failure)
    """
    graph = StateGraph(AgentState)

    # ── Nodes ───────────────────────────────────────────────
    graph.add_node("deep_research", run_deep_research)
    graph.add_node("dev_agent", run_dev_agent)

    # ── Edges ───────────────────────────────────────────────
    graph.set_entry_point("deep_research")
    graph.add_conditional_edges(
        "deep_research",
        _route_after_research,
        {
            "dev_agent": "dev_agent",
            END: END,
        },
    )
    graph.add_edge("dev_agent", END)

    return graph.compile()
