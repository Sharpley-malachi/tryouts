import tempfile
from unittest.mock import MagicMock

from app.services.ai_price_action.service import PriceActionService


def test_fetch_all_data_monkeypatched(monkeypatch):
    svc = PriceActionService()

    # Monkeypatch the fetcher to avoid network calls
    svc.fetcher.fetch_automated_data = MagicMock(return_value={"EURUSD": {}})
    svc.fetcher.save_to_local_storage = MagicMock(return_value=1)

    res = svc.fetch_all_data()
    assert isinstance(res, dict)
    assert res.get("status") == "success"
    assert "assets_updated" in res
