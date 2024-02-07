class Config:
    DEBUG = False
    TESTING = False
    JWT_EXPIRATION = 3600


class ProductionConfig(Config):
    # TODO: Look at common production configurations
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'dev'


class TestingConfig(Config):
    TESTING = True
    DATABASE = 'sqlite:///:memory:'
