import time
import streamlit as st
from firebase_config import get_db
from modules import login
from models.funcionario import Funcionario
from models.cargo import Cargo
from datetime import datetime, date
import calendar
from streamlit_js_eval import streamlit_js_eval

db = get_db()

def em_folga(funcionario_id, data_consulta):
    try:
        folgas_ref = db.collection('funcionarios').document(str(funcionario_id)) \
                      .collection('folgas').stream()
        
        for folga in folgas_ref:
            folga_data = folga.to_dict()
            try:
                di = datetime.fromisoformat(folga_data.get('dia_inicio'))
                df = datetime.fromisoformat(folga_data.get('dia_fim'))
                if di <= data_consulta <= df:
                    return True
            except:
                continue
        return False
    except:
        return False

def render_calendar_html(ano, mes, start_day, end_day):
    calendar.setfirstweekday(calendar.SUNDAY)
    dias_da_semana = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
    cal = calendar.monthcalendar(ano, mes)
    last_day_parity = calendar.monthrange(ano, mes)[1] % 2 == 0
    
    # Cabeçalho com fonte maior
    header_html = "".join([f"<th style='border: 1px solid #ccc; padding: 8px; text-align: center; font-size: 12pt; width: 14%;'>{d}</th>" for d in dias_da_semana])
    html = f"<table style='width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;'><thead><tr>{header_html}</tr></thead><tbody>"

    for semana in cal:
        html += "<tr>"
        for dia in semana:
            if dia == 0 or not (start_day <= dia <= end_day):
                html += "<td style='border: 1px solid #ccc; height: 120px; background-color: #f9f9f9;'></td>"
                continue

            prestadores = Funcionario.buscar_por_dia(db, dia, mes, ano, last_day_parity)
            cell_content = f"<div style='font-weight: bold; text-align: center; font-size: 14pt; margin-bottom: 5px;'>{dia}</div>"
            
            prestadores_noite = sorted(
                [p for p in prestadores if "Noite" in p.turno and not em_folga(p.id, date(ano, mes, dia))],
                key=lambda x: x.nome
            )

            prestadores_dia = sorted(
                [p for p in prestadores if "Dia" in p.turno and not em_folga(p.id, date(ano, mes, dia))],
                key=lambda x: x.nome
            )
            folgas = sorted(
                [
                    p for p in prestadores
                    if any(
                        datetime.fromisoformat(folga.to_dict()['dia_inicio']).date() <= date(ano, mes, dia) <= 
                        datetime.fromisoformat(folga.to_dict()['dia_fim']).date()
                        for folga in db.collection('funcionarios').document(str(p.id))
                                    .collection('folgas').stream()
                    )
                ],
                key=lambda x: x.nome
            )

            if prestadores_dia:
                cell_content += "<div style='font-size: 10pt; text-align: center; font-weight: bold; background-color: #e0e0e0; padding: 3px; margin: 2px 0;'>7h-19h</div>"
                for p in prestadores_dia:
                    cell_content += f"<div style='font-size: 10pt; background-color: #d1e7ff; padding: 4px; margin: 2px 0; border-radius: 3px;'>{p.nome.split()[0]} - {p.local}</div>"
            if prestadores_noite:
                cell_content += "<div style='font-size: 10pt; text-align: center; font-weight: bold; background-color: #e0e0e0; padding: 3px; margin: 2px 0;'>19h-7h</div>"
                for p in prestadores_noite:
                    cell_content += f"<div style='font-size: 10pt; background-color: #ffd1dc; padding: 4px; margin: 2px 0; border-radius: 3px;'>{p.nome.split()[0]} - {p.local}</div>"
            if folgas:
                cell_content += "<div style='font-size: 10pt; text-align: center; font-weight: bold; background-color: #e0e0e0; padding: 3px; margin: 2px 0;'>Folga</div>"
                for p in folgas:
                    cell_content += f"<div style='font-size: 10pt; background-color: #f0f0f0; padding: 4px; margin: 2px 0; border-radius: 3px;'>{p.nome.split()[0]}</div>"

            html += f"<td style='border: 1px solid #ccc; vertical-align: top; padding: 5px;'>{cell_content}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    return html

def show():
    login.logout_sidebar()
    login.check_login(db)
    st.header("Visualização Geral dos Plantões")

    # --- INJEÇÃO DE JAVASCRIPT E CSS PARA IMPRESSÃO ---
    st.markdown("""
    <script>
    // Função para preparar a impressão de uma div específica
    function printDiv(divId) {
        // Encontra todos os conteúdos 'imprimíveis' e remove a classe 'active-print'
        var allPrintableAreas = document.querySelectorAll('.printable-content');
        allPrintableAreas.forEach(function(area) {
            area.classList.remove('active-print');
        });

        // Adiciona a classe 'active-print' apenas na div que queremos imprimir
        var printableArea = document.getElementById(divId);
        if (printableArea) {
            printableArea.classList.add('active-print');
            window.print(); // Chama a impressão do navegador
        }
    }
    </script>
    <style>
    /* Estilos que são aplicados APENAS durante a impressão */
    @media print {
        /* Esconde tudo por padrão */
        body > * {
            display: none !important;
        }
        /* Mostra APENAS a área com a classe 'active-print' e seus filhos */
        .active-print, .active-print * {
            display: block !important;
        }
        /* Posiciona a área de impressão para ocupar a página toda */
        .active-print {
            position: absolute;
            top: 10px;
            left: 10px;
            width: 98%;
        }
        /* Garante que o container de colunas do Streamlit se comporte como uma tabela */
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    hoje = datetime.today()
    ano, mes = hoje.year, hoje.month
    ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
    
    # --- ABAS PARA CADA QUINZENA ---
    tab1, tab2 = st.tabs(["Imprimir 1ª Quinzena (1-15)", "Imprimir 2ª Quinzena (16-Fim)"])

    with tab1:
        st.subheader(f"Escala de {calendar.month_name[mes]} {ano} - Dias 1 a 15")
        if st.button("🖨️ Imprimir 1ª Quinzena", key="btn_q1"):
            # Chama a função JS para imprimir a div 'quinzena1'
            streamlit_js_eval(js_expressions="printDiv('quinzena1')")
        
        # Cria o conteúdo da primeira quinzena dentro de uma div com ID específico
        html_q1 = render_calendar_html(ano, mes, 1, 15)
        st.markdown(f"<div id='quinzena1' class='printable-content'>{html_q1}</div>", unsafe_allow_html=True)
        
    with tab2:
        st.subheader(f"Escala de {calendar.month_name[mes]} {ano} - Dias 16 a {ultimo_dia_mes}")
        if st.button(f"🖨️ Imprimir 2ª Quinzena", key="btn_q2"):
            # Chama a função JS para imprimir a div 'quinzena2'
            streamlit_js_eval(js_expressions="printDiv('quinzena2')")
            
        # Cria o conteúdo da segunda quinzena dentro de uma div com ID específico
        html_q2 = render_calendar_html(ano, mes, 16, ultimo_dia_mes)
        st.markdown(f"<div id='quinzena2' class='printable-content'>{html_q2}</div>", unsafe_allow_html=True)



if __name__ == "__main__":
    show()