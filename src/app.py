import os

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask_migrate import Migrate
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from src.models import db

migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()
ma = Marshmallow()
spec = APISpec(
    title="DIO Bank",
    version="1.0.0",
    openapi_version="3.0.3",
    info=dict(description="DIO Bank API"),
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)


def create_app(environment=os.environ["ENVIRONMENT"]):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(f"src.config.{environment.title()}Config")

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)
    
    # register blueprints
    from src.controllers import user, post, auth, role
    
    app.register_blueprint(user.app)
    app.register_blueprint(post.app)
    app.register_blueprint(auth.app)
    app.register_blueprint(role.app)
    
    @app.route("/docs")
    def docs():
        return spec.path(view=user.get_user).path(view=user.delete_user).to_dict()

    return app
