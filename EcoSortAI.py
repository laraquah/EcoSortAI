import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from ultralytics import YOLO
from PIL import Image, ImageDraw
import numpy as np

import os, json, random, cv2, time
import folium
from streamlit_folium import st_folium
# 🚀 App Logo (Left Side)
st.sidebar.image("ecosort_logo3.png", width=450)

# ✅ Store Checkbox Value in Session State
if "accepted_terms" not in st.session_state:
    st.session_state.accepted_terms = False

# ✅ Initialize detection counts & history
if "detection_count" not in st.session_state:
    st.session_state.detection_count = {"Cardboard": 0, "Metal": 0, "Paper": 0, "Plastic": 0}

if "detection_history" not in st.session_state:
    st.session_state.detection_history = pd.DataFrame(columns=["Timestamp", "Material", "Credits"])

if "webcam_active" not in st.session_state:
    st.session_state.webcam_active = False

# ✅ Dropdown Menu with Tabs
menu = st.sidebar.selectbox("Navigation", ["Terms & Conditions", "Ecosort's Overview", "Waste Tracking", "Materials Recognition", "Eco Gallery", "EcoPoints Redemption"])

# ✅ Terms & Conditions Tab
if menu == "Terms & Conditions":
    st.header("📜 Terms & Conditions")

    terms_text = """
    **Ecosort Terms & Conditions**
    
    _Last Updated: May 2025_
    
    ### **1️⃣ Data Protection & Privacy**
    - **Data Encryption:** All images and sensor data used for sorting are encrypted to protect user privacy.
    - **Secure Data Storage:** Sorting records are securely stored to prevent unauthorized access or accidental loss.
    - **Privacy Compliance:** No personal data is recorded—sorting reports contain only general recycling statistics.
    
    ### **2️⃣ Authorized Access & Security**
    - **Authentication Protocols:** Only authorized personnel (e.g., town council staff) can access system settings.
    - **User Access:** Residents can view basic stats, but only designated staff can modify sorting configurations.
    - **Secure Data Transfer:** All data exchanged between smart bins and the main system is encrypted for security.
    
    ### **3️⃣ System Reliability & Accuracy**
    - **Accurate Sorting:** The system ensures items are classified correctly, even if they are slightly damaged or dirty.
    - **Consistency:** Sorting accuracy is maintained regardless of environmental conditions (e.g., day/night, object size).
    - **Supports Recycling:** Proper sorting increases the likelihood that recyclable materials are reused instead of wasted.
    
    ### **4️⃣ Transparency & Environmental Responsibility**
    - **Transparency:** The system provides clear feedback, allowing users to track recycling performance and improvements.
    - **Environmental Responsibility:** Encourages responsible waste disposal, promoting sustainability in the community.
    - **Data Backup:** Sorting history is backed up regularly to ensure continuity, even in the event of system outages.
    
    ### **5️⃣ Acceptance of Terms**
    By using the Ecosort system, you agree to:  
    ✅ Respect the security measures in place.  
    ✅ Accept that data privacy is prioritized.  
    ✅ Follow proper recycling practices to support environmental efforts.
    """

    # ✅ Display Hardcoded Terms (Users CANNOT Edit)
    st.markdown(terms_text)
 

    # ✅ Checkbox to Accept Terms
    if st.checkbox("I Accept the Terms & Conditions", value=st.session_state.accepted_terms):
        st.session_state.accepted_terms = True
        st.success("✅ You can now access other tabs!")


if menu == "Ecosort's Overview":
    if not st.session_state.accepted_terms:
        st.warning("⚠️ You must accept the terms to access this page!")
    else:
        st.header("📊 Ecosort Overview - Monthly Snapshot")

        # 🚀 Select Month
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        selected_month = st.selectbox("📅 Select Month", months, index=4)

        # ✅ Detection Data
        df = pd.DataFrame(list(st.session_state.detection_count.items()), columns=["Material", "Count"])
        total = df["Count"].sum()
        top_material = df.loc[df["Count"].idxmax(), "Material"] if not df.empty else "None"

        # 📊 Metrics Summary
        st.markdown("### 📈 Quick Stats")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Items Detected", total)
        col2.metric("Top Material", top_material)
        col3.metric("Unique Materials", df.shape[0])

        # 🎨 Live Bar Chart (Styled)
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = {"Cardboard": "#66bb6a", "Metal": "#fdd835", "Paper": "#ef5350", "Plastic": "#42a5f5"}
        bars = ax.bar(df["Material"], df["Count"], color=[colors.get(m, "#9e9e9e") for m in df["Material"]])

        ax.set_ylabel("🔢 Detection Count", fontsize=12)
        ax.set_title(f"📦 Detected Materials in {selected_month}", fontsize=14)
        ax.set_facecolor("#f9f9f9")
        fig.patch.set_facecolor("#f9f9f9")

        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}', xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha='center', fontsize=10)

        st.pyplot(fig)

        # ℹ️ Optional Legend
        with st.expander("ℹ️ What Each Color Means"):
            for mat, col in colors.items():
                st.markdown(f"- <span style='color:{col}'>●</span> **{mat}**", unsafe_allow_html=True)


# ✅ Waste Tracking Tab (Live Line Graph & Table)
if menu == "Waste Tracking":
    if not st.session_state.accepted_terms:
        st.warning("⚠️ You must accept the terms to access this page!")
    else:
        st.header("♻️ Waste Tracking Dashboard")

        st.markdown("Track how your detected materials are contributing to recycling rewards and environmental impact over time.")

        # 📊 Summary Metrics
        if not st.session_state.detection_history.empty:
            total_credits = st.session_state.detection_history["Credits"].sum()
            total_detections = len(st.session_state.detection_history)
            unique_materials = st.session_state.detection_history["Material"].nunique()
        else:
            total_credits = 0
            total_detections = 0
            unique_materials = 0

        col1, col2, col3 = st.columns(3)
        col1.metric("🏅 Total Credits Earned", f"{total_credits}")
        col2.metric("📦 Total Detections", f"{total_detections}")
        col3.metric("🧾 Materials Detected", f"{unique_materials}")

        st.divider()

        # 🚀 Dynamic Line Graph (Live Credit Tracking)
        st.markdown("### 📈 Material Deposits Over Time")

        fig, ax = plt.subplots(figsize=(8, 5))
        colors = {"Cardboard": "#66bb6a", "Metal": "#fdd835", "Paper": "#ef5350", "Plastic": "#42a5f5"}

        for material in st.session_state.detection_count.keys():
            material_data = st.session_state.detection_history[
                st.session_state.detection_history["Material"] == material
            ]
            if not material_data.empty:
                ax.plot(
                    material_data.index,
                    material_data["Credits"].cumsum(),
                    label=material,
                    linewidth=2,
                    color=colors.get(material, "#9e9e9e"),
                )

        ax.set_ylabel("Total Credits", fontsize=12)
        ax.set_xlabel("Detection Event Index", fontsize=12)
        ax.set_title("📊 Credit Accumulation by Material", fontsize=14)
        ax.legend(loc="upper left")
        ax.grid(True, linestyle="--", alpha=0.3)
        fig.patch.set_facecolor("#f9f9f9")
        ax.set_facecolor("#f9f9f9")

        st.pyplot(fig)

        st.divider()

        # 📋 Material Detection Table
        st.markdown("### 📋 Detected Materials Log")

        if not st.session_state.detection_history.empty:
            st.session_state.detection_history["Timestamp"] = pd.to_datetime(
                st.session_state.detection_history["Timestamp"], errors="coerce"
            )
            st.session_state.detection_history.dropna(subset=["Timestamp"], inplace=True)
            st.session_state.detection_history["Date"] = st.session_state.detection_history["Timestamp"].dt.date
            st.session_state.detection_history["Time"] = st.session_state.detection_history["Timestamp"].dt.time
            formatted_history = st.session_state.detection_history[["Date", "Time", "Material", "Credits"]]
        else:
            formatted_history = pd.DataFrame(columns=["Date", "Time", "Material", "Credits"])

        st.dataframe(formatted_history, use_container_width=True)

# 🖼️ EcoGallery Feature
def run_eco_gallery():
    if not st.session_state.get("accepted_terms"):
        st.warning("⚠️ You must accept the terms to access this page!")
        return

    # Load YOLO model once
    model = YOLO("train33/weights/best.pt")
        
    # Detect material from image array
    def detect_material_from_frame(img_array):
        results = model(img_array)[0]
        if results.names and results.boxes:
            class_id = int(results.boxes.cls[0])
            return results.names[class_id]
        else:
            return "unknown"

    st.header("🖼️ EcoGallery")
    st.markdown("Snap a photo of a recyclable item using your external camera!")
    st.info("🤖 If the material was detected incorrectly, help us train the AI by labeling it correctly below!")
        
    # Initialize session state for image capture
    if "captured_image" not in st.session_state:
        st.session_state.captured_image = None
        
    # Button to trigger image capture
    if st.button("📸 Open Camera and Take Photo"):
        cap = cv2.VideoCapture(1)  # use external camera (index 1)
        if not cap.isOpened():
            st.error("❌ Could not open camera 1. Make sure your external webcam is connected.")
            return
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            st.error("❌ Failed to capture image.")
            return
        
        # Convert BGR to RGB and store in session state
        st.session_state.captured_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
    # Display captured image
    if st.session_state.captured_image is not None:
        st.image(st.session_state.captured_image, caption="📷 Captured Image", channels="RGB")
        
        # Detect material
        detected_material = detect_material_from_frame(st.session_state.captured_image)
        st.write(f"🤖 Detected: **{detected_material.upper()}**")
        
        # User correction
        correct_label = st.selectbox("What is the correct material?", ["cardboard", "metal", "paper", "plastic"])
        if st.button("Submit to Dataset"):
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{correct_label}_{timestamp}.jpg"
            save_path = os.path.join("eco_gallery_dataset", correct_label, filename)
        
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            cv2.imwrite(save_path, cv2.cvtColor(st.session_state.captured_image, cv2.COLOR_RGB2BGR))
            st.success(f"✅ Image saved to dataset under: {correct_label}")
            st.session_state.captured_image = None  # reset after saving
# ✅ Run only if this menu item is selected
if menu == "Eco Gallery":
    run_eco_gallery()

# ✅ Materials Recognition Tab (Live YOLO Detection & Image Saving)
if menu == "Materials Recognition":
    if not st.session_state.accepted_terms:
        st.warning("⚠️ You must accept the terms to access this page!")
    else:
        st.header("🔍 Materials Recognition - Real-Time Detection")

        st.markdown("Use your webcam to scan and detect recyclable materials. Each detection earns you eco-points!")

        # 🎥 Camera Status Display
        camera_status = "🟥 **Not Active**" if not st.session_state.webcam_active else "🟩 **Running**"
        st.markdown(f"**Camera Status:** {camera_status}")

        # 🎛️ Webcam Toggle Buttons
        col1, col2 = st.columns([1, 1])
        if not st.session_state.webcam_active:
            if col1.button("▶️ Start Webcam"):
                st.session_state.webcam_active = True
        else:
            if col2.button("⏹ Stop Webcam"):
                st.session_state.webcam_active = False

        if st.session_state.webcam_active:
            # 📦 Load YOLO model
            model = YOLO("train33/weights/best.pt")

            # 📷 Initialize Webcam
            cap = cv2.VideoCapture(1)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_FPS, 240)

            if not cap.isOpened():
                st.error("❌ Error: Webcam not detected.")
                st.session_state.webcam_active = False
                st.stop()

            stframe = st.empty()
            detection_info = st.empty()
            table_display = st.empty()

            # 🎯 Live Detection Loop
            while st.session_state.webcam_active:
                ret, frame = cap.read()
                if not ret:
                    st.error("❌ Failed to read webcam frame.")
                    break

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.flip(frame, 1)

                detected_material = "None"
                detected_credits = 0
                img_path = None

                # 🔍 Run YOLO on Frame
                results = model(frame, conf=0.8, iou=0.7, classes=[0, 1, 2, 3])
                for result in results:
                    class_ids = result.boxes.cls.cpu().numpy()
                    for cls_id in class_ids:
                        material_name = model.names[int(cls_id)].capitalize()
                        detected_material = material_name

                        # 💾 Save Frame
                        img_path = f"C:/Practice/AiPD/eco_gallery/{material_name}_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
                        cv2.imwrite(img_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

                        # ♻️ Record Detection
                        if material_name in st.session_state.detection_count:
                            st.session_state.detection_count[material_name] += 1
                            credit_mapping = {"Cardboard": 7, "Metal": 10, "Paper": 5, "Plastic": 6}
                            detected_credits = credit_mapping.get(material_name, 0)
                            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                            new_entry = pd.DataFrame([[timestamp, material_name, detected_credits]],
                                                     columns=["Timestamp", "Material", "Credits"])
                            st.session_state.detection_history = pd.concat(
                                [st.session_state.detection_history, new_entry],
                                ignore_index=True
                            )

                # 🖼️ Update Webcam Feed
                stframe.image(frame, channels="RGB")

                # ✅ Display Detected Material Info
                if detected_material != "None":
                    detection_info.success(
                        f"✅ Detected: **{detected_material}** | 🪙 Credits Earned: **{detected_credits}**"
                    )
                else:
                    detection_info.info("🔄 Scanning for recyclable materials...")

                # 📊 Live Count Table
                df = pd.DataFrame(
                    [["Cardboard", st.session_state.detection_count["Cardboard"]],
                     ["Metal", st.session_state.detection_count["Metal"]],
                     ["Paper", st.session_state.detection_count["Paper"]],
                     ["Plastic", st.session_state.detection_count["Plastic"]]],
                    columns=["Material", "Total Detected"]
                )
                table_display.dataframe(df, use_container_width=True)

            # ✅ Clean-up
            cap.release()
            cv2.destroyAllWindows()

if menu == "EcoPoints Redemption":
    if not st.session_state.accepted_terms:
        st.warning("⚠️ You must accept the terms to access this page!")
    else:
        pass
        # --- One-Time Reset Per App Launch ---
        if "reset_done" not in st.session_state:
            if os.path.exists("ai_avatar_app/user_data.json"):
                os.remove("ai_avatar_app/user_data.json")
            st.session_state.detection_history = pd.DataFrame(columns=["Timestamp", "Material", "Credits"])
            st.session_state.reset_done = True
    
        # --- Load & Save User Data ---
        def load_user_data():
            if os.path.exists("ai_avatar_app/user_data.json"):
                with open("ai_avatar_app/user_data.json", "r") as f:
                    return json.load(f)
            return {
                "earned_points": 0,
                "spent_points": 0,
                "avatar": "",
                "vouchers": []
            }
    
        def save_user_data(data):
            with open("ai_avatar_app/user_data.json", "w") as f:
                json.dump(data, f, indent=4)
    
        user_data = load_user_data()
        user_data.setdefault("spent_points", 0)
    
        # --- Fallback Detection History ---
        if "detection_history" not in st.session_state:
            st.session_state.detection_history = pd.DataFrame(columns=["Timestamp", "Material", "Credits"])
    
        # --- Cooldown Timer for Real-Time Updates ---
        now = time.time()
        last_update = st.session_state.get("last_detection_time", 0)
        cooldown_secs = 5
        
        # --- Recalculate Points if Cooldown Passed ---
        if now - last_update > cooldown_secs:
            earned_points = int(st.session_state.detection_history["Credits"].sum())
            if earned_points != user_data.get("earned_points", 0):
                user_data["earned_points"] = earned_points
                save_user_data(user_data)
            st.session_state["last_detection_time"] = now
        
        # --- Always Read Latest Earned Points From File ---
        earned_points = user_data.get("earned_points", 0)
        available_points = earned_points - user_data["spent_points"]

    
        # --- Avatar Theme Definitions ---
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
    
        # --- First-Time Avatar Selection ---
        if not user_data["avatar"]:
            st.title("🎨 Choose Your Avatar")
            st.markdown("Select your eco-avatar to start earning themed rewards!")
            avatar_files = os.listdir("avatars")
            selected = st.selectbox(
                "Pick your avatar:",
                avatar_files,
                format_func=lambda x: avatar_themes[x]["name"]
            )
            if st.button("Confirm Avatar"):
                user_data["avatar"] = selected
                save_user_data(user_data)
                st.rerun()
        else:
            voucher_redeemed = False
    
            st.title("♻️ AI Recycling Avatar App")
    
            # --- Avatar Display Section ---
            st.markdown("### 👤 Your Avatar")
            avatar = user_data["avatar"]
            avatar_data = avatar_themes.get(avatar, {})
            avatar_name = avatar_data.get("name", "")
            user_vouchers = avatar_data.get("vouchers", [])
            color = avatar_data.get("color", "#0077cc")
    
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(f"avatars/{avatar}", width=200)
            with col2:
                st.subheader(f"{avatar_name}")
                st.markdown(f"**Available EcoPoints:** `{available_points}`")
                st.markdown(f"**Earned Total:** `{earned_points}`")
                st.markdown(f"**Spent:** `{user_data['spent_points']}`")
    
            # --- Avatar Change Section ---
            st.markdown("### 🔄 Change Avatar")
            with st.expander("🧝 Change your avatar (Costs 200 points)"):
                if available_points < 200:
                    st.warning("Not enough points to change your avatar.")
                else:
                    avatar_files = os.listdir("avatars")
                    new_avatar = st.selectbox(
                        "Choose a new avatar:",
                        avatar_files,
                        format_func=lambda x: avatar_themes[x]["name"],
                        key="change_avatar"
                    )
                    if new_avatar == user_data["avatar"]:
                        st.info("This is already your current avatar.")
                    elif st.button("Confirm Avatar Change"):
                        user_data["avatar"] = new_avatar
                        user_data["spent_points"] += 200
                        save_user_data(user_data)
                        st.success(f"Avatar changed to {avatar_themes[new_avatar]['name']}!")
                        time.sleep(2)
                        st.rerun()
    
            st.markdown("<br><br>", unsafe_allow_html=True)
    
            # --- Points Summary ---
            st.markdown("### 🌿 Your EcoPoints Summary")
            points_col1, points_col2, points_col3 = st.columns(3)
            points_col1.metric("Available", f"{available_points} 🪙")
            points_col2.metric("Earned", f"{earned_points} 🎯")
            points_col3.metric("Spent", f"{user_data['spent_points']} 💸")
    
            # --- Redeem Themed Vouchers ---
            st.markdown("### 🎁 Redeem Themed Vouchers")
            st.markdown("Unlock unique rewards themed around your eco-avatar! Each voucher costs **1,000 EcoPoints**.")
    
            # Split vouchers into redeemed and unredeemed
            redeemed = [v for v in user_vouchers if v in user_data["vouchers"]]
            unredeemed = [v for v in user_vouchers if v not in user_data["vouchers"]]
            display_order = unredeemed + redeemed  # Unredeemed on top
    
            for voucher in display_order:
                redeemed_status = voucher in user_data["vouchers"]
                bg_color = "#f0f0f0" if redeemed_status else "white"
                opacity = "0.5" if redeemed_status else "1"
    
                with st.container():
                    st.markdown("<br>", unsafe_allow_html=True)
                    v_col1, v_col2 = st.columns([4, 1])
                    with v_col1:
                        st.markdown(
                            f"""
                            <div style="padding: 20px; border-radius: 12px;
                            background-color: {bg_color}; color: black; border: 2px solid {color}; opacity: {opacity};">
                            <h4 style="margin-bottom: 10px; font-size: 22px; font-weight: 800;
                            text-transform: uppercase; letter-spacing: 1px; border-bottom: 2px dashed {color}; padding-bottom: 5px;">🎟️ {voucher}</h4>
                            """,
                            unsafe_allow_html=True,
                        )
    
                        if redeemed_status:
                            st.markdown("✅ VOUCHER REDEEMED", unsafe_allow_html=True)
                        elif available_points < 1000:
                            st.warning("Not enough EcoPoints to redeem this voucher.")
                        else:
                            confirm = st.radio(
                                f"Confirm redemption of **{voucher}**?",
                                ["No", "Yes"],
                                key=f"confirm_{voucher}",
                                horizontal=True
                            )
                            if confirm == "Yes":
                                user_data["vouchers"].append(voucher)
                                user_data["spent_points"] += 1000
                                available_points -= 1000
                                save_user_data(user_data)
    
                                st.success(f"🎉 Voucher Redeemed: {voucher}")
                                code = "VCHR-" + str(random.randint(100000, 999999))
                                st.code(code, language="text")
    
                                img = Image.new('RGB', (300, 150), color='white')
                                draw = ImageDraw.Draw(img)
                                draw.rectangle([10, 10, 290, 140], outline=color, width=3)
                                draw.text((30, 50), f"{voucher}", fill="black")
                                draw.text((30, 90), f"Code: {code}", fill=color)
                                st.image(img, caption="Show this at counter", use_column_width=False)
    
                                st.balloons()
                                voucher_redeemed = True
    
                        st.markdown("</div>", unsafe_allow_html=True)
    
                    with v_col2:
                        if not redeemed_status:
                            st.metric("Cost", "1,000🪙")
    
            st.markdown("<br><br>", unsafe_allow_html=True)
    
            # --- Map Section ---
            st.markdown("### 🗺️ Find Nearby Recycling Points")
            st.info("Check out the nearest recycling bins to your location.")
            map = folium.Map(location=[1.3521, 103.8198], zoom_start=11)
            folium.Marker([1.355, 103.82], tooltip="Recycling Point - Block 123").add_to(map)
            folium.Marker([1.35, 103.83], tooltip="Recycling Point - Green Mall").add_to(map)
            st_folium(map, width=700, height=500)
    
            st.markdown("💚 *Thank you for being an eco-hero!*")
    
            # --- Refresh view if redeemed ---
            if voucher_redeemed:
                time.sleep(2)
                st.rerun()