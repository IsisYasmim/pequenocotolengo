import streamlit as st
from modules.login import logout


st.title("Adicionar Prestador")
st.write("Formulário para adicionar prestador aqui.")

with st.sidebar:
        if st.button("🔒 Logout"):
            login.logout()