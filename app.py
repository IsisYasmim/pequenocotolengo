from flask import Flask
from extensions import database as db, jwt
from authentication import authentication_blueprint
from authorization import authorization_blueprint as ab


def criar_app():
    app = Flask(__name__)

    # pega as variaveis do ambiente definidas no arquivo .env
    app.config.from_prefixed_env()

    # inicializa db e jwt
    db.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(authentication_blueprint, url_prefix='/auth')
    app.register_blueprint(ab, url_prefix='/authorization')

    @app.route('/')
    def oii():
        return 'hewwooo'
    return app


app = criar_app()
