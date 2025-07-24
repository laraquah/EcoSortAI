# app.py (with avatar choice at start, 50pt change cost, themed vouchers & color)
import streamlit as st
import json
import os
import random
import folium
from streamlit_folium import st_folium
from PIL import Image, ImageDraw

# --- Sync Points with Detection Credits from Materials Recognition ---
import pandas as pd

# Fallback if session_state is missing data
if "detection_history" not in st.session_state:
    st.session_state.detection_history = pd.DataFrame(columns=["Timestamp", "Material", "Credits"])

# Sum total points from AI-detected materials
total_ai_points = int(st.session_state.detection_history["Credits"].sum())
user_data["points"] = total_ai_points

# --- Load User Data ---
def load_user_data():
    if os.path.exists("user_data.json"):
        with open("user_data.json", "r") as f:
            return json.load(f)
    return {"points": 100, "avatar": "", "vouchers": []}

def save_user_data(data):
    with open("user_data.json", "w") as f:
        json.dump(data, f, indent=4)

user_data = load_user_data()

# --- Avatar Themes ---
avatar_themes = {
    "water_spirit.png": {
        "name": "Water Spirit 💧",
        "color": "#0077cc",
        "vouchers": ["Free Bubble Tea", "Hydration Bottle", "Iced Coconut"]
    },
    "metal_titan.png": {
        "name": "Metal Titan ⚙️",
        "color": "#555555",
        "vouchers": ["Tool Kit Discount", "Screwdriver Set", "Gadget Wipes"]
    },
    "earth_guardian.png": {
        "name": "Earth Guardian 🌱",
        "color": "#228B22",
        "vouchers": ["Plant Starter Kit", "Compost Bag", "Eco Fertilizer"]
    },
    "balance_seeker.png": {
        "name": "Balance Seeker 🌈",
        "color": "#9932CC",
        "vouchers": ["Rainbow Pouch", "Yoga Pass", "Mood Candle"]
    }
}

# --- Set Theme Colors ---
def set_theme(color):
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: #f0f2f6; }}
        .main h1, .main h2, .main h3 {{ color: {color}; }}
        .st-bb {{ color: {color} !important; }}
        .stButton>button {{ background-color: {color}; color: white; }}
        </style>
        """,
        unsafe_allow_html=True
    )

st.set_page_config(page_title="♻️ AI Recycling Avatar App", layout="centered")

# --- First Time Avatar Selection ---
if not user_data["avatar"]:
    st.title("🎨 Choose Your Avatar")
    avatar_files = os.listdir("avatars")
    selected = st.selectbox("Pick your avatar:", avatar_files, format_func=lambda x: avatar_themes[x]["name"])
    if st.button("Confirm Avatar"):
        user_data["avatar"] = selected
        save_user_data(user_data)
        st.rerun()

# --- Apply Avatar Theme ---
avatar = user_data["avatar"]
avatar_data = avatar_themes.get(avatar, {})
avatar_name = avatar_data.get("name", "")
color = avatar_data.get("color", "#000000")
user_vouchers = avatar_data.get("vouchers", [])
set_theme(color)

# --- Header ---
st.title("♻️ AI Recycling Avatar App")

# --- Show Avatar Info ---
st.subheader(f"Your Avatar: {avatar_name}")
st.image(f"avatars/{avatar}", width=250)
st.markdown(f"**Your Points:** {user_data['points']}")

# --- Avatar Change Section (50 pts) ---
with st.expander("🧝 Change Avatar (Costs 50 pts)"):
    if user_data["points"] < 50:
        st.warning("Not enough points to change avatar!")
    else:
        avatar_files = os.listdir("avatars")
        new_avatar = st.selectbox("Choose a new avatar:", avatar_files, format_func=lambda x: avatar_themes[x]["name"], key="change_avatar")
        if new_avatar == user_data["avatar"]:
            st.info("This is already your current avatar.")
        elif st.button("Confirm Avatar Change"):
            user_data["avatar"] = new_avatar
            user_data["points"] -= 50
            save_user_data(user_data)
            st.success(f"Avatar changed to {avatar_themes[new_avatar]['name']}!")
            st.rerun()

# --- Themed Vouchers ---
st.header("🎁 Redeem Vouchers")

for voucher in user_vouchers:
    if voucher in user_data["vouchers"]:
        st.markdown(f"✅ Already redeemed: {voucher}")
    elif st.button(f"Redeem {voucher}"):
        confirm = st.radio("Confirm?", ["No", "Yes"], key=voucher)
        if confirm == "Yes":
            user_data["vouchers"].append(voucher)
            user_data["points"] -= 10
            code = "VCHR-" + str(random.randint(100000, 999999))
            save_user_data(user_data)
            st.success(f"Redeemed: {voucher}")
            st.code(code, language="text")
            img = Image.new('RGB', (300, 150), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((20, 40), voucher, fill="black")
            draw.text((20, 90), f"Code: {code}", fill="blue")
            st.image(img, caption="Show this at counter", use_column_width=False)
            st.rerun()

# --- Nearest Recycling Bin Map ---
st.header("📍 Find Your Nearest Recycling Bin")
map = folium.Map(location=[1.3521, 103.8198], zoom_start=11)
folium.Marker([1.355, 103.82], tooltip="Recycling Point - Block 123").add_to(map)
folium.Marker([1.35, 103.83], tooltip="Recycling Point - Green Mall").add_to(map)
st_folium(map, width=700, height=500)
