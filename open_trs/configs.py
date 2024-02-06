class Config:
    DEBUG = False
    TESTING = False


class ProductionConfig(Config):
    # TOOD: Look at common production configurations
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'dev'


class TestingConfig(Config):
    TESTING = True
    DATABASE = 'sqlite:///:memory:'
