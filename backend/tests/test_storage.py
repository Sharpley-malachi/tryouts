import tempfile
import os
from datetime import datetime

from app.services.ai_data_pipeline.storage import UnifiedStorage
from app.services.ai_data_pipeline.core.types import MarketCandle


def test_save_and_query_feature_store(tmp_path=None):
    # Use a tempdir
    tmpdir = str(tempfile.mkdtemp())
    storage = UnifiedStorage(root_dir=tmpdir)

    # Create a sample MarketCandle dataclass instance
    ts = datetime.fromisoformat("2025-12-20T00:00:00+00:00")
    candle = MarketCandle(
        timestamp=ts,
        open=100.0,
        high=110.0,
        low=90.0,
        close=105.0,
        timeframe="4H",
        source_batch_id="TEST"
    )

    storage.save_feature("TEST", "4H", [candle])

    # Ensure silver file exists
    silver_path = os.path.join(tmpdir, "silver", "TEST_4H.json")
    assert os.path.exists(silver_path)

    # Query state at a later time (should return our candle)
    snapshot = storage.query_state_at_time("TEST", datetime.fromisoformat("2025-12-21T00:00:00+00:00"))
    assert "4H" in snapshot
    assert snapshot["4H"]["close"] == 105.0
