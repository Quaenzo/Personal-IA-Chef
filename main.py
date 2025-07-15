import os
from dotenv import load_dotenv
from graph import build_recipe_agent_graph
from state import RecipeAgentState

def run_chef_innovativo():
    """Main execution function with better error handling"""
    app = build_recipe_agent_graph()
    
    print("🍳 Welcome to Chef Innovativo!")
    print("I'll help you create unique recipes by combining traditional dishes with innovative pairings.")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            # Get user input
            user_input = input("What would you like to cook? ").strip()
            if user_input.lower() == 'exit':
                print("👋 Happy cooking!")
                break
            
            dietary_input = input("Any dietary preferences? (optional): ").strip()
            dietary_prefs = [p.strip() for p in dietary_input.split(',') if p.strip()]
            
            # Initialize state
            initial_state = RecipeAgentState(
                messages=[],
                user_desire=user_input,
                dietary_preferences=dietary_prefs,
                base_recipe_query=None,
                base_recipe_search_results=None,
                extracted_ingredients_from_base_recipe=[],
                pairing_query=None,
                pairing_results=None,
                final_recipe=None,
                error_message=None,
                retry_count=0,
                tool_calls=[],
                tool_results=[],
                awaiting_user_input=False
            )
            
            print("\n🔥 Creating your innovative recipe...")
            
            # Execute the graph
            final_state = app.invoke(initial_state)
            
            # Handle results
            if final_state.get("final_recipe"):
                print("\n" + "="*60)
                print("🎉 YOUR INNOVATIVE RECIPE")
                print("="*60)
                print(final_state["final_recipe"])
                print("="*60)
                
            elif final_state.get("error_message"):
                print(f"\n❌ Error: {final_state['error_message']}")
                
            else:
                print("\n🤔 I wasn't able to create a recipe. Please try again with more details.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n💥 Unexpected error: {e}")
            continue

if __name__ == "__main__":
    run_chef_innovativo()