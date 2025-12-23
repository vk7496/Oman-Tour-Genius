import streamlit as st
from groq import Groq
import re
import urllib.parse
import pandas as pd
from datetime import datetime
import time

# --- CONFIG ---
# Make sure GROQ_API_KEY is in your Streamlit Secrets
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("GROQ_API_KEY not found in Secrets!")

st.set_page_config(page_title="BinMajid AI Consultant", page_icon="🇴🇲", layout="wide")

# --- SYSTEM PROMPT (English) ---
REAL_DATA_PROMPT = """
You are 'Majid', a premium Travel Consultant for BinMajid Tourism Oman (bmtoursoman.com).
Your mission is to qualify the lead by asking specific questions before getting their WhatsApp.

Follow these rules:
1. Be warm and professional. Use "Omani Hospitality" style.
2. Flow of conversation:
   - Step A: Ask if they prefer Adventure/Nature or Luxury/Relaxation.
   - Step B: Ask how many people are in their group and if they have small children.
   - Step C: Ask for the duration of their stay in Oman.
   - Step D: Recommend a specific tour based on their needs.
   - Step E: Politely ask for their WhatsApp to send a personalized PDF itinerary and price quote.

IMPORTANT: Do not ask all questions in one message. Keep it a natural back-and-forth conversation.
"""

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "leads_data" not in st.session_state:
    st.session_state.leads_data = []

# --- FUNCTIONS ---
def extract_phone(text):
    pattern = r'(\+?\d{8,15})'
    match = re.search(pattern, text)
    return match.group(0) if match else None

# --- UI LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🇴🇲 BinMajid Smart Concierge")
    st.caption("Official AI Assistant for bmtoursoman.com")
    
    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Hi! I'm planning a trip to Oman..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Lead Capture
        phone = extract_phone(prompt)
        if phone:
            clean_phone = re.sub(r'\D', '', phone)
            st.session_state.leads_data.append({
                "Time": datetime.now().strftime("%H:%M"),
                "Phone": clean_phone,
                "Last_Msg": prompt[:30] + "..."
            })
            st.toast("Contact Details Saved!", icon="✅")

        # Groq AI Response
        with st.chat_message("assistant"):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": REAL_DATA_PROMPT}] + 
                             [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                )
                ai_msg = response.choices[0].message.content
                st.markdown(ai_msg)
                st.session_state.messages.append({"role": "assistant", "content": ai_msg})
            except:
                st.error("AI service is busy. Please try again.")

with col2:
    st.markdown("### 🔒 Business Dashboard")
    # ADMIN PASSWORD: binmajid2024
    admin_password = st.text_input("Admin Access Code", type="password")
    
    if admin_password == "binmajid2024": 
        st.success("Authorized Access")
        if st.session_state.leads_data:
            df = pd.DataFrame(st.session_state.leads_data)
            st.dataframe(df, use_container_width=True)
            
            last_phone = st.session_state.leads_data[-1]["Phone"]
            wa_text = urllib.parse.quote("Hi! This is BinMajid Tourism. We received your request through our AI assistant. How can we help you further?")
            
            st.link_button(f"Chat with Client: {last_phone}", f"https://wa.me/{last_phone}?text={wa_text}")
        else:
            st.info("No leads captured yet.")
    elif admin_password != "":
        st.error("Incorrect Code")
    else:
        st.info("Enter the admin code to view the leads table.")

    st.divider()
    st.image("https://visitoman.om/wp-content/uploads/2022/05/Wadi-Shab-1.jpg", caption="Experience Oman with BinMajid")
