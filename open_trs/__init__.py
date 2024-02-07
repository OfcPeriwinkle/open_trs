import os

from flask import Flask

import open_trs.configs
import open_trs.db
import open_trs.auth

CONFIGS = {
    'development': open_trs.configs.DevelopmentConfig,
    'testing': open_trs.configs.TestingConfig,
    'production': open_trs.configs.ProductionConfig
}


def create_app(testing: bool = False):
    """
    Create and configure the Flask application.

    Args:
        testing (bool, optional): Flag indicating whether the application is running in testing
            mode; defaults to False.

    Returns:
        The configured Flask application.
    """

    app = Flask(__name__, instance_relative_config=True)

    # Configure the app
    if testing:
        config_name = 'testing'
    else:
        config_name = os.getenv('FLASK_ENV', 'development')

    app.config['DATABASE'] = os.path.join(app.instance_path, 'open_trs.sqlite')
    app.config.from_object(CONFIGS[config_name])

    # Ensure instance folder exists; Flask does not automatically create it
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    open_trs.db.init_app(app)
    app.register_blueprint(open_trs.auth.bp)

    return app
