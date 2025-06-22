import firebase_admin
import streamlit as st
from firebase_admin import credentials, firestore
import os
import json

# inicia o db
if not firebase_admin._apps:
    key_dict= json.loads(st.secrets['textkey'])
    # credenciais NÃO podem ser públicas (não serão adicionadas ao repositório)
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)

# manda o db para as outras classes
def get_db():
    return firestore.client()

def get_funcionarios_len():
    db = get_db()
    funcionarios = db.collection('funcionarios')
    docs = funcionarios.stream()
    # retorna o tamanho da coleção de funcionários
    return len(list(docs))

def get_cargos_len():
    db = get_db()
    cargos = db.collection('cargos')
    docs = cargos.stream()
    # retorna o tamanho da coleção de cargos
    return len(list(docs))  