from app.services.ai_strategy_engine.core.crypto_spine import MerkleMountainRange, crypto_spine


def test_merkle_root_changes_on_append():
    mmr = MerkleMountainRange()
    root_empty = mmr.get_root()

    mmr.append_leaf({"a": 1})
    root_one = mmr.get_root()
    assert isinstance(root_one, str)
    assert root_one != root_empty

    mmr.append_leaf({"b": 2})
    root_two = mmr.get_root()
    assert root_two != root_one


def test_generate_proof_contains_root_and_index():
    mmr = MerkleMountainRange()
    mmr.append_leaf({"x": 1})
    proof = mmr.generate_proof(0)
    assert "root" in proof
    assert "leaf_index" in proof
    assert proof["leaf_index"] == 0


def test_crypto_spine_singleton():
    # crypto_spine is a module-level instance; ensure methods callable
    crypto_spine.append_leaf({"t": "singleton"})
    root = crypto_spine.get_root()
    assert isinstance(root, str)
