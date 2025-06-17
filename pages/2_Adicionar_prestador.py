import streamlit as st
from firebase_config import get_db
from datetime import date
from modules import login
from models.cargo import Cargo
from models.funcionario import Funcionario
import Inicio

db = get_db()  # inicializa o banco de dados

def show():
    Inicio.init_session()
    st.header("Adicionar Novo Prestador de Serviço")
    with st.form("form_adicionar_prestador"):
        nome = st.text_input("Nome completo*", key="nome_prestador")
        matricula = st.text_input("Matrícula (MAT)*", key="mat_prestador")
        coren = st.text_input("COREN*", key="coren_prestador")
        
        cargos = [c["nome_do_cargo"] for c in Cargo.get_all(db)]
        if cargos:
            cargo = st.selectbox("Cargo", cargos, key="cargo_prestador")
        else:
            cargo = st.selectbox()("Cargo", ["Nenhum cargo cadastrado"], key="cargo_prestador")

        data_admissao = st.date_input("Data de admissão*", value=date.today(), key="data_prestador")
        tipo_vinculo = st.selectbox(
            "Tipo de vínculo",
            ["AJ - PROGRAMA ANJO", "FT - EFETIVADO"],
            key="vinculo_prestador"
        )
        salvar = st.form_submit_button("Salvar")

    if salvar:
        if not nome or not matricula or not coren or not cargo or not data_admissao:
            st.warning("Por favor, preencha todos os campos obrigatórios.")
            return

        try:
            st.write(f"DEBUG: Tentando adicionar prestador - Nome: {nome}, MAT: {matricula}, COREN: {coren}")
            novo = Funcionario(nome, matricula, coren, cargo, tipo_vinculo, data_admissao)
            novo.save(db)
            st.success("Prestador cadastrado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao cadastrar prestador: {str(e)}")
    login.logout_sidebar()

if __name__ == "__main__":
    show()