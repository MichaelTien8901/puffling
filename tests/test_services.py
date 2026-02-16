from backend.services.settings_service import SettingsService
from backend.services.model_service import ModelService


def test_settings_service(db):
    svc = SettingsService(db)
    from backend.models.user import User
    db.add(User(id="default", name="Test"))
    db.commit()

    svc.set("default", "key1", "value1")
    assert svc.get("default", "key1") == "value1"

    all_settings = svc.get_all("default")
    assert "key1" in all_settings

    svc.delete("default", "key1")
    assert svc.get("default", "key1") is None


def test_model_service_list_types():
    svc = ModelService()
    types = svc.list_types()
    assert "ml" in types
    assert "xgboost" in types["ensembles"]
    assert "lstm" in types["deep"]
    assert "dqn" in types["rl"]
