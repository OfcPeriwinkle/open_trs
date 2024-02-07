from flask.testing import FlaskClient

import open_trs
import open_trs.configs


def test_config():
    normal_app = open_trs.create_app()
    assert not normal_app.testing

    testing_app = open_trs.create_app(testing=True)
    assert testing_app.testing
    assert testing_app.config['DATABASE'] == open_trs.configs.TestingConfig.DATABASE


def test_hello(client: FlaskClient):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'
