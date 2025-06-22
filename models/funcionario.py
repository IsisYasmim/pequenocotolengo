from datetime import date
import bcrypt
from firebase_config import get_db, get_funcionarios_len
import uuid
from datetime import datetime

db = get_db()

class Funcionario:
    def __init__(self, nome, matricula, coren, cargo, tipo_vinculo, data_admissao, turno=None, local=None, senha=None, id=None):
        self.id = id
        self.nome = nome
        self.matricula = matricula
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
            docs = funcionarios.stream()
            ids = [int(doc.id) for doc in docs if doc.id.isdigit()]
            novoId = str(max(ids) + 1) if ids else "1"

            funcionario_data = {
                'id': novoId,
                'nome': self.nome,
                'matricula': self.matricula,
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
            raise Exception(f"{str(e)}")

    def delete(self, db):
        try:
            doc_ref = db.collection("funcionarios").document(self.id)
            doc_ref.delete()
        except Exception as e:
            raise Exception(f"Erro ao excluir funcionário: {str(e)}")

    def update_por_id(self, db, dados_atualizados: dict):
        try:
            doc_ref = db.collection('funcionarios').document(str(self.id))
            doc = doc_ref.get()

            if not doc.exists:
                raise ValueError(f"Funcionário com ID {id} não encontrado.")

            # atualiza apenas os campos fornecidos como parametros
            doc_ref.update(dados_atualizados)

        except Exception as e:
            raise Exception(f"Erro ao atualizar funcionário: {str(e)}")
    
    def adicionar_folga(self, db, folga_data):
        try:
            folga_ref = db.collection('funcionarios').document(str(self.id)).collection('folgas')
            folga_ref.add({
                'folga_id': str(uuid.uuid1()),
                'dia_inicio': folga_data['dia_inicio'],
                'dia_fim': folga_data['dia_fim']
            })
        except Exception as e:
            raise Exception(f"Erro ao adicionar folga: {str(e)}")

    def remover_folga(self, db, folga_id):
        try:
            db.collection('funcionarios').document(str(self.id)) \
              .collection('folgas').document(folga_id).delete()
            return True
        except Exception as e:
            raise Exception(f"Erro ao remover folga: {str(e)}")

    def obter_folgas(self, db):
        try:
            folgas_ref = db.collection('funcionarios').document(str(self.id)) \
                        .collection('folgas').stream()
            folgas = [{'id': folga.id, **folga.to_dict()} for folga in folgas_ref]
            return folgas if folgas else None  # Retorna None se a lista estiver vazia
        except Exception as e:
            raise Exception(f"Erro ao obter folgas: {str(e)}") 
            

    @staticmethod
    def get_all(db):
        try:
            funcionarios_ref = db.collection('funcionarios').stream()
            return [f.to_dict() for f in funcionarios_ref]
        except Exception as e:
            raise Exception(f"Erro ao buscar funcionários: {str(e)}")
    
    @staticmethod
    def buscar_por_coren(db, coren):
        try:
            resultado = db.collection('funcionarios').where('coren', '==', coren).get()
            return resultado.to_dict() if resultado else None
        except Exception as e:
            raise Exception(f"Erro ao buscar funcionário: {str(e)}")


    @classmethod
    def get_funcionario_por_id(cls, db, id):
        try:
            doc = db.collection('funcionarios').document(str(id)).get()
            if doc.exists:
                data = doc.to_dict()
                return cls(
                id=id,
                nome=data['nome'],
                matricula=data['matricula'],
                coren=data['coren'],
                cargo=data['cargo'],
                tipo_vinculo=data['tipo_vinculo'],
                data_admissao=data['data_admissao'],
                turno=data['turno'],
                local=data['local'],
                senha=data['senha']
                )
            else:
                return None
        except Exception as e:
            raise Exception(f"Erro ao buscar funcionário: {str(e)}")

    

    @classmethod
    def buscar_por_dia(cls, db, dia, mes, ano, last_day_parity=None):
        try:
            funcionarios_ref = db.collection('funcionarios')
            docs = funcionarios_ref.stream()
            prestadores = []

            data_consulta = date(ano, mes, dia)

            for doc in docs:
                data = doc.to_dict()
                turno = data.get("turno")
                local = data.get("local", "UH")

                # Verifica folgas
                em_folga = False

                try:
                    folgas_ref = funcionarios_ref.document(doc.id).collection('folgas').stream()
                    for folga in folgas_ref:
                        folga_data = folga.to_dict()
                        dia_inicio = datetime.fromisoformat(folga_data.get('dia_inicio')).date()
                        dia_fim = datetime.fromisoformat(folga_data.get('dia_fim')).date()
                        if dia_inicio <= data_consulta <= dia_fim:
                            em_folga = True
                            break
                except Exception as e:
                    raise Exception(f"Erro ao acessar folgas: {str(e)}")
                
                # Lógica de escala
                if turno:
                    if not em_folga:
                        if last_day_parity is None:
                            if (turno == "Dia 1" and dia % 2 == 1) or (turno == "Dia 2" and dia % 2 == 0) or \
                            (turno == "Noite 1" and dia % 2 == 1) or (turno == "Noite 2" and dia % 2 == 0):
                                data["id"] = doc.id
                                data["local"] = local
                                prestadores.append(cls.from_dict(data))
                        else:
                            if last_day_parity:
                                if (turno == "Dia 2" and dia % 2 == 1) or (turno == "Dia 1" and dia % 2 == 0) or \
                                (turno == "Noite 2" and dia % 2 == 1) or (turno == "Noite 1" and dia % 2 == 0):
                                    data["id"] = doc.id
                                    data["local"] = local
                                    prestadores.append(cls.from_dict(data))
                            else:
                                if (turno == "Dia 1" and dia % 2 == 1) or (turno == "Dia 2" and dia % 2 == 0) or \
                                (turno == "Noite 1" and dia % 2 == 1) or (turno == "Noite 2" and dia % 2 == 0):
                                    data["id"] = doc.id
                                    data["local"] = local
                                    prestadores.append(cls.from_dict(data))
                    else:
                        # adiciona mesmo se estiver em folga, para aparecer na escala
                        data["id"] = doc.id
                        data["local"] = local
                        prestadores.append(cls.from_dict(data))

            return prestadores

        except Exception as e:
            raise Exception(f"Erro ao buscar funcionários por dia: {str(e)}")
    
    @classmethod
    def buscar_por_nome(cls, db, nome):
        try:
            query = db.collection('funcionarios').where('nome', '==', nome).stream()
            return [
                cls(
                    id=doc.id,  # <- importante
                    nome=data.get("nome"),
                    matricula=data.get("matricula"),
                    coren=data.get("coren"),
                    cargo=data.get("cargo"),
                    tipo_vinculo=data.get("tipo_vinculo"),
                    data_admissao=data.get("data_admissao"),
                    turno=data.get("turno", ""),  # opcional
                    local=data.get("local", "")   # opcional
                )
                for doc in query
                if (data := doc.to_dict()) is not None
            ]
        except Exception as e:
            raise Exception(f"Erro ao buscar funcionários por nome: {str(e)}")

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            nome=data.get("nome"),
            matricula=data.get("matricula"),
            coren=data.get("coren"),
            cargo=data.get("cargo"),
            tipo_vinculo=data.get("tipo_vinculo"),
            data_admissao=data.get("data_admissao"),
            turno=data.get("turno"),
            local=data.get("local"),
            senha=data.get("senha")
        )
