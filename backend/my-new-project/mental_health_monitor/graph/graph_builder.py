"""LangGraph builder for orchestrating the mental health monitoring pipeline."""

from langgraph.graph import StateGraph, START, END
from typing import Any

from .state import GraphState
from .nodes import (
    behavioral_agent_node,
    physiological_agent_node,
    context_agent_node,
    language_agent_node,
    orchestrator_agent_node,
    conversational_agent_node,
)


def build_monitoring_graph() -> StateGraph:
    """Build the LangGraph for mental health monitoring.
    
    Graph Flow:
    START
      ↓
    [Parallel] Behavioral, Physiological, Context, Language Agents
      ↓
    Orchestrator Agent
      ↓
    Conversational Support Agent
      ↓
    END
    
    Returns:
        Compiled StateGraph
    """
    # Create graph
    graph = StateGraph(GraphState)
    
    # Add nodes
    graph.add_node("behavioral_agent", behavioral_agent_node)
    graph.add_node("physiological_agent", physiological_agent_node)
    graph.add_node("context_agent", context_agent_node)
    graph.add_node("language_agent", language_agent_node)
    graph.add_node("orchestrator_agent", orchestrator_agent_node)
    graph.add_node("conversational_agent", conversational_agent_node)
    
    # Set edges
    # Start -> all analytical agents (parallel)
    graph.add_edge(START, "behavioral_agent")
    graph.add_edge(START, "physiological_agent")
    graph.add_edge(START, "context_agent")
    graph.add_edge(START, "language_agent")
    
    # All analytical agents -> orchestrator (convergence)
    graph.add_edge("behavioral_agent", "orchestrator_agent")
    graph.add_edge("physiological_agent", "orchestrator_agent")
    graph.add_edge("context_agent", "orchestrator_agent")
    graph.add_edge("language_agent", "orchestrator_agent")
    
    # Orchestrator -> conversational
    graph.add_edge("orchestrator_agent", "conversational_agent")
    
    # Conversational -> end
    graph.add_edge("conversational_agent", END)
    
    return graph


def get_compiled_graph():
    """Get compiled and runnable graph.
    
    Returns:
        Compiled LangGraph runnable
    """
    graph = build_monitoring_graph()
    return graph.compile()
