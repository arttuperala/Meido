class Config(object):
    BUILD_DIRECTORY = ''
    MAILGUN_ENABLED = False
    MAILGUN_KEY = ''
    MAILGUN_SENDER = ''
    MAILGUN_URL = ''
    SECRET_KEY = ''
    SENTRY_DSN = ''
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False
    ENV = 'prod'
    MAILGUN_ENABLED = True
    SENTRY_DSN = ''
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/meido'


class DevelopmentConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    ENV = 'dev'
    SEND_FILE_MAX_AGE_DEFAULT = 10
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/meido_dev'


class TestConfig(Config):
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    ENV = 'test'
    MAILGUN_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/meido_test'
    TEST = True
    WTF_CSRF_ENABLED = False
