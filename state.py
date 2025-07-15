from typing import List, TypedDict, Optional
from langchain_core.messages import BaseMessage

class RecipeAgentState(TypedDict):
    """
    Represent the state of our agent "Innovative Chef"
    """
    
    messages: List[BaseMessage] # Storico della conversazione con l'LLM
    user_desire: str            # Cosa l'utente vuole mangiare (es. "pasta", "piatto veloce con verdure")
    dietary_preferences: List[str] # Preferenze dietetiche (es. ["vegetariana", "senza glutine"])
    base_recipe_query: Optional[str] # Query usata per cercare la ricetta base su Tavily
    base_recipe_search_results: Optional[str] # Risultati della ricerca Tavily per la ricetta base
    extracted_ingredients_from_base_recipe: List[str] # Ingredienti chiave estratti dalla ricetta base
    pairing_query: Optional[str]    # Query usata per cercare abbinamenti nel PDF
    pairing_results: Optional[str]  # Risultati della ricerca nel PDF
    final_recipe: Optional[str]     # La ricetta innovativa finale generata
    error_message: Optional[str]    # Messaggio di errore se qualcosa va storto
    retry_count: int                # Contatore per gestire i tentativi in caso di errore
    tool_calls: List[dict]          # Le chiamate ai tool che l'LLM ha suggerito
    tool_results: List[dict]        # I risultati delle chiamate ai tool
    awaiting_user_input: Optional[bool] # Flag to indicate if the agent is waiting for user input
    user_language: Optional[str]    # User's detected language code (e.g., 'it', 'en', 'fr')