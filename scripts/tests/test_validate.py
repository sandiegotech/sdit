import validate


def test_real_catalog_passes():
    # The committed catalog must always satisfy the validator (regression guard).
    assert validate.main() == 0
