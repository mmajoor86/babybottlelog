import streamlit as st
import page_1
import page_2

# Add a sidebar with options to navigate between pages
st.sidebar.title("🚀 Navigation")
selection = st.sidebar.radio("👶 Go to", ["🍼 Data Entry", "📊 Overview"])

# Depending on the selection, call the relevant page
if selection == "🍼 Data Entry":
    page_1.app()
elif selection == "📊 Overview":
    page_2.app()
