import streamlit as st
from models import Funcionario
from extensions import database as db
from flask import Flask
from datetime import datetime
from sqlalchemy.orm import scoped_session

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
            st.write(f"Admissão: {funcionario.data_admissao}")
        else:
            st.error("ID ou senha inválidos.")
