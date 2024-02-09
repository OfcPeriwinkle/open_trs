import os

from flask import Flask, jsonify

import open_trs.auth
import open_trs.configs
import open_trs.db
import open_trs.projects


CONFIGS = {
    'development': open_trs.configs.DevelopmentConfig,
    'testing': open_trs.configs.TestingConfig,
    'production': open_trs.configs.ProductionConfig,
    'ci': open_trs.configs.GitHubActionsConfig
}


class InvalidUsage(Exception):
    """
    Exception raised for invalid usage of an endpoint.
    """

    def __init__(self, message, status_code=None, payload=None):
        """
        Initialize a new InvalidUsage exception.

        Args:
            message (str): The message associated with the instance.
            status_code (int, optional): The status code associated with the instance; defaults to None.
            payload (dict, optional): The payload associated with the instance; defaults to None.
        """
        super().__init__()

        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """
        Convert the exception to a dictionary representation.

        Returns:
            A dictionary containing the exception details.
        """

        return {
            'message': self.message,
            'payload': self.payload,
        }


def handle_invalid_usage(exception: InvalidUsage):
    """
    Handle an InvalidUsage exception.

    Args:
        exception: The InvalidUsage exception to handle.

    Returns:
        A JSON response containing the exception details and status code.
    """

    return jsonify(exception.to_dict()), exception.status_code


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

    # Register CLI commands and tear down functions
    open_trs.db.init_app(app)

    # Register API blueprints
    app.register_blueprint(open_trs.auth.bp)
    app.register_blueprint(open_trs.projects.bp)

    # Register error handlers
    app.register_error_handler(InvalidUsage, handle_invalid_usage)

    return app
