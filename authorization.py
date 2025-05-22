from flask_jwt_extended import get_jwt_identity, get_jwt, jwt_required
from flask import Blueprint, jsonify
from models import Funcionario


authorization_blueprint = Blueprint('authorization', __name__)


@authorization_blueprint.get('/rota')
@jwt_required()
def user_profile():
    current_user = get_jwt_identity()

    current_user_claims = get_jwt()

    funcionario = Funcionario.get_funcionario_por_id(id=current_user)

    if not funcionario:
        return jsonify({"message": "Usuário não encontrado :(",
                        "nome": current_user
                        }), 404

    return jsonify({
        "message": "Eba! Acesso liberado!",
        "funcionario_info": {
            "id": funcionario.id,
            "token_info": {
                "funcionario_id": current_user_claims["user_id"],
                "nome": current_user_claims["username"]
            }
        }
    }), 200
