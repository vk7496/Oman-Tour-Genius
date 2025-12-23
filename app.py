import streamlit as st
from openai import OpenAI
import re
import urllib.parse
import pandas as pd
from datetime import datetime

# --- CONFIGURATION & SECRETS ---
# Ensure you have OPENAI_API_KEY in your Streamlit Secrets
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error("Please set your OpenAI API Key in Streamlit Secrets!")

# Replace with your WhatsApp number for the demo (format: 989123456789)
MY_WHATSAPP_NUMBER = "96891278434" 

# --- PAGE SETUP ---
st.set_page_config(page_title="MajidAI | BinMajid Tourism", page_icon="🇴🇲", layout="wide")

# Custom CSS for a premium look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #007bff; color: white; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- AI PERSONA & KNOWLEDGE BASE ---
SYSTEM_PROMPT = """
You are 'Majid', a premium AI Travel Consultant for 'BinMajid Tourism' in Oman.
License Number: 12596902.
Your primary goal is to assist tourists and capture their WhatsApp number for bookings.

Services to promote:
1. Musandam Dhow Cruises (Dolphins & Snorkeling).
2. Wahiba Sands Desert Camping (Sunsets & Camel rides).
3. Jebel Shams & Jebel Akhdar (Mountain hiking and cool weather).
4. Wadi Shab & Wadi Bani Khalid (Waterfalls and swimming).

Guidelines:
- Be extremely polite and use Omani hospitality vibes.
- If a user expresses interest, say: "I'd love to send you our full brochure and current prices via WhatsApp. What is your contact number?"
- Keep responses concise but exciting.
- Answer in English (as requested for this demo).
"""

# --- SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "leads_data" not in st.session_state:
    st.session_state.leads_data = [] # Stores lead info as dictionaries

# --- HELPER FUNCTIONS ---
def extract_phone(text):
    pattern = r'(\+?\d{8,15})'
    match = re.search(pattern, text)
    return match.group(0) if match else None

# --- UI LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🇴🇲 MajidAI: BinMajid Smart Guide")
    st.write("Welcome to Oman! I can help you plan your perfect adventure.")
    
    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask me about Musandam, Desert or Mountains..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Check for Phone Number in user input
        found_phone = extract_phone(prompt)
        if found_phone:
            new_lead = {
                "Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Phone": found_phone,
                "Last_Message": prompt[:50] + "..."
            }
            st.session_state.leads_data.append(new_lead)
            st.toast("Lead Captured Successfully!", icon="✅")

        # Get AI Response
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + 
                         [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            ai_msg = response.choices[0].message.content
            st.markdown(ai_msg)
            st.session_state.messages.append({"role": "assistant", "content": ai_msg})

with col2:
    st.markdown("### 📊 Admin Dashboard")
    st.info("This section is only visible to the business owner.")
    
    if st.session_state.leads_data:
        df = pd.DataFrame(st.session_state.leads_data)
        st.write("Captured Leads:")
        st.dataframe(df, use_container_width=True)
        
        # WhatsApp Link for the owner
        latest_lead = st.session_state.leads_data[-1]["Phone"]
        wa_text = urllib.parse.quote(f"Hi, I am the manager of BinMajid. I saw your interest in our tours via our AI. How can I help you?")
        st.markdown(f"**Action Required:**")
        st.link_button(f"Chat with Lead ({latest_lead})", f"https://wa.me/{MY_WHATSAPP_NUMBER}?text={wa_text}")
        
        # Download as CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Leads Excel", csv, "binmajid_leads.csv", "text/csv")
    else:
        st.write("No leads captured yet. Try typing a phone number in the chat!")

    st.divider()
    st.image("https://images.unsplash.com/photo-1578922746465-3a80a228f223?auto=format&fit=crop&q=80&w=300", caption="Oman's Beautiful Coast")
