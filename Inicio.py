# app.py
import streamlit as st
from firebase_config import get_db
from datetime import datetime
from modules import login

def main():
    st.set_page_config(page_title="Sistema Cotolengo", layout="wide")
    db = get_db()
    # inicializa sessão
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
        st.session_state["expira_em"] = None
        st.session_state["pagina"] = "menu"

    # verifica se o login expirou
    if st.session_state["autenticado"] and st.session_state["expira_em"]:
        if datetime.now() > st.session_state["expira_em"]:
            st.session_state["autenticado"] = False
            st.session_state["expira_em"] = None
            st.warning("Sessão expirada. Faça login novamente.")

    # se não autenticado, mostra tela de login e esconde a sidebar
    if not st.session_state["autenticado"]:
        login.login_screen(db)
        if not st.session_state["autenticado"]:
            return
        else:
            st.rerun()

    # se autenticado, mostra a aplicação principal com sidebar
    usuario = st.session_state["usuario"]
    with st.sidebar:
        if st.button("🔒 Logout"):
            login.logout()

    # Conteúdo principal
    st.markdown(f"## 👋 Bem-vindo, **{usuario.nome}**!")
    st.markdown(
        """
        <div style="font-size: 1.1rem; color: #FFFFFF; margin-top: 10px;">
            Selecione a ação desejada no menu lateral para começar.
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()