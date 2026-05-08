import streamlit as st
from search import search_company
from brief import generate_brief
from render import save_brief

st.title("Pitch Brief Generator")
st.write("Enter a company name to generate a pitch brief.")

company_name = st.text_input("Company Name")

if st.button("Generate Brief"):
    if company_name:
        with st.spinner("Researching company..."):
            results = search_company(company_name)
        
        with st.spinner("Generating brief..."):
            brief = generate_brief(company_name, results)
        
        with st.spinner("Saving document..."):
            filepath = save_brief(company_name, brief)
        
        st.success("Brief generated!")
        st.markdown(brief)
        
        with open(filepath, "rb") as f:
            st.download_button(
                label="Download Word Doc",
                data=f,
                file_name=filepath.split("/")[-1],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        st.warning("Please enter a company name.")