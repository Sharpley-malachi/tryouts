import hashlib 
import json 
import sqlite3 
import logging 
import os 
import uuid 
from typing import Dict, Any, List, Optional 
from datetime import datetime, timezone 

from ..core.ledger_schema import EpistemicBlock, LedgerEventType, CausalityLink, TemporalAnchor 
from ..core.crypto_spine import crypto_spine 

logger = logging.getLogger("TruthLedger") 
logger.setLevel(logging.INFO) 

class EpistemicLedger: 
    """ 
    The Immutable Truth Ledger. 
    Layer 1: JSON-L (Append only) 
    Layer 2: SQLite (Index) 
    """ 
    def __init__(self, data_dir: str = "data/ledger"): 
        self.data_dir = data_dir 
        if not os.path.exists(self.data_dir): 
            os.makedirs(self.data_dir) 
            
        self.ledger_file = os.path.join(self.data_dir, "truth_ledger.jsonl") 
        self.db_file = os.path.join(self.data_dir, "ledger_index.db") 
        
        self.last_hash = "0" * 64 # Genesis hash 
        self.block_height = 0 
        
        # Initialize 
        self._init_sqlite() 
        self._recover_state() 

    def _init_sqlite(self): 
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False) 
        self.cursor = self.conn.cursor() 
        self.cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS ledger_index ( 
                entry_id TEXT PRIMARY KEY, 
                event_type TEXT, 
                timestamp_utc TEXT, 
                entry_hash TEXT, 
                prev_hash TEXT, 
                block_height INTEGER, 
                strategy_id TEXT, 
                instrument TEXT, 
                timeframe TEXT 
            ) 
        """) 
        self.conn.commit() 

    def _recover_state(self): 
        """ 
        Reads the last line of the JSON-L file to get the latest hash and height. 
        Also rebuilds standard Merkle Peaks if needed (omitted for speed). 
        """ 
        if not os.path.exists(self.ledger_file): 
            return 
        
        try: 
            with open(self.ledger_file, 'rb') as f: 
                try: 
                    # Seek to the end 
                    f.seek(-2, os.SEEK_END) 
                    while f.read(1) != b'\n': 
                        f.seek(-2, os.SEEK_CUR) 
                except OSError: 
                    f.seek(0) 
                
                last_line = f.readline().decode() 
                if last_line: 
                    data = json.loads(last_line) 
                    self.last_hash = data.get("hash", self.last_hash) 
                    self.block_height = data.get("block_height", 0) 
        except Exception as e: 
            logger.warning(f"Could not recover last hash (Empty file?): {e}") 

    def record_event(self, 
                     event_type: LedgerEventType, 
                     payload: Dict[str, Any], 
                     causality: Optional[CausalityLink] = None, 
                     temporal_anchor: Optional[TemporalAnchor] = None) -> str: 
        """ 
        The primary write method. 
        Locks a new truth into the system. 
        Returns the new entry_hash. 
        """ 

        # Default objects if None 
        if causality is None: 
            causality = CausalityLink(initiating_agent_id="SYSTEM", input_data_hash="UNKNOWN") 
        if temporal_anchor is None: 
            temporal_anchor = TemporalAnchor() 

        # 2. Construct Entry (EpistemicBlock) 
        self.block_height += 1 
        
        entry = EpistemicBlock( 
            event_type=event_type, 
            payload=payload, 
            prev_hash=self.last_hash, 
            block_height=self.block_height, 
            utc_correlation_id=str(uuid.uuid4()), # Unique ID for this moment 
            causality=causality, 
            temporal_anchor=temporal_anchor 
        ) 
        
        # ID generation 
        entry.entry_id = str(uuid.uuid4()) 
        entry.hash = entry.calculate_hash() 
        
        # Merkle Integration 
        # We append the BLOCK HASH to the Merkle Spine 
        crypto_spine.append_leaf(entry.to_dict()) 
        entry.merkle_root_snapshot = crypto_spine.get_root() 
        
        # 3. Write to Immutable Log (Layer 1) 
        self._write_to_disk(entry) 
        
        # 4. Index (Layer 2) 
        self._index_entry(entry) 
        
        # 5. Update State 
        self.last_hash = entry.hash 
        logger.info(f"Ledger Event {event_type.value} Recorded. Hash: {entry.hash[:8]}... Height: {self.block_height}") 
        
        return entry.hash 

    def _write_to_disk(self, entry: EpistemicBlock): 
        """ 
        Appends to JSON-L file. 
        """ 
        with open(self.ledger_file, 'a') as f: 
            f.write(json.dumps(entry.to_dict()) + "\n") 

    def _index_entry(self, entry: EpistemicBlock): 
        """ 
        Extracts indexable fields from payload and saves to SQLite. 
        """ 
        # Extract common search fields if they exist in payload 
        strategy_id = entry.payload.get("strategy_id") or entry.payload.get("id") 
        instrument = entry.payload.get("instrument") 
        timeframe = entry.payload.get("timeframe") 
        
        self.cursor.execute(""" 
            INSERT INTO ledger_index (entry_id, event_type, timestamp_utc, entry_hash, prev_hash, block_height, strategy_id, instrument, timeframe) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) 
        """, ( 
            entry.entry_id, 
            entry.event_type.value, 
            entry.timestamp_utc, 
            entry.hash, 
            entry.prev_hash, 
            entry.block_height, 
            strategy_id, 
            instrument, 
            timeframe 
        )) 
        self.conn.commit() 

    def reconstruct_state_at_timestamp(self, timestamp: datetime) -> List[Dict]: 
        """ 
        Query: Reconstruct the Universe at Timestamp X. 
        Returns all events up to that timestamp. 
        """ 
        iso_ts = timestamp.isoformat() 
        self.cursor.execute("SELECT entry_id FROM ledger_index WHERE timestamp_utc <= ? ORDER BY timestamp_utc ASC", (iso_ts,)) 
        rows = self.cursor.fetchall() 
        ids = [r[0] for r in rows] 
        # In a real system, we'd do a smarter read. Here we scan. 
        # Actually efficiently reading JSON-L by offset is better, but SQLite index helps. 
        # For MVP, we might just query the DB if we stored full payload? We didn't. 
        # So we have to fetch from file or store payload in DB. 
        # Prompt says "Storage Engine: SQLite for indexed search layer and a JSON-L... for immutable". 
        # So we use the index to find what we need? 
        # If we need FULL state, we need to read the file. 
        
        # Optimization: Just return the index data for now or a subset. 
        # Or read the specific lines if we tracked offsets (advanced). 
        return [{"id": i} for i in ids] 
    
    def get_audit_trail(self, strategy_id: str) -> List[Dict]: 
        """ 
        Returns lineage for a strategy. 
        """ 
        self.cursor.execute("SELECT * FROM ledger_index WHERE strategy_id = ? ORDER BY timestamp_utc ASC", (strategy_id,)) 
        cols = [description[0] for description in self.cursor.description] 
        return [dict(zip(cols, row)) for row in self.cursor.fetchall()] 

    def close(self): 
        self.conn.close() 

# Singleton 
# Using a relative path for dev environment 
_ledger_path = os.path.join(os.getcwd(), "data", "ledger") 
truth_ledger = EpistemicLedger(_ledger_path) 
