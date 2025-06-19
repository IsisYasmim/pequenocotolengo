import time
import streamlit as st
from firebase_config import get_db
from modules import login
from models.funcionario import Funcionario

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
                    cols[1].write(f"**Data de Admissão:** {prestador.data_admissao.strftime('%d/%m/%Y')}")
                    btn_cols = st.columns(3)
                    # criando botões e registrando os estados de clique
                    btn1_clicado = btn_cols[0].button("Registrar Agendamento", key=f"editar_{prestador.id}", use_container_width=True)
                    btn2_clicado = btn_cols[1].button("Registrar Folga", key=f"registrar_folga_{prestador.id}", use_container_width=True)
                    btn3_clicado = btn_cols[2].button("Editar Prestador", key=f"editar_prestador_{prestador.id}", use_container_width=True)
                    
                    # lógica para lidar com os cliques dos botões
                    if btn1_clicado:
                        btn2_clicado = False
                        btn3_clicado = False
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
                            salvar_agendamento = st.form_submit_button("Salvar Agendamento",use_container_width=True)
                            '''if salvar_agendamento:
                                prestador.turno = turno
                                prestador.local = local
                                prestador.save(db)
                                st.success(f"Agendamento atualizado para {prestador.nome}!")'''

                        
                        

                    if btn2_clicado:
                        btn1_clicado = False
                        btn3_clicado = False
                        st.write("### Registrar Folga")
                        

                    if btn3_clicado:
                        btn1_clicado = False
                        btn2_clicado = False
                        st.write("### Editar Prestador")
                        


                

        except Exception as e:
            st.error(f"Erro ao buscar prestadores: {str(e)}")

if __name__ == "__main__":
    show()