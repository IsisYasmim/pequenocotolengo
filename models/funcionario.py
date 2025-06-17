from datetime import date
import bcrypt
from firebase_config import get_db, get_funcionarios_len

db = get_db()

class Funcionario:
    def __init__(self, nome, coren, cargo, tipo_vinculo, data_admissao, turno=None, local=None, senha=None, id=None):
        self.id = id
        self.nome = nome
        self.coren = coren
        self.cargo = cargo
        self.tipo_vinculo = tipo_vinculo
        self.data_admissao = data_admissao
        self.turno = turno
        self.local = local
        self.senha = senha

    def set_senha(self, senha):
        return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') 

    def checa_senha(self, senha):
        return bcrypt.checkpw(senha.encode('utf-8'), self.senha.encode('utf-8'))

    def save(self, db):
        try:
            funcionarios = db.collection('funcionarios')

            # checa se já existe um funcionário com o mesmo COREN
            if funcionarios.where('coren', '==', self.coren).get():
                raise ValueError("Já existe um funcionário com este COREN.")

            # define o id a partir do tamanho da coleção
            novoId = str(get_funcionarios_len() + 1)

            funcionario_data = {
                'id': novoId,
                'nome': self.nome,
                'coren': self.coren,
                'cargo': self.cargo,
                'tipo_vinculo': self.tipo_vinculo,
                'data_admissao': self.data_admissao.isoformat(),
                'turno': self.turno,
                'local': self.local,
                'senha': self.set_senha(self.senha) if self.senha else None
            }
            # salva o funcionário no Firestore
            funcionarios.document(novoId).set(funcionario_data)
            # atualiza o id do objeto
            self.id = novoId 

        except Exception as e:
            raise Exception(f"Erro ao salvar funcionário: {str(e)}")

    @classmethod
    def get_funcionario_por_id(db, id):
        try:
            doc = db.collection('funcionarios').document(str(id)).get()
            if doc.exists:
                data = doc.to_dict()
                return Funcionario(
                id=id,
                nome=data['nome'],
                coren=data['coren'],
                cargo=data['cargo'],
                tipo_vinculo=data['tipo_vinculo'],
                data_admissao=data['data_admissao'],
                turno=data['turno'],
                local=data['local'],
                senha=data['senha']  # já está em hash
            )
            else:
                return None
        except Exception as e:
            raise Exception(f"Erro ao buscar funcionário: {str(e)}")

    @classmethod
    def buscar_por_nome(db, nome):
        try:
            nome = nome.strip().lower()
            funcionarios = db.collection('funcionarios')
            docs = funcionarios.stream()

            resultados = []
            for doc in docs:
                data = doc.to_dict()
                nome_doc = data.get('nome', '').strip().lower()
                if nome_doc == nome:
                    resultados.append(Funcionario(
                        id=doc.id,
                        nome=data['nome'],
                        coren=data['coren'],
                        cargo=data['cargo'],
                        tipo_vinculo=data['tipo_vinculo'],
                        data_admissao=data['data_admissao'],
                        turno=data['turno'],
                        local=data['local'],
                        senha=data['senha']
                    ))
            return resultados
        except Exception as e:
            raise Exception(f"Erro ao buscar por nome: {str(e)}")

''' ----  AJUSTAR DEPOIS DA IMPLEMENTAÇÃO DO FIREBASE -----

    @classmethod
    def buscar_por_dia(cls, dia, mes, ano, last_day_parity=None):
        try:
            # Implementar a lógica de busca por dia no Firebase
            # Esta é uma implementação simplificada - você precisará adaptar
            all_funcionarios = db.collection('funcionarios').stream()
            prestadores = []
            
            for doc in all_funcionarios:
                funcionario = cls._doc_to_funcionario(doc)
                if funcionario.turno:
                    # Mesma lógica de paridade do dia original
                    if last_day_parity is None:  # Mês atual
                        if (funcionario.turno == "Dia 1" and dia % 2 == 1) or (funcionario.turno == "Dia 2" and dia % 2 == 0) or \
                           (funcionario.turno == "Noite 1" and dia % 2 == 1) or (funcionario.turno == "Noite 2" and dia % 2 == 0):
                            prestadores.append(funcionario)
                    else:  # Próximo mês
                        if last_day_parity:  # Último dia par
                            if (funcionario.turno == "Dia 2" and dia % 2 == 1) or (funcionario.turno == "Dia 1" and dia % 2 == 0) or \
                               (funcionario.turno == "Noite 2" and dia % 2 == 1) or (funcionario.turno == "Noite 1" and dia % 2 == 0):
                                prestadores.append(funcionario)
                        else:  # Último dia ímpar
                            if (funcionario.turno == "Dia 1" and dia % 2 == 1) or (funcionario.turno == "Dia 2" and dia % 2 == 0) or \
                               (funcionario.turno == "Noite 1" and dia % 2 == 1) or (funcionario.turno == "Noite 2" and dia % 2 == 0):
                                prestadores.append(funcionario)
                if not funcionario.local:
                    funcionario.local = "UH"
            return prestadores
        except Exception as e:
            raise Exception(f"Erro ao buscar por dia: {str(e)}")

    @classmethod
    def _doc_to_funcionario(cls, doc):
        data = doc.to_dict()
        data['data_admissao'] = date.fromisoformat(data['data_admissao'])
        funcionario = cls(**{k: v for k, v in data.items() if k != '_senha_hash'})
        if '_senha_hash' in data:
            funcionario._senha_hash = data['_senha_hash']
        return funcionario

    @classmethod
    def atualizar_aj_para_ft(cls):
        try:
            hoje = date.today()
            funcionarios_ref = db.collection('funcionarios')
            docs = funcionarios_ref.where('tipo_vinculo', '==', 'AJ - PROGRAMA ANJO').stream()
            
            for doc in docs:
                data = doc.to_dict()
                data_admissao = date.fromisoformat(data['data_admissao'])
                dias_desde_admissao = (hoje - data_admissao).days
                if dias_desde_admissao >= 7:
                    doc.reference.update({'tipo_vinculo': 'FT - EFETIVADO'})
        except Exception as e:
            raise Exception(f"Erro ao atualizar AJ para FT: {str(e)}")'''