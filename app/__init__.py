
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_pagedown import PageDown
from config import config, Config
from celery import Celery


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
pagedown = PageDown()

login_manager = LoginManager()           # provide login service
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'  # bind with view 'auth.login'

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL ,backend=Config.CELERY_RESULT_BACKEND)


def create_app(config_name):
    app = Flask(__name__)              # instance of app
    app._static_folder = "static"
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)  # pass configurations

    bootstrap.init_app(app)            # bind app with bootstrap/mail/moment/db/login, etc.
    mail.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    celery.conf.update(app.config)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .code import code as code_blueprint
    app.register_blueprint(code_blueprint, url_prefix='/code')

    return app
