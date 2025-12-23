import streamlit as st
import re
import urllib.parse
import pandas as pd
from datetime import datetime
import time

# --- PAGE SETUP ---
st.set_page_config(page_title="MajidAI | BinMajid Tourism", page_icon="🇴🇲", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "leads_data" not in st.session_state:
    st.session_state.leads_data = []

# --- MOCK AI LOGIC ---
def get_mock_response(user_input):
    user_input = user_input.lower()
    if "price" in user_input or "cost" in user_input:
        return "Our prices are very competitive! For example, Musandam trips start at 20 OMR. May I have your WhatsApp to send the full price list? 📄"
    elif "musandam" in user_input:
        return "Musandam is beautiful! We offer dolphin watching and snorkeling. Can I get your number to send the available dates? 🐬"
    elif any(char.isdigit() for char in user_input):
        return "Thank you! I've noted your number. Our team from BinMajid Tourism will contact you shortly. 🇴🇲"
    else:
        return "Oman is a land of adventure! Would you like to know more about our Desert Camping or Wadi tours? Just leave your WhatsApp number for details. ✨"

# --- HELPER FUNCTIONS ---
def extract_phone(text):
    # این الگو شماره‌های ۸ رقمی عمان و شماره‌های بین‌المللی را پیدا می‌کند
    pattern = r'(\+?\d{8,15})'
    match = re.search(pattern, text)
    return match.group(0) if match else None

# --- UI LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🇴🇲 OM MajidAI: BinMajid Smart Guide")
    st.write("Helping you explore Oman's beauty. Type below to start.")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about tours or leave your number..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Lead Capture Logic
        found_phone = extract_phone(prompt)
        if found_phone:
            # پاکسازی شماره برای لینک واتس‌اپ (حذف کاراکترهای اضافه)
            clean_phone = re.sub(r'\D', '', found_phone)
            new_lead = {
                "Time": datetime.now().strftime("%H:%M"),
                "Customer Phone": clean_phone,
                "Interest": prompt[:30] + "..."
            }
            st.session_state.leads_data.append(new_lead)
            st.toast(f"Lead captured: {clean_phone}", icon="📞")

        # Assistant Response
        with st.chat_message("assistant"):
            with st.spinner("Majid is typing..."):
                time.sleep(1)
                full_response = get_mock_response(prompt)
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

with col2:
    st.markdown("### 📊 Admin Dashboard")
    st.info("Captured Leads appear here instantly.")
    
    if st.session_state.leads_data:
        df = pd.DataFrame(st.session_state.leads_data)
        st.dataframe(df, use_container_width=True)
        
        # دریافت آخرین شماره مشتری برای دکمه پاسخ
        target_customer = st.session_state.leads_data[-1]["Customer Phone"]
        
        # متن پیام که ادمین برای مشتری می‌فرستد
        message_to_customer = urllib.parse.quote(f"Hello! This is BinMajid Tourism 🇴🇲. We saw your interest in our tours via our AI assistant. How can we help you plan your trip?")
        
        st.success(f"Action: Reply to {target_customer}")
        # لینک واتس‌اپ حالا به شماره مشتری (target_customer) اشاره می‌کند
        st.link_button("🚀 Start WhatsApp Chat", f"https://wa.me/{target_customer}?text={message_to_customer}")
        
        if st.button("Clear Dashboard"):
            st.session_state.leads_data = []
            st.rerun()
    else:
        st.write("No leads yet. Type a phone number in the chat to test!")

    st.divider()
    st.image("https://images.unsplash.com/photo-1544274411-a7af6d121cff?q=80&w=300", caption="BinMajid Adventures")
