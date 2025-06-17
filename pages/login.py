import streamlit as st
from datetime import datetime, timedelta
from models.funcionario import Funcionario

def login_screen(db):
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.title("Login - Sistema Cotolengo")

    with st.form("login_form"):
        coren = st.text_input("COREN").strip()
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")

        if submit:
            funcionarios = db.collection('funcionarios')
            docs = funcionarios.where('coren', '==', coren).stream()
            funcionario = None
            for doc in docs:
                data = doc.to_dict()
                funcionario = Funcionario(
                    id=doc.id,
                    nome=data.get('nome'),
                    coren=data.get('coren'),
                    cargo=data.get('cargo'),
                    tipo_vinculo=data.get('tipo_vinculo'),
                    data_admissao=data.get('data_admissao'),
                    turno=data.get('turno'),
                    local=data.get('local'),
                    senha=data.get('senha')  # senha já vem como hash
                )
                break

            if funcionario and funcionario.checa_senha(senha):
                st.success("Login realizado com sucesso.")
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = funcionario
                st.session_state["expira_em"] = datetime.now() + timedelta(days=30)
                st.rerun()
            else:
                st.error(f"COREN ou senha inválidos")
