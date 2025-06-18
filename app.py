import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from streamlit_lottie import st_lottie
import requests
import os

# Set your Gemini API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyAOBV-XP98L4tQCXd_sfmbrp2VuLA9o3TA"

# Custom CSS for enhanced UI
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(45deg, #FFB6C1, #FFD700);
        background-size: 400% 400%;
        animation: gradient-animation 15s ease infinite;
    }

    @keyframes gradient-animation {
        0% {background-position: 0% 50%}
        50% {background-position: 100% 50%}
        100% {background-position: 0% 50%}
    }

    .recipe-container {
        padding: 20px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        margin-top: 30px;
        font-family: 'Segoe UI', sans-serif;
        line-height: 1.6;
    }

    .fun-fact-box {
        background-color: #e1f5fe;
        padding: 15px;
        border-left: 8px solid #03a9f4;
        border-radius: 10px;
        font-family: 'Segoe UI', sans-serif;
        font-size: 16px;
        margin-top: 20px;
    }

    h1, h2 {
        text-align: center;
        font-family: 'Segoe UI', sans-serif;
        color: #FF6347;
    }

    .emoji {
        font-size: 40px;
    }

    .input-section {
        background-color: rgba(0, 0, 0, 0.05);
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to load Lottie animations
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load Lottie animations
lottie_cook = load_lottie_url("https://lottie.host/0e899f3d-fa7e-4762-88be-f49dff784df2/BBqoxxx3FB.json")
lottie_ready = load_lottie_url("https://lottie.host/d7cd360a-9ec2-46ba-87f0-65dcb6718cd8/uYbB8p41OA.json")

# Header with animation
st_lottie(lottie_cook, speed=1, height=250, key="cooking_animation")

st.markdown('<h1 class="emoji">🍲 AI Food Recipe Generator 🌮</h1>', unsafe_allow_html=True)
st.markdown("<h2>Enter your main ingredients to get a recipe (e.g., chicken, tomato, spinach)</h2>", unsafe_allow_html=True)

# User input
user_ingredients = st.text_input("Enter your main ingredients (comma-separated) 🍅🥬:")

# Cuisine selection (AFTER ingredient input)
cuisine_option = st.selectbox(
    "Choose a cuisine style 🍽️:",
    ["Indian", "Chinese", "Italian", "Mexican", "Thai", "French"],
    index=0
)

# Save last inputs for retry
if "last_ingredients" not in st.session_state:
    st.session_state.last_ingredients = ""
if "last_cuisine" not in st.session_state:
    st.session_state.last_cuisine = ""

# Recipe generation function
def generate_recipe(ingredients, cuisine):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    prompt = PromptTemplate(
        input_variables=["ingredients", "cuisine"],
        template="""
You are a professional chef AI that also knows about nutrition.

Create a complete {cuisine} main course recipe using only the ingredients: {ingredients}.

Important Rules:
- Avoid adding any extra ingredients.
- Assume basic pantry items (salt, water, oil, sugar, spices) and add only if needed.
- Be creative and ensure the dish feels like authentic {cuisine} cuisine.

Explicitly include the following estimated nutritional information **per serving**:
1. Calories (kcal)
2. Carbohydrates (g)
3. Protein (g)
4. Fat (g)
5. Fiber (g)
6. Sodium (mg)

Output Format:
1. Recipe Title 
2. Ingredients List
3. Preparation Steps (each step marked with a star ★)
4. Estimated Cook Time
5. Nutrient Chart per Serving (Estimated):
    | Nutrient      | Amount   |
    |---------------|----------|
    | Calories      | ___ kcal |
    | Carbohydrates | ___ g    |
    | Protein       | ___ g    |
    | Fat           | ___ g    |
    | Fiber         | ___ g    |
    | Sodium        | ___ mg   |
"""
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run({"ingredients": ingredients, "cuisine": cuisine})

# Fun Fact generator function
def get_fun_fact(ingredients):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    fun_fact_prompt = PromptTemplate(
        input_variables=["ingredients"],
        template="""
You are a fun and informative culinary assistant.

Give me a fun or surprising food fact that involves one or more of these ingredients: {ingredients}.

The fact should be short, interesting, and suitable for general audiences.
Only return the fact in 1–2 lines.
"""
    )
    fact_chain = LLMChain(llm=llm, prompt=fun_fact_prompt)
    return fact_chain.run({"ingredients": ingredients})

# Generate recipe button
if st.button("Generate Recipe 🍽️", key="generate_button"):
    if user_ingredients:
        st.session_state.last_ingredients = user_ingredients
        st.session_state.last_cuisine = cuisine_option
        result = generate_recipe(user_ingredients, cuisine_option)
        fun_fact = get_fun_fact(user_ingredients)

        st.success(f"Here’s your {cuisine_option} recipe! 🍽️")
        st.markdown(f"<div class='recipe-container'>{result}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='fun-fact-box'>🧠 <strong>Fun Food Fact:</strong> {fun_fact}</div>", unsafe_allow_html=True)
        st_lottie(lottie_ready, speed=1, height=200, key="ready_dish")
    else:
        st.warning("Please enter some ingredients! 😕")

# Retry button
if st.session_state.last_ingredients:
    if st.button("Not satisfied? Generate another recipe 🔁", key="retry_button"):
        result = generate_recipe(st.session_state.last_ingredients, st.session_state.last_cuisine)
        fun_fact = get_fun_fact(st.session_state.last_ingredients)

        st.success(f"Here’s another {st.session_state.last_cuisine} recipe! 🍛")
        st.markdown(f"<div class='recipe-container'>{result}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='fun-fact-box'>🧠 <strong>Fun Food Fact:</strong> {fun_fact}</div>", unsafe_allow_html=True)
        st_lottie(lottie_ready, speed=1, height=200, key="ready_dish_2")
