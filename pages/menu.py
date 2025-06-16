import streamlit as st
from models.funcionario import Funcionario

def show():
    st.sidebar.title(f"Bem-vindo(a), {st.session_state['usuario'].nome}")
    
    pagina = st.sidebar.radio(
        "Selecione uma opção:",
        ["Adicionar novo prestador", "Gerenciar prestadores", "Visualização geral"]
    )
    
    
    if st.sidebar.button("Sair"):
        st.session_state["autenticado"] = False
        st.session_state["usuario"] = None
        st.session_state["pagina"] = "login"
        st.rerun()
    
    if pagina == "Adicionar novo prestador":
        st.session_state["pagina"] = "adicionar_prestador"
        st.rerun()
    elif pagina == "Gerenciar prestadores":
        st.session_state["pagina"] = "gerenciar_prestadores"
        st.rerun()
    elif pagina == "Visualização geral":
        st.session_state["pagina"] = "visualizacao_geral"
        st.rerun()