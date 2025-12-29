from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import extract_entities, stock_and_order

def build_agent(llm):
    graph = StateGraph(AgentState)

    graph.add_node("extract", lambda s: extract_entities(s, llm))
    graph.add_node("process", stock_and_order)

    graph.set_entry_point("extract")
    graph.add_edge("extract", "process")
    graph.add_edge("process", END)

    return graph.compile()
