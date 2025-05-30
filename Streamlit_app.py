import streamlit as st
from models import Funcionario
from extensions import database as db
from flask import Flask
from datetime import datetime
from sqlalchemy.orm import scoped_session

app = Flask(__name__)
app.config.from_prefixed_env()
db.init_app(app)

with app.app_context():
    db.create_all()

# Configuração do Streamlit
st.set_page_config(page_title="Sistema Pequeno Cotolengo", layout="centered")
st.title("Login do Funcionário")

# Se ainda não está logado e aparecer mensagem de erro caso erre algo
if "usuario_id" not in st.session_state:
    id_usuario = st.text_input("ID")
    senha_usuario = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        with app.app_context():
            funcionario = Funcionario.get_funcionario_por_id(id=id_usuario)
            if funcionario and funcionario.checa_senha(senha=senha_usuario):
                st.session_state["usuario_id"] = funcionario.id
                st.experimental_rerun()
            else:
                st.error("ID ou senha inválidos.")

# Se já está logado
else:
    with app.app_context():
        funcionario = Funcionario.get_funcionario_por_id(id=st.session_state["usuario_id"])
    st.success(f"Bem-vindo, {funcionario.nome}!")
    if st.button("Sair"):
        del st.session_state["usuario_id"]
        st.experimental_rerun()



# Interface
st.title("Login do Funcionário")

id_usuario = st.text_input("ID")
senha_usuario = st.text_input("Senha", type="password")

if st.button("Entrar"):
    with app.app_context():
        funcionario = Funcionario.get_funcionario_por_id(id=id_usuario)
        if funcionario and funcionario.checa_senha(senha=senha_usuario):
            st.success(f"Bem-vindo, {funcionario.nome}!")
            st.write(f"Cargo: {funcionario.cargo}")
        else:
            st.error("ID ou senha inválidos.")
