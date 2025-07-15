import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from typing import List, Any, Dict
from pdf_processor import get_abbinamenti_retriever
from langgraph.prebuilt.tool_node import ToolNode # Import ToolNode

load_dotenv()

llm = ChatGroq( model="llama3-70b-8192", temperature=0.7)

tavily_search_tool = TavilySearch(max_results=5)
tavily_search_tool.name = "tavily_search"
tavily_search_tool.description = "Used to retrieve information about recipes, ingredients and cooking methods or any other general information on the web. Give pertinent result based on the query."

abbinamenti_retriever = get_abbinamenti_retriever()

@tool
def search_food_pairings(query: str) -> str:
    """
    Search the flavours book for suggestions for specific ingredients or combinations.
    Use this feature when you need to find innovative pairings for a recipe's ingredients.
    Input: query (string, e.g., "pairings for chicken and rosemary").
    """
    print(f"\n--- TOOL CALL: search_food_pairings for : '{query}' ---")
    try:
        docs = abbinamenti_retriever.invoke(query)
        if not docs:
            return "No pertinent pairing found in the book for the query."
        
        results = "\n---\n".join([doc.page_content for doc in docs])
        return f"Results from the book of flavours:\n{results}"
    except Exception as e:
        return f"Error found during the research for the pairings in the book: {e}"
    
tools = [tavily_search_tool, search_food_pairings]

# Ensure llm_with_tools is defined here so it can be imported by nodes.py
llm_with_tools = llm.bind_tools(tools)

# Define tool_executor here so it can be imported from tools.py
tool_executor = ToolNode(tools)
