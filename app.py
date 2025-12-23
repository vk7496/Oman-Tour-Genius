import streamlit as st
from groq import Groq
import re
import urllib.parse
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURATION ---
# حتماً در Secrets استریم‌لیت کلید را با نام GROQ_API_KEY وارد کن
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Please set your GROQ_API_KEY in Streamlit Secrets!")

st.set_page_config(page_title="BinMajid AI | bmtoursoman.com", page_icon="🇴🇲", layout="wide")

# --- KNOWLEDGE BASE (REAL DATA) ---
# اطلاعات استخراج شده از سایت و اینستاگرام بن‌ماجد
REAL_DATA_PROMPT = """
You are 'Majid', the official AI specialist for BinMajid Tourism (bmtoursoman.com).
License Number: 12596902.
WhatsApp Business: +96879378780.

Our Tours:
1. Musandam Khasab: Full day dhow cruise, dolphin watching, snorkeling at Telegraph & Seebi islands. Includes lunch & drinks.
2. Desert Safari: Wahiba Sands (Sharqiya Sands) overnight camping, sunset dunes, camel rides.
3. Mountains: Jebel Shams (Oman's Grand Canyon) and Jebel Akhdar (Green Mountain).
4. Wadis: Wadi Shab hiking/swimming and Wadi Bani Khalid.
5. City: Muscat Grand Mosque, Mutrah Souq, and Al Alam Palace.

Rules:
- Answer in English or the user's language.
- Be extremely polite and use Omani hospitality vibes.
- If they ask for prices, tell them it depends on group size and ask for their WhatsApp to send the latest PDF brochure.
- Your priority is to capture their phone number for the sales team.
"""

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "leads_data" not in st.session_state:
    st.session_state.leads_data = []

# --- HELPER FUNCTIONS ---
def extract_phone(text):
    pattern = r'(\+?\d{8,15})'
    match = re.search(pattern, text)
    return match.group(0) if match else None

# --- UI LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🏝️ BinMajid AI Travel Agent")
    st.write("Plan your dream Oman adventure with our official AI guide.")
    
    # نمایش تاریخچه چت
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ورودی کاربر
    if prompt := st.chat_input("Ask about Musandam, Desert or Jebel Shams..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # استخراج لید (شماره تماس)
        phone = extract_phone(prompt)
        if phone:
            clean_phone = re.sub(r'\D', '', phone)
            st.session_state.leads_data.append({
                "Time": datetime.now().strftime("%H:%M"),
                "Customer Phone": clean_phone,
                "Context": prompt[:30] + "..."
            })
            st.toast("New Booking Interest Captured!", icon="📞")

        # پاسخ هوش مصنوعی از Groq
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
            except Exception as e:
                st.error("The AI is busy. Please try again in a moment.")

with col2:
    st.markdown("### 📊 Business Dashboard")
    st.info("Direct leads for BinMajid Sales Team")
    
    if st.session_state.leads_data:
        df = pd.DataFrame(st.session_state.leads_data)
        st.dataframe(df, use_container_width=True)
        
        target_customer = st.session_state.leads_data[-1]["Customer Phone"]
        wa_text = urllib.parse.quote(f"Hello from BinMajid Tourism! We saw your interest in our Oman tours. How can we help you?")
        
        st.success(f"Action: Contact {target_customer}")
        st.link_button("🚀 Chat on WhatsApp", f"https://wa.me/{target_customer}?text={wa_text}")
        
        if st.button("Clear Leads"):
            st.session_state.leads_data = []
            st.rerun()
    else:
        st.write("Waiting for leads... (Test by typing a phone number)")

    st.divider()
    st.image("https://visitoman.om/wp-content/uploads/2022/05/Wadi-Shab-1.jpg", caption="BinMajid: Your Gateway to Oman")
