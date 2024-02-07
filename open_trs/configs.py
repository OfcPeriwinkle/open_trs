class Config:
    DEBUG = False
    TESTING = False
    JWT_EXPIRATION = 3600


class ProductionConfig(Config):
    # TODO: Look at common production configurations
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'secret'


class TestingConfig(Config):
    TESTING = True
    DATABASE = 'file::memory:?cache=shared'
    SECRET_KEY = 'secret'


class GitHubActionsConfig(TestingConfig):
    DATABASE = 'sqlite:///open_trs.db'
