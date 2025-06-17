import time
import streamlit as st
from firebase_config import get_db
from modules import login
from models.funcionario import Funcionario

def show():
    db = get_db()

    st.header("Gerenciar Prestadores Cadastrados")
    login.logout_sidebar()

    nome_busca = st.text_input("Digite o nome do prestador para buscar", key="busca_prestador")

    if nome_busca:
        try:
            prestadores = Funcionario.buscar_por_nome(db, nome_busca.strip())
            st.write(f"DEBUG: Prestadores encontrados: {len(prestadores)}")

            if not prestadores:
                st.warning("Nenhum prestador encontrado com esse nome.")
                return

            for prestador in prestadores:
                st.subheader(f"Prestador: {prestador.nome}")
                st.write(f"Matrícula: {prestador.id}")
                st.write(f"COREN: {prestador.coren}")
                st.write(f"Cargo: {prestador.cargo}")
                st.write(f"Tipo de Vínculo: {prestador.tipo_vinculo}")
                st.write(f"Data de Admissão: {prestador.data_admissao}")

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
                    salvar_agendamento = st.form_submit_button("Salvar Agendamento")
                    excluir = st.form_submit_button("Excluir Prestador")

                    if salvar_agendamento:
                        prestador.turno = turno
                        prestador.local = local
                        prestador.save(db)
                        st.success(f"Agendamento atualizado para {prestador.nome}!")
                        time.sleep(1)
                        st.session_state["pagina"] = "menu"
                        st.rerun()

                    if excluir:
                        prestador.delete(db)
                        st.success(f"Prestador {prestador.nome} excluído com sucesso!")
                        time.sleep(1)
                        st.session_state["pagina"] = "menu"
                        st.rerun()

        except Exception as e:
            st.error(f"Erro ao buscar prestadores: {str(e)}")

if __name__ == "__main__":
    show()