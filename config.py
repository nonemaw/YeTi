import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # MASTER_KEY: for password encryption / decryption
    # SECRET_KEY: for token encryption / decryption
    MASTER_KEY = os.environ.get('MASTER_KEY') or 'QnpNp9A5tUFJKnQtWXRBHSnknRil24JmH'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'JuFhrkPDQ3y5P1ad6lREcQ'
    MAIL_SUBJECT_PREFIX = '[YeTi OJ]'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'michaelxuchj@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SENDER = 'YeTi Admin <michaelxuchj@gmail.com>'
    SITE_ADMIN = os.environ.get('SITE_ADMIN') or 'michaelxuchj@gmail.com'
    CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672/'
    CELERY_RESULT_BACKEND = 'amqp://guest:guest@localhost:5672/'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


config = {
    'test': TestingConfig,
    'production': Config,
    'default': DevelopmentConfig
}
