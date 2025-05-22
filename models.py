from extensions import database as db
import bcrypt


class Funcionario(db.Model):
    __tablename__ = 'funcionarios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(), nullable=False)
    coren = db.Column(db.String(), unique=True, nullable=False)
    senha = db.Column(db.String(), nullable=False)
    cargo = db.Column(db.String(), nullable=False)
    tipo_vinculo = db.Column(db.String(), nullable=False)
    data_admissao = db.Column(db.Date, nullable=False)
    gerente = db.Column(db.Boolean, default=False)

    def set_senha(self, senha):
        self.senha = bcrypt.hashpw(
            senha.encode('utf-8'),
            bcrypt.gensalt()
            )

    def checa_senha(self, senha):
        return bcrypt.checkpw(
            senha.encode('utf-8'),
            self.senha
            )

    def __repr__(self):
        return f"<Funcionario {self.id}>"

    @classmethod
    def get_funcionario_por_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
