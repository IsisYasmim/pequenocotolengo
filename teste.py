import bcrypt
from firebase_config import get_db
from models.funcionario import Funcionario

db = get_db()
#user = funcionario.Funcionario.get_funcionario_por_id(db, "1")
funcionarios = db.collection('funcionarios')
docs = funcionarios.where('nome', '==', "Isis").stream()
funcionario = None
for doc in docs:
    data = doc.to_dict()
    funcionario = Funcionario(
        id=doc.id,
        nome=data.get('nome'),
        coren=data.get('coren'),
        cargo=data.get('cargo'),
        tipo_vinculo=data.get('tipo_vinculo'),
        data_admissao=data.get('data_admissao'),
        turno=data.get('turno'),
        local=data.get('local'),
        senha=data.get('senha')  # senha já vem como hash
    )
    break

senha = "123456"

hashed = data.get('senha') #bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()) 

print(f"Senha original: {senha}")
print(f"Senha criptografada: {hashed}")


if bcrypt.checkpw(senha.encode('utf-8'), hashed.encode('utf-8')):
    print("A senha confere!")
else:
    print("A senha não confere!")