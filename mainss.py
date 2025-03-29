import streamlit as st
import requests
import google.generativeai as genai
from streamlit_lottie import st_lottie
from api_key_gift import api_keys  # Ensure this file contains your API key
import os

genai.configure(api_key=api_keys)

def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        return None

HUGGINGFACE_API_KEY = "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"

# Function to generate an image from text using Stable Diffusion v2.1
def generate_gift_image(gift_name):
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {"inputs": f"A cute, high-quality, aesthetically pleasing image of {gift_name}"}

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200 and response.content:
        return response.content  # Return image bytes
    else:
        st.error(f"❌ Failed to generate image. Status Code: {response.status_code}")
        return None

# Function to Generate AI Gift Recommendations
def get_gift_recommendations(age, hobbies, occasion, budget):
    user_prompt = f"""
    Suggest 5 gift items for a {age}-year-old who likes {hobbies}. 
    The occasion is {occasion}, and the budget is between ${budget[0]} and ${budget[1]}. 
    Provide only the names of the items, without descriptions.
    """
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
        response = model.generate_content([user_prompt])
        return response.text.strip().split("\n")[:5]  # Limit to 5 recommendations
    except Exception as e:
        return [f"⚠ Error: {e}"]

# Streamlit UI Setup
st.set_page_config(page_title="🎁 GiftGennie", page_icon="🎀", layout="wide")

# Load Lottie Animation
lottie_gift = load_lottie_url("https://lottie.host/82a1cb36-1dff-4956-87b3-e8fb93497455/4hV9ihdLR6.json")

# UI Header
st.title("🎁 GiftGennie")
st.subheader("Find the perfect gift in a fun and interactive way!")

col1, col2 = st.columns(2)
with col1:
    if lottie_gift:
        st_lottie(lottie_gift, height=300, key="gift")
    else:
        st.image("https://source.unsplash.com/600x400/?gift,happy", caption="Surprise Gifts!")

with col2:
    st.write("💡 *How it Works?*")
    st.write("1️⃣ Select recipient details")
    st.write("2️⃣ Choose an occasion & budget")
    st.write("3️⃣ Click 'Find Gifts' to see recommendations!")

# Sidebar for User Input
st.sidebar.header("🎀 Customize Your Search")
name = st.sidebar.text_input("Recipient's Name")
age = st.sidebar.slider("🎂 Age", 1, 100, 25)
hobbies = st.sidebar.text_area("🎨 Hobbies & Interests")
occasion = st.sidebar.selectbox("🎉 Occasion", ["Birthday", "Anniversary", "Festival", "Wedding", "Graduation", "Other"])
budget = st.sidebar.slider("💰 Budget ($)", 10, 1000, (50, 300))

# Initialize session state for reserved gifts
if "reserved_gifts" not in st.session_state:
    st.session_state.reserved_gifts = []

# Generate Gift Recommendations
gift_list = []
if st.sidebar.button("Find Gifts 🎁"):
    with st.spinner(f"🔍 Finding the best gifts for {name}..."):
        gift_list = get_gift_recommendations(age, hobbies, occasion, budget)
        
        if "⚠ Error" not in gift_list[0]:  # Ensure response is valid
            st.success(f"🎀 Here are some AI-generated gift ideas for {name}:")
            
            for gift in gift_list:
                image_data = generate_gift_image(gift)  # Generate image using Hugging Face
                col1, col2 = st.columns([1, 3])
                with col1:
                    if image_data:
                        st.image(image_data, width=150, caption=gift)
                    else:
                        st.warning("🚫 Image not available")
                with col2:
                    amazon_url = f"https://www.amazon.com/s?k={gift.replace(' ', '+')}&tag=your-affiliate-id"
                    st.markdown(f"🔗 [Buy {gift} on Amazon]({amazon_url})")
                    if st.button(f"Reserve {gift}", key=gift):
                        if gift not in st.session_state.reserved_gifts:
                            st.session_state.reserved_gifts.append(gift)
                        st.experimental_rerun()

# Sidebar Reserved Gifts Card
st.sidebar.subheader("🛍️ Reserved Gifts")
if st.session_state.reserved_gifts:
    for reserved_gift in st.session_state.reserved_gifts:
        with st.sidebar.expander(f"🎁 {reserved_gift}"):
            image_data = generate_gift_image(reserved_gift)
            if image_data:
                st.image(image_data, width=100)
            else:
                st.warning("🚫 Image not available")
            amazon_url = f"https://www.amazon.com/s?k={reserved_gift.replace(' ', '+')}&tag=your-affiliate-id"
            st.markdown(f"🔗 [Buy {reserved_gift} on Amazon]({amazon_url})")
