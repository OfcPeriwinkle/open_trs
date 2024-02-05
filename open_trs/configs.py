class Config:
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite:////tmp/trs.db'


class ProductionConfig(Config):
    # TOOD: Look at common production configurations
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DATABASE_URI = 'sqlite:///:memory:'
