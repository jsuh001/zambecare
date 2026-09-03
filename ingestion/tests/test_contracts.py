from zambecare_ingestion.contracts import canonical_json, checksum


def test_checksum_is_stable_across_key_order():
    assert checksum({"b": 2, "a": 1}) == checksum({"a": 1, "b": 2})
    assert canonical_json({"b": 2, "a": 1}) == '{"a":1,"b":2}'

