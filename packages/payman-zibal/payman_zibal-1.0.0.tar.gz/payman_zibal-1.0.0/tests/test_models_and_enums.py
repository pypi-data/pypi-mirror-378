import pytest
from pydantic import ValidationError

from zibal.models import PaymentRequest, MultiplexingInfo, VerifyResponse
from zibal.enums.transaction_status import TransactionStatus
from zibal.enums.result_code import ResultCode


def test_payment_request_validation():
    """Tests Pydantic validation for PaymentRequest model."""

    pr = PaymentRequest(
        amount=15000,
        callback_url="https://example.com/callback",
        mobile="09123456789",
        national_code="1234567890",
    )
    assert pr.amount == 15000

    with pytest.raises(ValidationError):
        PaymentRequest(amount=99, callback_url="https://example.com")

    with pytest.raises(ValidationError):
        PaymentRequest(
            amount=1000, callback_url="https://example.com", mobile="0987654"
        )


def test_multiplexing_info_validation():
    """Tests validation for MultiplexingInfo model."""

    mi = MultiplexingInfo(amount=1000, bank_account="123456789012345678901234")
    assert mi.amount == 1000

    with pytest.raises(
        ValueError,
        match="At least one of 'bank_account', 'sub_merchant_id', or 'wallet_id' must be provided.",
    ):
        MultiplexingInfo(amount=1000)


def test_verify_response_properties():
    """Tests the properties and logic within the VerifyResponse model."""

    response_data_success = {
        "result": ResultCode.SUCCESS,
        "message": "success",
        "status": TransactionStatus.VERIFIED,
    }
    response_success = VerifyResponse(**response_data_success)
    assert response_success.success is True
    assert response_success.already_verified is True

    response_data_fail = {
        "result": ResultCode.MERCHANT_NOT_FOUND,
        "message": "Payment not successful",
    }
    response_fail = VerifyResponse(**response_data_fail)
    assert response_fail.success is False

    invalid_response_data = {
        "result": 202,
        "message": "Payment not successful",
        "status": 0,
    }
    with pytest.raises(ValidationError):
        VerifyResponse(**invalid_response_data)
