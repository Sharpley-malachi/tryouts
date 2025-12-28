import tempfile
import os
from datetime import datetime

from app.services.ai_data_pipeline.agent import DataPipelineAgent
from app.services.ai_data_pipeline.storage import UnifiedStorage


def test_agent_ingest_writes_files():
    tmpdir = tempfile.mkdtemp()
    agent = DataPipelineAgent()
    # Inject test storage root
    agent.storage = UnifiedStorage(root_dir=tmpdir)

    payload = {
        'correlation_id': 'TEST-INGEST',
        'data': {
            '4H': [
                {'time': '2025-12-20T00:00:00Z', 'open': '100', 'high': '110', 'low': '90', 'close': '105'}
            ]
        },
        'metadata': {'symbol': 'TEST', 'filename': 'test.csv', 'timeframe': '4H'}
    }

    res = agent.ingest_market_data(payload['correlation_id'], payload['data'], payload['metadata'])
    assert res['status'] == 'SUCCESS'

    # Check bronze and silver files exist
    bronze_dir = os.path.join(tmpdir, 'bronze')
    silver_dir = os.path.join(tmpdir, 'silver')
    assert os.path.isdir(bronze_dir)
    assert os.path.isdir(silver_dir)
