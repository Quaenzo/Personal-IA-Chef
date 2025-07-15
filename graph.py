from langgraph.graph import StateGraph, END
from state import RecipeAgentState
from nodes import *

def build_recipe_agent_graph():
    workflow = StateGraph(RecipeAgentState)
    
    # Add nodes
    workflow.add_node("start", start_node)
    workflow.add_node("search_base_recipe", search_base_recipe_node)
    workflow.add_node("extract_ingredients", extract_ingredients_node)
    workflow.add_node("search_pairings", search_pairings_node)
    workflow.add_node("generate_recipe", generate_recipe_node)
    workflow.add_node("clarify_input", clarify_input_node)
    
    # Set entry point
    workflow.set_entry_point("start")
    
    # Linear flow with clear progression
    workflow.add_conditional_edges(
        "start",
        lambda state: "search_base_recipe" if state["user_desire"] else "clarify_input"
    )
    
    workflow.add_conditional_edges(
        "search_base_recipe",
        lambda state: "extract_ingredients" if state["base_recipe_search_results"] else "clarify_input"
    )
    
    workflow.add_conditional_edges(
        "extract_ingredients", 
        lambda state: "search_pairings" if state["extracted_ingredients_from_base_recipe"] else "generate_recipe"
    )
    
    workflow.add_conditional_edges(
        "search_pairings",
        lambda state: "generate_recipe"
    )
    
    workflow.add_conditional_edges(
        "generate_recipe",
        lambda state: END if state["final_recipe"] else "clarify_input"
    )
    
    workflow.add_edge("clarify_input", END)
    
    return workflow.compile()