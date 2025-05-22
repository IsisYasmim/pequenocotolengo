
import streamlit as st
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("banco.db", check_same_thread=False)
cursor = conn.cursor()

# banco de dados SQlite
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    coren TEXT UNIQUE,
    senha TEXT,
    cargo TEXT,
    tipo_vinculo TEXT,
    data_admissao TEXT,
    gerente INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS escalas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    data TEXT,
    turno TEXT,
    local_uh INTEGER,
    local_ucci INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)
""")

# gerente padrão: Jean
cursor.execute("SELECT * FROM usuarios WHERE coren='56.127'")
if not cursor.fetchone():
# espaços reservados para colocar os valores que serão fornecidos, para segurança fiz que pegassem cada informação separadamente, por isso os "?"
    cursor.execute("""
    INSERT INTO usuarios (nome, coren, senha, cargo, tipo_vinculo, data_admissao, gerente)
    VALUES (?, ?, ?, ?, ?, ?, 1)
    """, ("Administrador", "56.127", "147258", "SUPERVISOR", "FT - EFETIVADO", datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
# Acesso do Jean
def autenticar(coren, senha):
    cursor.execute("SELECT * FROM usuarios WHERE coren=? AND senha=? AND gerente=1", (coren, senha))
    return cursor.fetchone()
# como irá ficar o "front end"
st.set_page_config(page_title="Sistema de Escalas", layout="wide")
st.title("Gerenciamento de Escalas - Somente Gerência")

coren = st.text_input("Coren", key="login_coren")
senha = st.text_input("Senha", type="password", key="login_senha")
# Configurando a segunda aba da interface
if st.button("Entrar"):
    gerente = autenticar(coren, senha)
    if gerente:
        st.success(f"Bem-vindo(a), {gerente[1]}! Gestão autorizada.")
        menu = ["Novo Prestador", "Gerenciar Escala"]
        escolha = st.sidebar.selectbox("Menu", menu)

        if escolha == "Novo Prestador":
            st.subheader("Cadastro de Prestador")
            nome = st.text_input("Nome completo")
            novo_coren = st.text_input("Coren", key="cadastro_coren")
            nova_senha = st.text_input("Senha", type="password", key="cadastro_senha")
            cargo = st.selectbox("Cargo", ["Enfermeira", "Tec. Enf", "SUPERVISOR", "HOSPITALISTA", "NIR", "Aux. Enf."])
            tipo = st.selectbox("Tipo de vínculo", ["FT - EFETIVADO", "PJ - PROGRAMA ANJO"])
            data_adm = st.date_input("Data de admissão")
            if st.button("Cadastrar"):
                try:
                    cursor.execute("""
                    INSERT INTO usuarios (nome, coren, senha, cargo, tipo_vinculo, data_admissao)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (nome, novo_coren, nova_senha, cargo, tipo, data_adm.strftime('%Y-%m-%d')))
                    conn.commit()
                    st.success("Prestador cadastrado com sucesso!")
                except:
                    st.error("Erro: Coren já existente ou inválido")
# GERENCIAMENTO DA ESCALA MENSAL
        elif escolha == "Gerenciar Escala":
            st.subheader("Gerenciar Escala Mensal")
            cursor.execute("SELECT id, nome FROM usuarios")
            prestadores = cursor.fetchall()
            prestador = st.selectbox("Escolha o prestador:", prestadores, format_func=lambda x: x[1])
            mes_atual = datetime.now().replace(day=1)
            dias_mes = [mes_atual + timedelta(days=i) for i in range(31)
                        if (mes_atual + timedelta(days=i)).month == mes_atual.month]
            for dia in dias_mes:
                turnos = ["Dia 1", "Noite 1"] if dia.day % 2 == 0 else ["Dia 2", "Noite 2"]
                st.markdown(f"### {dia.strftime('%d/%m/%Y')} - Turnos: {', '.join(turnos)}")
                for turno in turnos:
                    with st.expander(turno):
                        uh = st.checkbox("UH", key=f"{dia}-{turno}-uh")
                        ucci = st.checkbox("UCCI", key=f"{dia}-{turno}-ucci")
                        if st.button("Salvar", key=f"{dia}-{turno}-btn"):
                            cursor.execute("""
                            INSERT INTO escalas (usuario_id, data, turno, local_uh, local_ucci)
                            VALUES (?, ?, ?, ?, ?)
                            """, (prestador[0], dia.strftime('%Y-%m-%d'), turno, int(uh), int(ucci)))
                            conn.commit()
                            st.success("Escala salva!")
    else:
        st.error("Acesso negado. Apenas gerentes podem usar este sistema.")
