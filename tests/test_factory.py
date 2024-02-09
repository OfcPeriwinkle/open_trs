import pytest

import open_trs
import open_trs.configs


def test_config(monkeypatch: pytest.MonkeyPatch):
    testing_app = open_trs.create_app(testing=True)
    assert testing_app.testing
    assert testing_app.config['DATABASE'] == open_trs.configs.TestingConfig.DATABASE

    monkeypatch.setenv('FLASK_ENV', 'development')
    normal_app = open_trs.create_app()
    assert not normal_app.testing
