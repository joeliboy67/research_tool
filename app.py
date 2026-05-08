import streamlit as st
from search import search_company
from brief import generate_brief
from render import save_brief

st.set_page_config(page_title="Pitch Brief Generator", page_icon="📋", layout="centered")

st.markdown("""
    <style>
    .main { padding: 2rem; }
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
    .stTextInput>div>input {
        border-radius: 8px;
        padding: 0.5rem;
        font-size: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📋 Pitch Brief Generator")
st.markdown("*Generate a professional pitch brief for any company in seconds.*")
st.divider()

company_name = st.text_input("", placeholder="Enter company name e.g. Tesco PLC")

if st.button("Generate Brief"):
    if company_name:
        with st.spinner("🔍 Researching company..."):
            results = search_company(company_name)
        with st.spinner("✍️ Generating brief..."):
            brief = generate_brief(company_name, results)
        with st.spinner("💾 Saving document..."):
            filepath = save_brief(company_name, brief)

        st.success("Brief generated successfully!")
        st.divider()
        
        # Fix dollar sign rendering
        safe_brief = brief.replace("$", "\\$")
        st.markdown(safe_brief)
        
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