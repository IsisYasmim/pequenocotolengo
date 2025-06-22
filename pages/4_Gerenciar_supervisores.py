import streamlit as st
from firebase_config import get_db
from models.funcionario import Funcionario
from datetime import datetime, date
from modules import login

def show():
    db = get_db()
    login.check_login(db)
    login.logout_sidebar()

    usuario_atual = st.session_state["usuario"]
    
    st.title("Gerenciamento de Supervisores")
    
    # Abas para diferentes operações
    tab1, tab2 = st.tabs(["Editar Meu Perfil", "Cadastrar Novo Supervisor"])
    
    with tab1:
        st.header("Editar Meu Perfil")
        with st.form("editar_supervisor"):
            nome = st.text_input("Nome Completo", value=usuario_atual.nome)
            matricula = st.text_input("Matrícula", value=usuario_atual.matricula)
            coren = st.text_input("COREN", value=usuario_atual.coren)
            senha = st.text_input("Nova Senha", type="password", placeholder="Deixe em branco para manter senha a atual")
            confirma_senha = st.text_input("Confirmar Nova Senha", type="password", placeholder="Deixe em branco para manter senha a atual")
            
            if st.form_submit_button("Salvar Alterações", use_container_width=True):
                try:
                    dados_atualizados = {
                        "nome": nome,
                        "matricula": matricula,
                        "coren": coren
                    }
                    
                    # Atualiza senha apenas se foi informada
                    if senha:
                        if senha == confirma_senha:
                            dados_atualizados["senha"] = usuario_atual.set_senha(senha)
                        else:
                            st.error("As senhas não coincidem")
                            return
                            
                    
                    # Atualiza no banco de dados
                    usuario_atual.update_por_id(db, dados_atualizados)
                    
                    # Atualiza na sessão
                    st.session_state["usuario"].nome = nome
                    st.session_state["usuario"].matricula = matricula
                    st.session_state["usuario"].coren = coren
                    
                    st.success("Perfil atualizado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao atualizar perfil: {str(e)}")
    
    with tab2:
        st.header("Cadastrar Novo Supervisor")
        with st.form("novo_supervisor"):
            novo_nome = st.text_input("Nome Completo")
            nova_matricula = st.text_input("Matrícula")
            novo_coren = st.text_input("COREN")
            novo_data_admissao = st.date_input("Data de admissão*", value=date.today(), key="data_prestador")
            novo_tipo_vinculo = st.selectbox(
            "Tipo de vínculo",
            ["AJ - PROGRAMA ANJO", "FT - EFETIVADO"],
            key="vinculo_prestador"
            )
            nova_senha = st.text_input("Senha", type="password")
            nova_confirma_senha = st.text_input("Confirmar Senha", type="password")
            
            if st.form_submit_button("Cadastrar Supervisor"):
                if nova_senha != nova_confirma_senha:
                    st.error("As senhas não coincidem")
                else:
                    try:
                        novo_cargo = "Supervisor"
                        novo = Funcionario(novo_nome, nova_matricula, novo_coren, novo_cargo, novo_tipo_vinculo, novo_data_admissao, senha=nova_senha)
                        novo.save(db)
                        st.success("Supervisor cadastrado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao cadastrar supervisor: {str(e)}")

if __name__ == "__main__":
    show()