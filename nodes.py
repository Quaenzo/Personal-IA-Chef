import asyncio
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from state import RecipeAgentState
from tools import llm, tavily_search_tool, search_food_pairings

def start_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Initialize the conversation"""
    print("🍳 Starting recipe creation process...")
    
    if not state["user_desire"]:
        return {"awaiting_user_input": True}
    
    return {"awaiting_user_input": False}

def search_base_recipe_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Search for a base recipe using Tavily - FIXED VERSION"""
    print(f"🔍 Searching for base recipe: {state['user_desire']}")
    
    try:
        query = f"{state['user_desire']} recipe cooking instructions"
        print(f"Search query: {query}")
        
        # Call Tavily search
        results = tavily_search_tool.invoke(query)
        print(f"Raw results type: {type(results)}")
        print(f"Raw results: {results}")
        
        # Handle different possible result formats
        formatted_results = []
        
        if isinstance(results, dict):
            # If results is a dict, look for 'results' key
            if 'results' in results:
                search_results = results['results']
            else:
                search_results = [results]  # Treat the dict as a single result
        elif isinstance(results, list):
            search_results = results
        elif isinstance(results, str):
            # If it's already a string, use it directly
            return {
                "base_recipe_search_results": results,
                "base_recipe_query": query
            }
        else:
            # Fallback for unknown types
            return {
                "base_recipe_search_results": str(results),
                "base_recipe_query": query
            }
        
        # Process the search results
        for i, result in enumerate(search_results[:3]):  # Top 3 results
            if isinstance(result, dict):
                title = result.get('title', result.get('name', f'Recipe {i+1}'))
                content = result.get('content', result.get('snippet', result.get('description', 'No description available')))
                url = result.get('url', '')
                
                formatted_result = f"**{title}**\n{content}"
                if url:
                    formatted_result += f"\nSource: {url}"
                
                formatted_results.append(formatted_result)
            elif isinstance(result, str):
                formatted_results.append(f"**Recipe {i+1}**\n{result}")
            else:
                formatted_results.append(f"**Recipe {i+1}**\n{str(result)}")
        
        if formatted_results:
            return {
                "base_recipe_search_results": "\n\n".join(formatted_results),
                "base_recipe_query": query
            }
        else:
            return {"error_message": "No useful recipe information found"}
            
    except Exception as e:
        print(f"Error in search_base_recipe_node: {str(e)}")
        print(f"Error type: {type(e)}")
        return {"error_message": f"Error searching for base recipe: {str(e)}"}

def debug_search_base_recipe_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Debug version to understand Tavily output format"""
    print(f"🔍 DEBUG: Searching for base recipe: {state['user_desire']}")
    
    try:
        query = f"{state['user_desire']} recipe cooking instructions"
        print(f"Search query: {query}")
        
        # Call Tavily search
        results = tavily_search_tool.invoke(query)
        
        # Detailed debugging
        print(f"Results type: {type(results)}")
        print(f"Results repr: {repr(results)}")
        
        if hasattr(results, '__dict__'):
            print(f"Results attributes: {results.__dict__}")
        
        if isinstance(results, (list, tuple)):
            print(f"Results length: {len(results)}")
            if len(results) > 0:
                print(f"First result type: {type(results[0])}")
                print(f"First result: {repr(results[0])}")
        
        if isinstance(results, dict):
            print(f"Results keys: {list(results.keys())}")
            for key, value in results.items():
                print(f"  {key}: {type(value)} - {repr(value)[:100]}...")
        
        # For now, just return the raw results as a string
        return {
            "base_recipe_search_results": str(results),
            "base_recipe_query": query
        }
        
    except Exception as e:
        print(f"DEBUG Error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return {"error_message": f"Error searching for base recipe: {str(e)}"}

def extract_ingredients_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Extract key ingredients from the base recipe"""
    print("📝 Extracting ingredients from base recipe...")
    
    base_recipe = state["base_recipe_search_results"]
    
    prompt = f"""
    From the following recipe information, extract the 3-4 main ingredients that would be most important for finding flavor pairings:

    {base_recipe}

    Return only the main ingredients as a comma-separated list (e.g., "chicken, lemon, herbs, garlic").
    Focus on proteins, main vegetables, and dominant flavors.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        ingredients_text = response.content.strip()
        
        # Clean and parse ingredients
        ingredients = [ing.strip() for ing in ingredients_text.split(',') if ing.strip()]
        
        return {
            "extracted_ingredients_from_base_recipe": ingredients,
            "pairing_query": f"pairings for {' '.join(ingredients[:3])}"
        }
        
    except Exception as e:
        return {"error_message": f"Error extracting ingredients: {str(e)}"}

def search_pairings_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Search for food pairings"""
    print("🍯 Searching for flavor pairings...")
    
    try:
        query = state["pairing_query"]
        results = search_food_pairings.invoke(query)
        
        return {"pairing_results": results}
        
    except Exception as e:
        return {"error_message": f"Error searching pairings: {str(e)}"}

def get_language_instructions(lang_code: str) -> str:
    """Get specific language instructions for the LLM"""
    language_instructions = {
        'it': "IMPORTANTE: Rispondi SEMPRE in italiano. Usa unità di misura italiane (grammi, litri, cucchiai, ecc.). Scrivi tutti i testi in italiano.",
        'en': "IMPORTANT: Always respond in English. Use imperial or metric measurements as appropriate. Write all text in English.",
        'fr': "IMPORTANT: Répondez TOUJOURS en français. Utilisez des unités de mesure françaises (grammes, litres, cuillères, etc.). Écrivez tout le texte en français.",
        'es': "IMPORTANTE: Responde SIEMPRE en español. Usa unidades de medida españolas (gramos, litros, cucharadas, etc.). Escribe todo el texto en español.",
        'de': "WICHTIG: Antworte IMMER auf Deutsch. Verwende deutsche Maßeinheiten (Gramm, Liter, Esslöffel, usw.). Schreibe den gesamten Text auf Deutsch.",
        'pt': "IMPORTANTE: Responda SEMPRE em português. Use unidades de medida portuguesas (gramas, litros, colheres, etc.). Escreva todo o texto em português.",
        'zh': "重要：始终用中文回复。使用中文度量单位（克、升、勺等）。用中文写所有文本。",
        'ja': "重要：必ず日本語で回答してください。日本の単位（グラム、リットル、大さじなど）を使用してください。すべてのテキストを日本語で書いてください。",
        'ko': "중요: 항상 한국어로 답하세요. 한국의 측정 단위(그램, 리터, 큰술 등)를 사용하세요. 모든 텍스트를 한국어로 작성하세요.",
        'ru': "ВАЖНО: Всегда отвечайте на русском языке. Используйте русские единицы измерения (граммы, литры, ложки и т.д.). Пишите весь текст на русском языке.",
        'ar': "مهم: أجب دائماً بالعربية. استخدم وحدات القياس العربية (جرام، لتر، ملعقة، إلخ). اكتب كل النص بالعربية."
    }
    
    return language_instructions.get(lang_code, language_instructions['it'])

def generate_recipe_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Generate the final innovative recipe"""
    print("👨‍🍳 Generating innovative recipe...")
    
    dietary_prefs = ", ".join(state['dietary_preferences']) if state['dietary_preferences'] else "none"
    user_language = state.get('user_language', 'it')
    
    # Get specific language instructions
    language_instruction = get_language_instructions(user_language)
    
    prompt = f"""
    {language_instruction}

    Create an innovative recipe based on:
    - User request: {state['user_desire']}
    - Dietary preferences: {dietary_prefs}
    - Base recipe: {state['base_recipe_search_results']}
    - Flavor pairings: {state.get('pairing_results', 'No specific pairings found')}

    Format your response as a complete recipe with:
    - Creative title
    - Ingredients list with quantities (use appropriate units for the target language)
    - Step-by-step instructions
    - Serving suggestions

    Make it innovative by incorporating the suggested pairings while keeping it practical.
    
    Remember: The user's language is {user_language}. Write EVERYTHING in this language including measurements, cooking terms, and all text.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        recipe = response.content.strip()
        
        # Simple validation
        if len(recipe) > 100:
            return {"final_recipe": recipe}
        else:
            return {"error_message": "Generated recipe seems incomplete"}
            
    except Exception as e:
        return {"error_message": f"Error generating recipe: {str(e)}"}

def clarify_input_node(state: RecipeAgentState) -> Dict[str, Any]:
    """Ask for clarification when needed"""
    print("❓ Requesting clarification...")
    
    error_msg = state.get("error_message", "")
    user_language = state.get('user_language', 'it')
    
    # Language-specific clarification messages
    clarification_messages = {
        'it': {
            'rate_limit': "Ho raggiunto il limite di richieste. Attendi un momento e riprova.",
            'no_desire': "Cosa vorresti cucinare? Descrivi il piatto che hai in mente.",
            'more_details': f"Ho bisogno di più dettagli per creare la tua ricetta. Potresti essere più specifico riguardo '{state.get('user_desire', '')}'?"
        },
        'en': {
            'rate_limit': "I've hit a rate limit. Please wait a moment and try again.",
            'no_desire': "What would you like to cook? Please describe the dish you have in mind.",
            'more_details': f"I need more details to create your recipe. Could you be more specific about '{state.get('user_desire', '')}'?"
        },
        'fr': {
            'rate_limit': "J'ai atteint une limite de débit. Veuillez attendre un moment et réessayer.",
            'no_desire': "Que souhaitez-vous cuisiner ? Veuillez décrire le plat que vous avez en tête.",
            'more_details': f"J'ai besoin de plus de détails pour créer votre recette. Pourriez-vous être plus précis sur '{state.get('user_desire', '')}'?"
        },
        'es': {
            'rate_limit': "He alcanzado un límite de velocidad. Por favor, espera un momento e inténtalo de nuevo.",
            'no_desire': "¿Qué te gustaría cocinar? Describe el plato que tienes en mente.",
            'more_details': f"Necesito más detalles para crear tu receta. ¿Podrías ser más específico sobre '{state.get('user_desire', '')}'?"
        },
        'de': {
            'rate_limit': "Ich habe ein Ratenlimit erreicht. Bitte warten Sie einen Moment und versuchen Sie es erneut.",
            'no_desire': "Was möchten Sie kochen? Bitte beschreiben Sie das Gericht, das Sie sich vorstellen.",
            'more_details': f"Ich brauche mehr Details, um Ihr Rezept zu erstellen. Könnten Sie spezifischer über '{state.get('user_desire', '')}' sein?"
        }
    }
    
    messages = clarification_messages.get(user_language, clarification_messages['it'])
    
    if "rate limit" in error_msg.lower():
        message = messages['rate_limit']
    elif not state["user_desire"]:
        message = messages['no_desire']
    else:
        message = messages['more_details']
    
    return {
        "messages": [AIMessage(content=message)],
        "awaiting_user_input": True
    }