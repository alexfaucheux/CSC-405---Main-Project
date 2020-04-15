from flask import Flask
from config import Config
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from app.commands import create_tables, fill_image_table
from app.extensions import db

migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap()
login.login_view = "auth.login"
login.login_message = 'Please log in.'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:
        # FUTURE AUTOMATED TEST LOGGING HERE
        pass

    app.cli.add_command(create_tables)
    app.cli.add_command(fill_image_table)

    return app


from app import models
