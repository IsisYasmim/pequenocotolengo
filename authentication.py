from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from models import Funcionario

authentication_blueprint = Blueprint('auth', __name__)


@authentication_blueprint.post('/register')
def register_user():
    data = request.get_json()  # pega o json mandado no request
    # pesquisa o id no banco e coloca na variavel
    funcionario = Funcionario.get_funcionario_por_id(id=data.get('id'))

    if funcionario is not None:
        # checa se o usuario ja existe
        return jsonify({"error": "Usuario ja existe, baby"}), 409

    novo_usuario = Funcionario(
        id=data.get('id'),
        nome=data.get('nome'),
        coren=data.get('coren'),
        senha=data.get('senha'),
        cargo=data.get('cargo'),
        tipo_vinculo=data.get('tipo_vinculo'),
        data_admissao=data.get('data_admissao'),
        gerente=data.get('gerente', False)  # padrao falso se nao for passado
    )

    novo_usuario.set_senha(password=data.get('senha'))

    novo_usuario.save()

    return jsonify({"message": "Usuario criado com sucesso e carinho!"}), 201


@authentication_blueprint.post('/login')
def login():
    data = request.get_json()  # pega o json mandado no request
    funcionario = Funcionario.get_funcionario_por_id(id=data.get('id'))

    if funcionario and (funcionario.checa_senha(senha=data.get('senha'))):
        additional_claims = {
            "funcionario_id": funcionario.id,
            "nome": funcionario.nome
        }
        access_token = create_access_token(
            identity=funcionario.id,
            additional_claims=additional_claims
        )

        return jsonify(
            {
                "message": "Logado <3",
                "access": access_token
            }
            ), 200

    return jsonify({"error": "Usuário ou senha inválido(s)"}), 400
