import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from streamlit_lottie import st_lottie
import requests
import os
import pandas as pd

# Set your Gemini API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyAOBV-XP98L4tQCXd_sfmbrp2VuLA9o3TA"

# Initialize session state
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "user_health_data" not in st.session_state:
    st.session_state.user_health_data = {}

# Custom CSS for enhanced UI
def load_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #FAFAF8, #F5FCFF);
            font-family: 'Segoe UI', sans-serif;
        }

        /* Home Page Styles */
        .main-title {
            text-align: center;
            font-size: 3.5em;
            color: #A8D5BA;
            font-weight: bold;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }

        .main-subtitle {
            text-align: center;
            font-size: 1.3em;
            color: #666;
            margin-bottom: 40px;
            font-style: italic;
        }

        .feature-card {
            background: linear-gradient(135deg, #FFFFFF, #F8F9FA);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            border-left: 6px solid #A8D5BA;
            transition: transform 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }

        .feature-title {
            font-size: 1.8em;
            color: #A8D5BA;
            font-weight: bold;
            margin-bottom: 15px;
        }

        .feature-description {
            color: #333333;
            line-height: 1.6;
            font-size: 1.1em;
        }

        /* ChefMate Styles */
        .chefmate-bg {
            background: linear-gradient(45deg, #FFB6B9, #FFE0AC);
            background-size: 400% 400%;
            animation: gradient-animation 15s ease infinite;
        }

        .chefmate-container {
            padding: 20px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            margin-top: 30px;
            line-height: 1.6;
        }

        .chefmate-title {
            text-align: center;
            color: #FFB6B9;
            font-size: 2.5em;
            margin-bottom: 20px;
        }

        /* WellBit Styles */
        .wellbit-bg {
            background: linear-gradient(135deg, #F4FFF8, #B9E3C6);
        }

        .wellbit-container {
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }

        .wellbit-title {
            text-align: center;
            color: #B9E3C6;
            font-size: 2.5em;
            margin-bottom: 20px;
        }

        .nutrition-table {
            background: #F4FFF8;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }

        /* PlatePlanner Styles */
        .plateplanner-bg {
            background: linear-gradient(135deg, #F5FCFF, #A0CED9);
        }

        .plateplanner-container {
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }

        .plateplanner-title {
            text-align: center;
            color: #A0CED9;
            font-size: 2.5em;
            margin-bottom: 20px;
        }

        .meal-plan-table {
            background: #F5FCFF;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }

        /* Common Styles */
        .fun-fact-box {
            background: linear-gradient(135deg, #e1f5fe, #b3e5fc);
            padding: 20px;
            border-left: 8px solid #03a9f4;
            border-radius: 10px;
            font-size: 16px;
            margin-top: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .back-button {
            background: linear-gradient(135deg, #A8D5BA, #B9E3C6);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            cursor: pointer;
            margin-bottom: 20px;
        }

        @keyframes gradient-animation {
            0% {background-position: 0% 50%}
            50% {background-position: 100% 50%}
            100% {background-position: 0% 50%}
        }

        .stButton > button {
            background: linear-gradient(135deg, #A8D5BA, #B9E3C6);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            font-weight: bold;
            font-size: 16px;
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Function to load Lottie animations
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# BMR and TDEE calculation functions
def calculate_bmr(gender, age, height, weight):
    if gender.lower() == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return bmr

def calculate_tdee(bmr, activity_level):
    activity_multipliers = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725
    }
    return bmr * activity_multipliers.get(activity_level, 1.2)

# Home Page
def show_home_page():
    st.markdown('<div class="main-title">🍽️ Smart Bite Hub</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Eat Well, Plan Smart, Live Healthy</div>', unsafe_allow_html=True)
    
    # ChefMate Card
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🍳 ChefMate</div>
        <div class="feature-description">
            Get instant recipes based on ingredients you already have at home. 
            Just enter what's in your kitchen and ChefMate will whip up a personalized, 
            nutritious recipe in seconds.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🍳 Launch ChefMate", key="chefmate_btn"):
        st.session_state.current_page = "chefmate"
        st.rerun()
    
    # PlatePlanner Card
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📅 PlatePlanner</div>
        <div class="feature-description">
            Plan your week's meals with ease. Choose your diet type, select cuisines 
            for each day or meal, and include non-veg preferences to build a custom, 
            balanced weekly meal plan.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📅 Launch PlatePlanner", key="plateplanner_btn"):
        st.session_state.current_page = "plateplanner"
        st.rerun()
    
    # WellBit Card
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">💪 WellBit</div>
        <div class="feature-description">
            Know what your body needs. Enter basic health info like gender, height, 
            and weight to get daily nutrition goals and ingredient suggestions rich 
            in protein, iron, fiber, and more.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("💪 Launch WellBit", key="wellbit_btn"):
        st.session_state.current_page = "wellbit"
        st.rerun()

# ChefMate Page
def show_chefmate_page():
    st.markdown('<div class="chefmate-bg">', unsafe_allow_html=True)
    st.markdown('<div class="chefmate-title">🍳 ChefMate</div>', unsafe_allow_html=True)
    
    if st.button("🏠 Back to Home", key="back_from_chefmate"):
        st.session_state.current_page = "home"
        st.rerun()
    
    # Load Lottie animations
    lottie_cook = load_lottie_url("https://lottie.host/0e899f3d-fa7e-4762-88be-f49dff784df2/BBqoxxx3FB.json")
    lottie_ready = load_lottie_url("https://lottie.host/d7cd360a-9ec2-46ba-87f0-65dcb6718cd8/uYbB8p41OA.json")
    
    if lottie_cook:
        st_lottie(lottie_cook, speed=1, height=200, key="cooking_animation")
    
    st.markdown("<h3 style='text-align: center; color: #666;'>Enter your ingredients to get a personalized recipe</h3>", unsafe_allow_html=True)
    
    # User inputs
    col1, col2 = st.columns(2)
    
    with col1:
        user_ingredients = st.text_input("🍅 Enter ingredients (comma-separated):", 
                                       placeholder="e.g., chicken, tomato, spinach")
        cuisine_option = st.selectbox("🍽️ Choose cuisine style:", 
                                    ["South Indian", "North Indian", "Chinese", "Italian", "Mexican", "Thai", "French"])
    
    with col2:
        portions = st.number_input("👥 Number of portions:", min_value=1, max_value=10, value=2)
    
    # Save last inputs for retry
    if "last_ingredients" not in st.session_state:
        st.session_state.last_ingredients = ""
    if "last_cuisine" not in st.session_state:
        st.session_state.last_cuisine = ""
    if "last_portions" not in st.session_state:
        st.session_state.last_portions = 2
    
    # Recipe generation
    def generate_recipe(ingredients, cuisine, portions):
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        prompt = PromptTemplate(
            input_variables=["ingredients", "cuisine", "portions"],
            template="""
You are a professional chef AI that also knows about nutrition.

Create a complete {cuisine} main course recipe using the ingredients: {ingredients} for {portions} portions.

Important Rules:
- Use the given ingredients as main components
- Assume basic pantry items (salt, water, oil, sugar, common spices) are available
- Make it authentic {cuisine} cuisine
- Scale the recipe for {portions} portions

Format your response as:
🍽️ Recipe Title:

📝 Ingredients:
(List all ingredients with quantities for {portions} portions)

👨‍🍳 Preparation Steps:
★ Step 1: [detailed instruction]
★ Step 2: [detailed instruction]
★ Step 3: [detailed instruction]
(continue with all steps)

⏲️ Estimated Cook Time: [time]

📊 Nutrition per Serving:
| Nutrient | Amount |
|----------|---------|
| Calories | ___ kcal |
| Protein | ___ g |
| Carbs | ___ g |
| Fat | ___ g |
| Fiber | ___ g |
| Sodium | ___ mg |
"""
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        return chain.run({"ingredients": ingredients, "cuisine": cuisine, "portions": portions})
    
    def get_fun_fact(ingredients):
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        prompt = PromptTemplate(
            input_variables=["ingredients"],
            template="Give me a fun, interesting food fact about one of these ingredients: {ingredients}. Keep it to 1-2 sentences."
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        return chain.run({"ingredients": ingredients})
    
    # Generate recipe button
    if st.button("🍽️ Generate Recipe", key="generate_recipe_btn"):
        if user_ingredients:
            with st.spinner("Cooking up something delicious..."):
                st.session_state.last_ingredients = user_ingredients
                st.session_state.last_cuisine = cuisine_option
                st.session_state.last_portions = portions
                
                result = generate_recipe(user_ingredients, cuisine_option, portions)
                fun_fact = get_fun_fact(user_ingredients)
                
                st.success(f"Here's your {cuisine_option} recipe for {portions} portions! 🍽️")
                st.markdown(f"<div class='chefmate-container'>{result}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='fun-fact-box'>🧠 <strong>Fun Food Fact:</strong> {fun_fact}</div>", unsafe_allow_html=True)
                
                if lottie_ready:
                    st_lottie(lottie_ready, speed=1, height=150, key="ready_dish")
        else:
            st.warning("Please enter some ingredients! 😕")
    
    # Retry button
    if st.session_state.last_ingredients:
        if st.button("🔁 Generate Another Recipe", key="retry_recipe_btn"):
            with st.spinner("Creating a new recipe..."):
                result = generate_recipe(st.session_state.last_ingredients, 
                                       st.session_state.last_cuisine, 
                                       st.session_state.last_portions)
                fun_fact = get_fun_fact(st.session_state.last_ingredients)
                
                st.success(f"Here's another {st.session_state.last_cuisine} recipe! 🍛")
                st.markdown(f"<div class='chefmate-container'>{result}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='fun-fact-box'>🧠 <strong>Fun Food Fact:</strong> {fun_fact}</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# WellBit Page
def show_wellbit_page():
    st.markdown('<div class="wellbit-bg">', unsafe_allow_html=True)
    st.markdown('<div class="wellbit-title">💪 WellBit</div>', unsafe_allow_html=True)
    
    if st.button("🏠 Back to Home", key="back_from_wellbit"):
        st.session_state.current_page = "home"
        st.rerun()
    
    st.markdown("<h3 style='text-align: center; color: #666;'>Calculate your daily nutrition requirements</h3>", unsafe_allow_html=True)
    
    st.markdown('<div class="wellbit-container">', unsafe_allow_html=True)
    
    # User input form
    col1, col2 = st.columns(2)
    
    with col1:
        gender = st.selectbox("👤 Gender:", ["Male", "Female", "Other"])
        age = st.number_input("🎂 Age (years):", min_value=13, max_value=100, value=25)
        height = st.number_input("📏 Height (cm):", min_value=100, max_value=250, value=170)
    
    with col2:
        weight = st.number_input("⚖️ Weight (kg):", min_value=30, max_value=200, value=70)
        activity_level = st.selectbox("🏃 Activity Level:", 
                                    ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
        diet_preference = st.selectbox("🥗 Diet Preference:", ["Vegetarian", "Non-Vegetarian", "Vegan"])
    
    if st.button("📊 Calculate Nutrition Needs", key="calculate_nutrition_btn"):
        with st.spinner("Calculating your nutrition requirements..."):
            # Calculate BMR and TDEE
            bmr = calculate_bmr(gender, age, height, weight)
            tdee = calculate_tdee(bmr, activity_level)
            
            # Calculate nutrition requirements
            protein_req = weight * 0.8  # 0.8g per kg body weight
            fiber_req = 25 if gender.lower() == 'female' else 38  # Daily fiber requirement
            iron_req = 18 if gender.lower() == 'female' else 8  # Daily iron requirement
            
            # Store user data for meal planning integration
            st.session_state.user_health_data = {
                'calories': int(tdee),
                'protein': int(protein_req),
                'fiber': int(fiber_req),
                'iron': int(iron_req),
                'diet_preference': diet_preference
            }
            
            # Display results
            st.success("Here are your personalized nutrition requirements! 💪")
            
            # Nutrition table
            nutrition_data = {
                'Nutrient': ['Calories', 'Protein', 'Fiber', 'Iron'],
                'Daily Requirement': [f'{int(tdee)} kcal', f'{int(protein_req)} g', f'{fiber_req} g', f'{iron_req} mg']
            }
            
            df = pd.DataFrame(nutrition_data)
            st.markdown('<div class="nutrition-table">', unsafe_allow_html=True)
            st.table(df)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Get ingredient suggestions using AI
            def get_ingredient_suggestions(diet_preference, protein_req, fiber_req, iron_req):
                llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
                prompt = PromptTemplate(
                    input_variables=["diet_preference", "protein_req", "fiber_req", "iron_req"],
                    template="""
Based on a {diet_preference} diet, suggest ingredients rich in:
- Protein (need {protein_req}g daily)
- Fiber (need {fiber_req}g daily) 
- Iron (need {iron_req}mg daily)

Provide 3-4 ingredients for each nutrient category with brief benefits.

Format:
🥩 High Protein Ingredients:
- [ingredient]: [brief benefit]

🌾 High Fiber Ingredients:
- [ingredient]: [brief benefit]

🩸 High Iron Ingredients:
- [ingredient]: [brief benefit]
"""
                )
                chain = LLMChain(llm=llm, prompt=prompt)
                return chain.run({
                    "diet_preference": diet_preference,
                    "protein_req": protein_req,
                    "fiber_req": fiber_req,
                    "iron_req": iron_req
                })
            
            suggestions = get_ingredient_suggestions(diet_preference, protein_req, fiber_req, iron_req)
            
            st.markdown("### 🥗 Recommended Ingredients for Your Diet")
            st.markdown(f"<div class='wellbit-container'>{suggestions}</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# PlatePlanner Page
def show_plateplanner_page():
    st.markdown('<div class="plateplanner-bg">', unsafe_allow_html=True)
    st.markdown('<div class="plateplanner-title">📅 PlatePlanner</div>', unsafe_allow_html=True)
    
    if st.button("🏠 Back to Home", key="back_from_plateplanner"):
        st.session_state.current_page = "home"
        st.rerun()
    
    st.markdown("<h3 style='text-align: center; color: #666;'>Plan your weekly meals effortlessly</h3>", unsafe_allow_html=True)
    
    st.markdown('<div class="plateplanner-container">', unsafe_allow_html=True)
    
    # Planning options
    col1, col2 = st.columns(2)
    
    with col1:
        diet_type = st.selectbox("🥗 Diet Type:", ["Vegetarian", "Non-Vegetarian", "Mixed"])
        
        if diet_type == "Mixed":
            nonveg_days = st.number_input("🍖 Non-veg days per week:", min_value=1, max_value=7, value=3)
        else:
            nonveg_days = 7 if diet_type == "Non-Vegetarian" else 0
    
    with col2:
        planning_type = st.selectbox("📋 Planning Type:", ["Same cuisine for whole week", "Different cuisine each day"])
        
        if planning_type == "Same cuisine for whole week":
            weekly_cuisine = st.selectbox("🍽️ Choose cuisine for the week:", 
                                        ["South Indian", "North Indian", "Chinese", "Italian", "Mexican", "Thai", "French"])
        
        portions = st.number_input("👥 Number of portions per meal:", min_value=1, max_value=10, value=2)
        health_integration = st.checkbox("💪 Use WellBit health data (if available)")
    
    if st.button("📅 Generate Meal Plan", key="generate_meal_plan_btn"):
        with st.spinner("Creating your personalized meal plan..."):
            
            def generate_meal_plan(diet_type, nonveg_days, planning_type, weekly_cuisine=None, health_data=None, portions=2):
                llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
                
                if health_data and health_integration:
                    health_context = f"Focus on ingredients that help meet daily goals: {health_data['calories']} calories, {health_data['protein']}g protein, {health_data['fiber']}g fiber, {health_data['iron']}mg iron."
                else:
                    health_context = "Focus on balanced, nutritious meals."
                
                if planning_type == "Same cuisine for whole week":
                    prompt = PromptTemplate(
                        input_variables=["diet_type", "nonveg_days", "cuisine", "health_context", "portions"],
                        template="""
Create a 7-day meal plan with {cuisine} cuisine for {portions} portions per meal.

Diet type: {diet_type}
Non-veg days: {nonveg_days} days per week
Health focus: {health_context}
Portions: {portions} per meal

IMPORTANT: If cuisine is "South Indian", focus on South Indian dishes like:
Suggest South Indian meals for the following:

🥣 Breakfast options:
- Ragi Idli
- Kambu Kichadi (Pearl Millet Upma)
- Varagu Pongal (Little Millet Pongal)
- Thinai Dosa (Foxtail Millet)
- Navadhanya Adai (9-Grain Lentil Pancake)
- Murungai Keerai Dosa (Drumstick Leaf Dosa)
- Vegetable Uthappam
- Keerai Paniyaram (Leafy Appe)
- Horse Gram Upma
- Kambu Kool (Fermented Pearl Millet Gruel)

🍛 Lunch sets (include rice, curry, dal, poriyal/kootu):
- Kootanchoru with Aviyal and Appalam  
- Red Rice with Murungai Keerai Sambar + Beans Poriyal + Curd  
- Karuveppilai Kuzhambu + Chow Chow Kootu + Brown Rice  
- Sundakkai Vathal Kulambu + Avarakkai Poriyal + Rasam  
- Millet Rice with Manathakkali Keerai Kootu + Pickle  
- Saamai (Little Millet) with Paruppu Rasam + Banana Stem Poriyal  
- Kuzhi Paniyaram with Tomato Chutney + Buttermilk  

🌙 Dinner options:
- Broken Wheat Upma  
- Millet Pongal (Kodo/Thinai)  
- Ragi Dosa  
- Vegetable Sevai  
- Vendhaya Kanji (Fenugreek Porridge)  
- Puzhungal Arisi Kanji (Boiled rice porridge)  
- Kambu Kool (Light pearl millet porridge)  
- Thuthuvalai Rasam with Hot Rice  

- Traditional South Indian vegetables and preparations

If cuisine is "North Indian", focus on North Indian dishes like:
- Parathas, Chole Bhature, Poha for breakfast  
- Dal, Sabzi, Roti, Rice, Rajma, Paneer dishes
- Tandoori items, Butter-based gravies

For each day, provide:
- Day name
- Breakfast, Lunch, Dinner suggestions (scaled for {portions} portions)
- Indicate if meal is Veg/Non-Veg
- Include authentic {cuisine} dish names
- Keep it simple and practical

Format as a clear weekly schedule.
"""
                    )
                    return LLMChain(llm=llm, prompt=prompt).run({
                        "diet_type": diet_type,
                        "nonveg_days": nonveg_days,
                        "cuisine": weekly_cuisine,
                        "health_context": health_context,
                        "portions": portions
                    })
                else:
                    prompt = PromptTemplate(
                        input_variables=["diet_type", "nonveg_days", "health_context", "portions"],
                        template="""
Create a 7-day meal plan with different cuisines each day for {portions} portions per meal.

Diet type: {diet_type}
Non-veg days: {nonveg_days} days per week
Health focus: {health_context}
Portions: {portions} per meal

For each day, suggest:
- A different cuisine (South Indian, North Indian, Chinese, Italian, Mexican, Thai, French, etc.)
- Breakfast, Lunch, Dinner from that cuisine (scaled for {portions} portions)
- Indicate if meal is Veg/Non-Veg
- Include authentic dish names from each cuisine
- Keep it varied and interesting

IMPORTANT: When suggesting Indian cuisine days, specify whether it's South Indian or North Indian and include appropriate dishes:
- South Indian: Suggest South Indian meals for the following:

🥣 Breakfast options:
- Ragi Idli
- Kambu Kichadi (Pearl Millet Upma)
- Varagu Pongal (Little Millet Pongal)
- Thinai Dosa (Foxtail Millet)
- Navadhanya Adai (9-Grain Lentil Pancake)
- Murungai Keerai Dosa (Drumstick Leaf Dosa)
- Vegetable Uthappam
- Keerai Paniyaram (Leafy Appe)
- Horse Gram Upma
- Kambu Kool (Fermented Pearl Millet Gruel)
- lemon rice 

🍛 Lunch sets (include rice, curry, dal, poriyal/kootu):
- Kootanchoru with Aviyal and Appalam  
- Red Rice with Murungai Keerai Sambar + Beans Poriyal + Curd  
- Karuveppilai Kuzhambu + Chow Chow Kootu + Brown Rice  
- Sundakkai Vathal Kulambu + Avarakkai Poriyal + Rasam  
- Millet Rice with Manathakkali Keerai Kootu + Pickle  
- Saamai (Little Millet) with Paruppu Rasam + Banana Stem Poriyal  
- Kuzhi Paniyaram with Tomato Chutney + Buttermilk  

🌙 Dinner options:
- Broken Wheat Upma  
- Millet Pongal (Kodo/Thinai)  
- Ragi Dosa  
- Vegetable Sevai  
- Vendhaya Kanji (Fenugreek Porridge)  
- Puzhungal Arisi Kanji (Boiled rice porridge)  
- Kambu Kool (Light pearl millet porridge)  
- Thuthuvalai Rasam with Hot Rice  
- poori with potato masal

- North Indian: Parathas, Dal, Sabzi, Paneer dishes, Tandoori items

Format as a clear weekly schedule with cuisine themes.
"""
                    )
                    return LLMChain(llm=llm, prompt=prompt).run({
                        "diet_type": diet_type,
                        "nonveg_days": nonveg_days,
                        "health_context": health_context,
                        "portions": portions
                    })
            
            # Get health data if available
            health_data = st.session_state.user_health_data if health_integration and st.session_state.user_health_data else None
            
            meal_plan = generate_meal_plan(diet_type, nonveg_days, planning_type, weekly_cuisine, health_data, portions)
            
            st.success("Here's your personalized weekly meal plan! 📅")
            st.markdown(f"<div class='meal-plan-table'>{meal_plan}</div>", unsafe_allow_html=True)
            
            if health_data and health_integration:
                st.info("✅ This meal plan is optimized based on your WellBit health profile!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Main app logic
def main():
    st.set_page_config(
        page_title="Smart Bite Hub",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    load_css()
    
    # Navigation
    if st.session_state.current_page == "home":
        show_home_page()
    elif st.session_state.current_page == "chefmate":
        show_chefmate_page()
    elif st.session_state.current_page == "wellbit":
        show_wellbit_page()
    elif st.session_state.current_page == "plateplanner":
        show_plateplanner_page()

if __name__ == "__main__":
    main() 