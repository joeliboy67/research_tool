import streamlit as st
import json
import os
from datetime import datetime
from search import search_company
from brief import generate_brief
from render import save_brief

st.set_page_config(page_title="Joel | Pitchcraft Advisory", page_icon="👋", layout="wide")
st.markdown("""
    <style>
    .stButton>button {
        background-color: #0066CC;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-size: 1rem;
        border: none;
        width: 100%;
    }
    .stButton>button:hover { background-color: #0052A3; }
    </style>
""", unsafe_allow_html=True)

HISTORY_FILE = "search_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_to_history(company_name, brief):
    history = load_history()
    history.insert(0, {
        "company": company_name,
        "brief": brief,
        "date": datetime.now().strftime("%d %b %Y %H:%M")
    })
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[:20], f)

# Sidebar
with st.sidebar:
    st.title("🕘 Search History")
    history = load_history()
    if history:
        for item in history:
            if st.button(f"📄 {item['company']}\n{item['date']}", key=item['date']):
                st.session_state.selected_brief = item['brief']
                st.session_state.selected_company = item['company']
    else:
        st.write("No searches yet.")

# Main#
st.title("👋 Alright butt, I'm Joel, Pitchcraft's research assistant")
st.divider()

if "selected_brief" in st.session_state:
    st.subheader(f"📄 {st.session_state.selected_company}")
    st.markdown(st.session_state.selected_brief.replace("$", "\\$"))
    
    filepath = save_brief(st.session_state.selected_company, st.session_state.selected_brief)
    with open(filepath, "rb") as f:
        st.download_button(
            label="⬇️ Download Word Doc",
            data=f,
            file_name=filepath.split("/")[-1],
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    
    if st.button("← New Search"):
        del st.session_state.selected_brief
        del st.session_state.selected_company
        st.rerun()
else:
    company_name = st.text_input("", placeholder="Enter company name e.g. Tesco PLC")

    if st.button("Generate Brief"):
        if company_name:
            with st.spinner("🔍 Researching company..."):
                results = search_company(company_name)
            with st.spinner("✍️ Generating brief..."):
                brief = generate_brief(company_name, results)
            with st.spinner("💾 Saving document..."):
                filepath = save_brief(company_name, brief)

            if st.button("💾 Save to watchlist"):
                save_to_history(company_name, brief)
                with open("companies.txt", "a+") as f:
                    f.seek(0)
                    existing = [line.strip().lower() for line in f.readlines()]
                    if company_name.lower() not in existing:
                        f.write(f"\n{company_name}")
                st.success(f"{company_name} saved to watchlist and weekly digest.")

            st.success("Brief generated successfully!")
            st.divider()
            st.markdown(brief.replace("$", "\\$"))
            st.divider()

            with open(filepath, "rb") as f:
                st.download_button(
                    label="⬇️ Download Word Doc",
                    data=f,
                    file_name=filepath.split("/")[-1],
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        else:
            st.warning("Please enter a company name.")