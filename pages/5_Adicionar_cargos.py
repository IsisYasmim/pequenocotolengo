import streamlit as st
from firebase_config import get_db
from models.cargo import Cargo
from modules import login
from time import sleep

def show():
    db = get_db()
    
    login.check_login(db)
    
    st.title("📋 Gerenciamento de Cargos")
    login.logout_sidebar()
    
    # Abas para diferentes operações
    tab1, tab2 = st.tabs(["Lista de Cargos", "Adicionar Novo Cargo"])
    
    with tab1:
        st.header("Cargos Cadastrados")
        
        try:
            cargos = Cargo.get_all(db)
            
            if not cargos:
                st.info("Nenhum cargo cadastrado ainda.")
            else:
                # Ordena cargos alfabeticamente
                cargos_ordenados = sorted(cargos, key=lambda x: x['nome_do_cargo'].lower())
                
                for cargo in cargos_ordenados:
                    with st.expander(f"🔸 {cargo['nome_do_cargo']}"):
                        col1, col2 = st.columns([4, 1])
                        col1.write(f"**ID:** {cargo['id']}")
                        
                        # Botão de exclusão com confirmação
                        if col2.button("🗑️ Excluir", key=f"del_{cargo['id']}"):
                            if st.button(f"Confirmar exclusão de {cargo['nome_do_cargo']}?", key=f"conf_del_{cargo['id']}"):
                                try:
                                    Cargo.delete(db, cargo['id'])
                                    st.success(f"Cargo {cargo['nome_do_cargo']} excluído!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao excluir: {str(e)}")
        
        except Exception as e:
            st.error(f"Erro ao carregar cargos: {str(e)}")
    
    with tab2:
        st.header("Adicionar Novo Cargo")
        
        with st.form("novo_cargo", clear_on_submit=True):
            novo_cargo = st.text_input("Nome do Cargo*", placeholder="Ex: Enfermeiro Chefe")
            
            if st.form_submit_button("Salvar Cargo"):
                if not novo_cargo:
                    st.error("O nome do cargo é obrigatório")
                else:
                    try:
                        cargo = Cargo(nome_do_cargo=novo_cargo.strip())
                        cargo.save(db)
                        st.success(f"Cargo '{novo_cargo}' cadastrado com sucesso!")
                        sleep(1) 
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"Erro inesperado: {str(e)}")

if __name__ == "__main__":
    show()