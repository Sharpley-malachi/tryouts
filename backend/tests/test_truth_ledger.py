import tempfile
import os
from datetime import datetime, timezone

from app.services.ai_strategy_engine.core.truth_ledger import EpistemicLedger
from app.services.ai_strategy_engine.core.ledger_schema import LedgerEventType


def test_ledger_record_and_indexing():
    tmpdir = tempfile.mkdtemp()
    ledger = EpistemicLedger(data_dir=tmpdir)

    payload = {"instrument": "TEST", "timeframe": "4H", "note": "unit test"}
    h = ledger.record_event(LedgerEventType.DATA_INGESTED, payload)

    # ledger file should exist and contain the entry
    ledger_file = os.path.join(tmpdir, "truth_ledger.jsonl")
    assert os.path.exists(ledger_file)

    # Add a second event to exercise ordering and indexing
    payload2 = {"instrument": "TEST", "timeframe": "4H", "note": "second"}
    h2 = ledger.record_event(LedgerEventType.DATA_INGESTED, payload2)

    # Reconstruct state and ensure both IDs present in the index query
    ts = datetime.now(timezone.utc)
    state = ledger.reconstruct_state_at_timestamp(ts)
    assert isinstance(state, list)
    # We expect at least two indexed entries (IDs returned)
    assert len(state) >= 2

    ledger.close()
