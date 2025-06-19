from datetime import datetime
from firebase_config import get_db, get_cargos_len

class Cargo:
    def __init__(self, nome_do_cargo, id=None):
        self.id = id
        self.nome_do_cargo = nome_do_cargo

    def save(self, db):
        try:
            cargos_ref = db.collection("cargos")

            # verifica se já existe um cargo com o mesmo nome
            if cargos_ref.where("nome_do_cargo", "==", self.nome_do_cargo).get():
                raise ValueError("Já existe um cargo com esse nome.")

            # define o id a partir do tamanho da coleção
            novo_id = str(get_cargos_len() + 1)

            cargo_data = {
                "id": novo_id,
                "nome_do_cargo": self.nome_do_cargo
            }
            self.id = novo_id  # atualiza o id do objeto
            # salva o cargo no Firestore
            cargos_ref.document(self.id).set(cargo_data)
        except Exception as e:
            raise Exception(f"Erro ao salvar cargo: {str(e)}")

    @staticmethod
    def get_all(db):
        try:
            cargos_ref = db.collection("cargos").stream()
            return [doc.to_dict() for doc in cargos_ref]
        except Exception as e:
            raise Exception(f"Erro ao buscar cargos: {str(e)}")

    @staticmethod
    def get_by_id(db, id):
        try:
            doc = db.collection("cargos").document(id).get()
            if doc.exists:
                return doc.to_dict()
            else:
                return None
        except Exception as e:
            raise Exception(f"Erro ao buscar cargo por ID: {str(e)}")

    def update(self, db):
        try:
            cargo_ref = db.collection("cargos").document(self.id)
            if not cargo_ref.get().exists:
                raise ValueError("Cargo não encontrado para atualização.")

            cargo_ref.update({
                "nome_do_cargo": self.nome_do_cargo,
                "atualizado_em": datetime.now().isoformat()
            })
        except Exception as e:
            raise Exception(f"Erro ao atualizar cargo: {str(e)}")

    @staticmethod
    def delete(db, id):
        try:
            cargo_ref = db.collection("cargos").document(id)
            if cargo_ref.get().exists:
                cargo_ref.delete()
            else:
                raise ValueError("Cargo não encontrado para exclusão.")
        except Exception as e:
            raise Exception(f"Erro ao excluir cargo: {str(e)}")
