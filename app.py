import streamlit as st
import os
from dotenv import load_dotenv
from graph import build_recipe_agent_graph
from state import RecipeAgentState
import time
from langdetect import detect
import langdetect.lang_detect_exception

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Innovative Chef",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    .recipe-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border-left: 5px solid #4ECDC4;
        margin: 1rem 0;
    }
    
    .error-container {
        background-color: #ffe6e6;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #ff4444;
        margin: 1rem 0;
    }
    
    .loading-container {
        text-align: center;
        padding: 2rem;
    }
    
    .sidebar-section {
        background-color: #f1f3f4;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'app' not in st.session_state:
    st.session_state.app = build_recipe_agent_graph()
if 'user_language' not in st.session_state:
    st.session_state.user_language = 'en'

def detect_language(text):
    """Detect the language of the input text"""
    try:
        language = detect(text)
        return language
    except langdetect.lang_detect_exception.LangDetectException:
        return 'en'  

def get_language_name(lang_code):
    """Convert language code to full name"""
    lang_names = {
        'it': 'Italian',
        'en': 'English',
        'fr': 'French',
        'es': 'Spanish',
        'de': 'German',
        'pt': 'Portuguese',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean',
        'ru': 'Russian',
        'ar': 'Arabic'
    }
    return lang_names.get(lang_code, 'English')

def display_message(message, is_user=True):
    """Display a message in the chat interface"""
    if is_user:
        with st.chat_message("user"):
            st.write(message)
    else:
        with st.chat_message("assistant"):
            st.write(message)

def process_recipe_request(user_desire, dietary_preferences):
    """Process the recipe request using the LangGraph agent"""
    
    # Detect user language
    detected_lang = detect_language(user_desire)
    st.session_state.user_language = detected_lang
    language_name = get_language_name(detected_lang)
    
    # Initialize state
    initial_state = RecipeAgentState(
        messages=[],
        user_desire=user_desire,
        dietary_preferences=dietary_preferences,
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
        awaiting_user_input=False,
        user_language=detected_lang  # Add language to state
    )
    
    # Create progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Update progress with language-specific messages
        if detected_lang == 'en':
            status_text.text("🔍 Searching for base recipe...")
        elif detected_lang == 'fr':
            status_text.text("🔍 Recherche de la recette de base...")
        elif detected_lang == 'es':
            status_text.text("🔍 Buscando receta base...")
        elif detected_lang == 'de':
            status_text.text("🔍 Suche nach Grundrezept...")
        else:
            status_text.text("🔍 Ricerca ricetta base...")
        
        progress_bar.progress(20)
        
        # Execute the graph
        final_state = st.session_state.app.invoke(initial_state)
        
        # Update progress
        if detected_lang == 'en':
            status_text.text("📝 Extracting ingredients...")
        elif detected_lang == 'fr':
            status_text.text("📝 Extraction des ingrédients...")
        elif detected_lang == 'es':
            status_text.text("📝 Extrayendo ingredientes...")
        elif detected_lang == 'de':
            status_text.text("📝 Zutaten extrahieren...")
        else:
            status_text.text("📝 Estrazione ingredienti...")
        
        progress_bar.progress(40)
        time.sleep(0.5)
        
        if detected_lang == 'en':
            status_text.text("🍯 Finding flavor pairings...")
        elif detected_lang == 'fr':
            status_text.text("🍯 Recherche d'associations de saveurs...")
        elif detected_lang == 'es':
            status_text.text("🍯 Buscando maridajes de sabores...")
        elif detected_lang == 'de':
            status_text.text("🍯 Geschmackskombinationen finden...")
        else:
            status_text.text("🍯 Ricerca abbinamenti sapori...")
        
        progress_bar.progress(60)
        time.sleep(0.5)
        
        if detected_lang == 'en':
            status_text.text("👨‍🍳 Generating innovative recipe...")
        elif detected_lang == 'fr':
            status_text.text("👨‍🍳 Génération de recette innovante...")
        elif detected_lang == 'es':
            status_text.text("👨‍🍳 Generando receta innovadora...")
        elif detected_lang == 'de':
            status_text.text("👨‍🍳 Innovative Rezept generieren...")
        else:
            status_text.text("👨‍🍳 Generazione ricetta innovativa...")
        
        progress_bar.progress(80)
        time.sleep(0.5)
        
        progress_bar.progress(100)
        
        if detected_lang == 'en':
            status_text.text("✅ Recipe ready!")
        elif detected_lang == 'fr':
            status_text.text("✅ Recette prête!")
        elif detected_lang == 'es':
            status_text.text("✅ ¡Receta lista!")
        elif detected_lang == 'de':
            status_text.text("✅ Rezept fertig!")
        else:
            status_text.text("✅ Ricetta pronta!")
        
        # Clear progress indicators
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        return final_state
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"Error processing request: {str(e)}")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">🍳 Chef Innovativo</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #666;">
            Creo ricette innovative combinando piatti tradizionali con abbinamenti creativi
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for settings
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.header("🔧 Impostazioni")
        
        # Dietary preferences
        st.subheader("Dietary preferences")
        dietary_options = [
            "Vegetarian", "Vegan", "Gluten-free", "Lactose-free",
            "Keto", "Paleo", "Mediterranean", "No Sugar"
        ]
        selected_prefs = st.multiselect(
            "Select your preference:",
            dietary_options,
            default=[]
        )
        
        # Language detection display
        st.markdown("### 🌐 Language found")
        if st.session_state.user_language:
            lang_name = get_language_name(st.session_state.user_language)
            st.info(f"**{lang_name}** ({st.session_state.user_language})")
        else:
            st.info("No language found")
        
        # Recipe complexity
        st.subheader("Recipe complexity")
        complexity = st.select_slider(
            "Difficulty level:",
            options=["Easy", "Medium", "Hard"],
            value="Medium"
        )
        
        # Serving size
        st.subheader("Portions")
        servings = st.number_input(
            "Number of portions:",
            min_value=1,
            max_value=12,
            value=4
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Clear chat button
        if st.button("🗑️ Clean chat", type="secondary"):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Display chat messages
        for message in st.session_state.messages:
            display_message(message['content'], message['is_user'])
        
        # Chat input with multilingual placeholder
        placeholders = {
            'it': "Cosa vorresti cucinare oggi?",
            'en': "What would you like to cook today?",
            'fr': "Que souhaitez-vous cuisiner aujourd'hui?",
            'es': "¿Qué te gustaría cocinar hoy?",
            'de': "Was möchten Sie heute kochen?",
            'pt': "O que você gostaria de cozinhar hoje?",
            'zh': "你今天想做什么菜？",
            'ja': "今日は何を作りたいですか？",
            'ko': "오늘 무엇을 요리하고 싶으신가요?",
            'ru': "Что бы вы хотели приготовить сегодня?",
            'ar': "ماذا تريد أن تطبخ اليوم؟"
        }
        
        placeholder = placeholders.get(st.session_state.user_language, placeholders['it'])
        user_input = st.chat_input(placeholder)
        
        if user_input:
            # Add user message to chat
            st.session_state.messages.append({
                'content': user_input,
                'is_user': True
            })
            
            # Display user message
            display_message(user_input, is_user=True)
            
            # Process the request
            with st.spinner("Creating your innovative recipe..."):
                final_state = process_recipe_request(user_input, selected_prefs)
            
            if final_state:
                if final_state.get("final_recipe"):
                    # Display the recipe
                    recipe_content = final_state["final_recipe"]
                    
                    # Add recipe to chat
                    st.session_state.messages.append({
                        'content': recipe_content,
                        'is_user': False
                    })
                    
                    # Display recipe in a nice container
                    st.markdown('<div class="recipe-container">', unsafe_allow_html=True)
                    st.markdown("## 🎉 Your innovative recipe")
                    st.markdown(recipe_content)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Add download button
                    st.download_button(
                        label="📥 Download recipe",
                        data=recipe_content,
                        file_name=f"ricetta_{user_input.replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
                    
                elif final_state.get("error_message"):
                    error_msg = final_state["error_message"]
                    st.session_state.messages.append({
                        'content': f"❌ Errore: {error_msg}",
                        'is_user': False
                    })
                    
                    st.markdown('<div class="error-container">', unsafe_allow_html=True)
                    st.error(f"Errore: {error_msg}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                else:
                    error_msg = "I cannot create the recipe you asked. Try to be more specific."
                    st.session_state.messages.append({
                        'content': error_msg,
                        'is_user': False
                    })
                    st.warning(error_msg)
    
    with col2:
        # Recipe suggestions with multilingual support
        st.markdown("### 💡 Suggestions")
        
        # Language-specific suggestions
        suggestions_by_lang = {
            'it': [
                "Pasta alla carbonara fusion",
                "Risotto innovativo", 
                "Pollo con spezie esotiche",
                "Dessert al cioccolato creativo",
                "Insalata gourmet",
                "Pizza con ingredienti inusuali"
            ],
            'en': [
                "Fusion carbonara pasta",
                "Innovative risotto",
                "Chicken with exotic spices", 
                "Creative chocolate dessert",
                "Gourmet salad",
                "Pizza with unusual ingredients"
            ],
            'fr': [
                "Pâtes carbonara fusion",
                "Risotto innovant",
                "Poulet aux épices exotiques",
                "Dessert au chocolat créatif", 
                "Salade gourmet",
                "Pizza aux ingrédients inhabituels"
            ],
            'es': [
                "Pasta carbonara fusión",
                "Risotto innovador",
                "Pollo con especias exóticas",
                "Postre de chocolate creativo",
                "Ensalada gourmet", 
                "Pizza con ingredientes inusuales"
            ],
            'de': [
                "Fusion Carbonara Pasta",
                "Innovatives Risotto",
                "Hähnchen mit exotischen Gewürzen",
                "Kreatives Schokoladendessert",
                "Gourmet Salat",
                "Pizza mit ungewöhnlichen Zutaten"
            ]
        }
        
        current_suggestions = suggestions_by_lang.get(st.session_state.user_language, suggestions_by_lang['it'])
        
        for suggestion in current_suggestions:
            if st.button(suggestion, key=f"suggestion_{suggestion}"):
                # Simulate clicking the suggestion
                st.session_state.messages.append({
                    'content': suggestion,
                    'is_user': True
                })
                st.rerun()
        
        # Statistics
        st.markdown("### 📊 Statistics")
        st.metric("Recipe created", len([m for m in st.session_state.messages if not m['is_user']]))
        st.metric("Total messages", len(st.session_state.messages))
        
        # Tips
        st.markdown("### 💭 Tips")
        st.info("""
        **For better recipes:**
        - Specify your tastes
        - Put your preferred ingredients
        - Specify the meal type
        - Specify preparation time
        """)

if __name__ == "__main__":
    main()