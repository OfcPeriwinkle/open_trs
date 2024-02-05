import os

from flask import Flask

import open_trs.configs

app = Flask(__name__)

configs = {
    'development': open_trs.configs.DevelopmentConfig,
    'testing': open_trs.configs.TestingConfig,
    'production': open_trs.configs.ProductionConfig
}

config_name = os.getenv('FLASK_ENV', 'development')
app.config.from_object(configs[config_name])


@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)
