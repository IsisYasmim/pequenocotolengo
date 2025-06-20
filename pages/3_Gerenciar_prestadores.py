import time
import streamlit as st
from firebase_config import get_db
from modules import login
from models.funcionario import Funcionario
from models.cargo import Cargo
from datetime import date, datetime

def show():
    db = get_db()

    st.header("Gerenciar Prestadores Cadastrados")
    login.logout_sidebar()

    funcionarios = [f["nome"] for f in Funcionario.get_all(db)]
    nome_busca = st.selectbox("Digite o nome do prestador", funcionarios, key="busca_prestador", index=None, placeholder="Selecione um prestador")

    if nome_busca:
        try:
            prestadores = Funcionario.buscar_por_nome(db, nome_busca.strip())
            if not prestadores:
                st.warning("Nenhum registro encontrado com esse nome.")
                return

            for prestador in prestadores:
                with st.container(border=True):
                    st.subheader(f"Prestador(a): {prestador.nome}")
                    cols = st.columns(3)
                    cols[0].write(f"**Matrícula:** {prestador.id}")
                    cols[1].write(f"**COREN:** {prestador.coren}")
                    cols[2].write(f"**Cargo:** {prestador.cargo}")
                    cols[0].write(f"**Tipo de Vínculo:** {prestador.tipo_vinculo}")
                    cols[1].write(f"**Data de Admissão:** {prestador.data_admissao}")
                    btn_cols = st.columns(3)
                    # criando botões e registrando os estados de clique
                    btn1_clicado = btn_cols[0].button("Registrar Agendamento", key=f"agendamento_{prestador.id}", use_container_width=True)
                    btn2_clicado = btn_cols[1].button("Registrar Folga", key=f"registrar_folga_{prestador.id}", use_container_width=True)
                    btn3_clicado = btn_cols[2].button("Editar Prestador", key=f"editar_prestador_{prestador.id}", use_container_width=True)
                    
                    # lógica para lidar com os cliques dos botões
                    key_estado = f"estado_acao_{prestador.id}"
                    if key_estado not in st.session_state:
                        st.session_state[key_estado] = None  # Nenhuma ação ativa inicialmente
                    
                    if btn1_clicado:
                        st.session_state[key_estado] = "agendamento"
                    elif btn2_clicado:
                        st.session_state[key_estado] = "folga"
                    elif btn3_clicado:
                        st.session_state[key_estado] = "editar"

                    # Renderiza o formulário com base na ação ativa
                    acao_ativa = st.session_state[key_estado]
         
                    if acao_ativa == "agendamento":
                        with st.form(f"form_agendamento_{prestador.id}"):
                            turno = st.selectbox(
                                "Turno",
                                ["Dia 1", "Dia 2", "Noite 1", "Noite 2"],
                                key=f"turno_{prestador.id}",
                                index=["Dia 1", "Dia 2", "Noite 1", "Noite 2"].index(prestador.turno) if prestador.turno else 0
                            )
                            local = st.selectbox(
                                "Local",
                                ["UH", "UCCI"],
                                key=f"local_{prestador.id}",
                                index=["UH", "UCCI"].index(prestador.local) if prestador.local else 0
                            )
                            salvar_agendamento = st.form_submit_button("Salvar Agendamento", use_container_width=True)
                            if salvar_agendamento:
                                try:
                                    dados = {"turno": turno, "local": local}
                                    prestador.update_por_id(db, dados)
                                    st.success(f"Agendamento atualizado para {prestador.nome}!")
                                    # mantém o formulário aberto, mas você pode resetar se quiser
                                    # st.session_state[key_estado] = None
                                except Exception as e:
                                    st.error(f"Erro ao atualizar agendamento: {str(e)}")

                    elif acao_ativa == "folga":
                        st.write("### Registrar Folga")
                        st.info("Funcionalidade de folga em construção.")
                        

                    elif acao_ativa == "editar":
                        with st.form("form_adicionar_prestador"):
                            nome = st.text_input("Nome completo", key="nome_prestador")
                            matricula = st.text_input("Matrícula (MAT)", key="mat_prestador")
                            coren = st.text_input("COREN", key="coren_prestador")
                            
                            cargos = [c["nome_do_cargo"] for c in Cargo.get_all(db)]
                            if cargos:
                                cargo = st.selectbox("Cargo", cargos, key="cargo_prestador", index=cargos.index(prestador.cargo) if prestador.cargo else 0)
                            else:
                                cargo = st.selectbox()("Cargo", ["Nenhum cargo cadastrado"], key="cargo_prestador")

                            data_admissao = st.date_input("Data de admissão", key="data_prestador")
                            tipo_vinculo = st.selectbox(
                                "Tipo de vínculo",
                                ["AJ - PROGRAMA ANJO", "FT - EFETIVADO"],
                                key="vinculo_prestador",
                                index=["AJ - PROGRAMA ANJO", "FT - EFETIVADO"].index(prestador.tipo_vinculo) if prestador.tipo_vinculo else 0
                            )
                            salvar = st.form_submit_button("Salvar")
                        if salvar:
                            try:
                                dados = {
                                    "nome": nome,
                                    "matricula": matricula,
                                    "coren": coren,
                                    "cargo": cargo,
                                    "tipo_vinculo": tipo_vinculo,
                                    "data_admissao": data_admissao.isoformat() if data_admissao else None
                                }
                                # remove as chaves com valores None ou strings vazias
                                dados = {k: v for k, v in dados.items() if v not in [None, ""]}
                                prestador.update_por_id(db, dados)
                                st.success("Prestador atualizado com sucesso!")
                            except Exception as e:
                                st.error(f"Erro ao atualizar prestador: {str(e)}")
                    
                
                        
                        

        except Exception as e:
            st.error(f"Erro ao buscar prestadores: {str(e)}")

if __name__ == "__main__":
    show()