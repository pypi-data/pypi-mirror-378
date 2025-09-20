import pytest

from zibal.gateway import Zibal


def test_zibal_initialization_with_valid_merchant_id():
    """Validates that a Zibal instance can be created with a valid merchant ID."""

    zibal = Zibal(merchant_id="1234567890")
    assert zibal.merchant_id == "1234567890"
    assert zibal.base_url == "https://gateway.zibal.ir/v1"
    assert "Zibal" in repr(zibal)


def test_zibal_initialization_with_invalid_merchant_id():
    """Checks for ValueError when initializing with an empty or invalid merchant ID."""

    with pytest.raises(ValueError, match="`merchant_id` must be a non-empty string"):
        Zibal(merchant_id="")
    with pytest.raises(ValueError, match="`merchant_id` must be a non-empty string"):
        Zibal(merchant_id=None)
