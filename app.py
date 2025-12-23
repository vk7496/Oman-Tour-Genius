import streamlit as st
import re
import urllib.parse
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURATION ---
MY_WHATSAPP_NUMBER = "96879378780" # شماره رسمی بن‌ماجد برای دمو

st.set_page_config(page_title="MajidAI | BinMajid Tourism", page_icon="🇴🇲", layout="wide")

# --- UI DESIGN ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #ddd; }
    .stHeader { color: #d4a017; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "leads_data" not in st.session_state:
    st.session_state.leads_data = []

# --- MOCK AI LOGIC (No API Needed) ---
def get_mock_response(user_input):
    user_input = user_input.lower()
    if "price" in user_input or "cost" in user_input or "how much" in user_input:
        return "Our tour prices depend on the group size. For example, the Musandam Dhow Cruise starts at 20 OMR. May I have your WhatsApp number to send you the full price list? 📄"
    elif "musandam" in user_input:
        return "Musandam is breathtaking! We offer dolphin watching and snorkeling. Would you like to see our available dates for next week? Please share your phone number. 🐬"
    elif "desert" in user_input or "wahiba" in user_input:
        return "The Wahiba Sands camping experience is a must-see! Sunset camel rides and traditional Omani dinners are included. Can I get your WhatsApp to send the itinerary? 🐪"
    elif any(char.isdigit() for char in user_input):
        return "Thank you! I've received your contact details. Our team will contact you shortly to finalize your booking. Welcome to Oman! 🇴🇲"
    else:
        return "That's a great choice! Oman has so much to offer. To give you the best recommendation, could you tell me your travel dates or leave your WhatsApp number? ✨"

# --- HELPER FUNCTIONS ---
def extract_phone(text):
    pattern = r'(\+?\d{8,15})'
    match = re.search(pattern, text)
    return match.group(0) if match else None

# --- UI LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🇴🇲 OM MajidAI: BinMajid Smart Guide")
    st.write("Welcome! I am your AI assistant. Type a message to start planning your Oman trip.")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Try: 'Tell me about Musandam' or 'How much for the desert tour?'"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Check for Lead
        found_phone = extract_phone(prompt)
        if found_phone:
            new_lead = {"Time": datetime.now().strftime("%H:%M"), "Phone": found_phone, "Status": "New"}
            st.session_state.leads_data.append(new_lead)
            st.toast("Lead Captured!", icon="📞")

        # Simulate Thinking
        with st.chat_message("assistant"):
            with st.spinner("Majid is typing..."):
                time.sleep(1)
                full_response = get_mock_response(prompt)
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

with col2:
    st.markdown("### 📊 Admin Dashboard")
    st.info("This panel is for the Business Owner to see captured leads in real-time.")
    
    if st.session_state.leads_data:
        df = pd.DataFrame(st.session_state.leads_data)
        st.table(df) # نمایش جدول لیدها
        
        last_phone = st.session_state.leads_data[-1]["Phone"]
        wa_text = urllib.parse.quote("Hi! We saw your request on BinMajid AI. How can we help?")
        st.link_button(f"Direct WhatsApp to {last_phone}", f"https://wa.me/{MY_WHATSAPP_NUMBER}?text={wa_text}")
    else:
        st.write("No leads yet. Type a phone number in the chat to see the magic! ✨")

    st.divider()
    st.image("https://images.unsplash.com/photo-1544274411-a7af6d121cff?q=80&w=300", caption="Omani Hospitality")
