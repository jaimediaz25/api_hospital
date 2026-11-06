import pytest

@pytest.fixture
def client(monkeypatch):
    import app as app_module
    # Evita iniciar el scheduler de respaldos durante las pruebas.
    monkeypatch.setattr(app_module, "init_scheduler", lambda flask_app: None)
    flask_app = app_module.create_app()
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as test_client:
        yield test_client
