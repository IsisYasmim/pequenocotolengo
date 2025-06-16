# app.py
import streamlit as st
import streamlit_authenticator as stauth
from firebase_config import get_db
from pages import login, menu#, adicionar_supervisor, adicionar_prestador, gerenciar_prestadores, visualizacao_geral
db = get_db()
def main():
    st.set_page_config(page_title="Sistema Cotolengo", layout="wide", initial_sidebar_state="collapsed")

    # Inicializa sessão
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
        st.session_state["expira_em"] = None

    # Verifica se o login expirou
    if st.session_state["autenticado"] and st.session_state["expira_em"]:
        from datetime import datetime
        if datetime.now() > st.session_state["expira_em"]:
            st.session_state["autenticado"] = False
            st.session_state["expira_em"] = None
            st.warning("Sessão expirada. Faça login novamente.")

    # Se não autenticado, mostra tela de login
    if not st.session_state["autenticado"]:
        login.login_screen(db)
        return  # não renderiza mais nada enquanto não logar

    # Se autenticado, mostra sistema
    st.sidebar.title("Menu")
    st.session_state["pagina"] = st.sidebar.radio("Navegação", ["menu"])

    if st.session_state["pagina"] == "menu":
        menu.show()
    '''elif st.session_state["pagina"] == "adicionar_supervisor":
        adicionar_supervisor.show()
    elif st.session_state["pagina"] == "adicionar_prestador":
        adicionar_prestador.show()
    elif st.session_state["pagina"] == "gerenciar_prestadores":
        gerenciar_prestadores.show()
    elif st.session_state["pagina"] == "visualizacao_geral":
        visualizacao_geral.show()'''

if __name__ == "__main__":
    main()