def test_record_count_reconciliation_equation():
    source_count, staged_count, rejected_count = 25, 23, 2
    unexplained_count = source_count - staged_count - rejected_count
    assert unexplained_count == 0

