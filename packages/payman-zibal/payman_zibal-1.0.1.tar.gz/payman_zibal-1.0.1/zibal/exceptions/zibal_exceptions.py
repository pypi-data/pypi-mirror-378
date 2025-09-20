from payman.core.exceptions.base import GatewayError


class ZibalGatewayError(GatewayError):
    """Base class for all Zibal errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class MerchantNotFoundError(ZibalGatewayError):
    """Merchant not found."""

    pass


class MerchantInactiveError(ZibalGatewayError):
    """Merchant is inactive."""

    pass


class InvalidMerchantError(ZibalGatewayError):
    """Invalid merchant."""

    pass


class AmountTooLowError(ZibalGatewayError):
    """Amount must be greater than 1,000 IRR."""

    pass


class InvalidCallbackUrlError(ZibalGatewayError):
    """Invalid callback URL."""

    pass


class AmountExceedsLimitError(ZibalGatewayError):
    """Transaction amount exceeds the limit."""

    pass


class InvalidNationalCodeError(ZibalGatewayError):
    """Invalid national code."""

    pass


class InvalidPercentModeError(ZibalGatewayError):
    """Invalid percentMode value (only 0 or 1 allowed)."""

    pass


class InvalidMultiplexingBeneficiariesError(ZibalGatewayError):
    """One or more multiplexing beneficiaries are invalid."""

    pass


class InactiveMultiplexingBeneficiaryError(ZibalGatewayError):
    """One or more multiplexing beneficiaries are inactive."""

    pass


class MissingSelfBeneficiaryError(ZibalGatewayError):
    """'self' beneficiary ID not included in multiplexingInfos."""

    pass


class AmountMismatchInMultiplexingError(ZibalGatewayError):
    """Total amount does not match the sum of shares in multiplexingInfos."""

    pass


class InsufficientWalletBalanceForFeesError(ZibalGatewayError):
    """Insufficient wallet balance for fee deduction."""

    pass


class AlreadyConfirmedError(ZibalGatewayError):
    """Already confirmed."""

    pass


class PaymentNotSuccessfulError(ZibalGatewayError):
    """Payment order is not successful or unpaid."""

    pass


class InvalidTrackIdError(ZibalGatewayError):
    """Invalid track ID."""

    pass


ZIBAL_ERRORS = {
    102: MerchantNotFoundError,
    103: MerchantInactiveError,
    104: InvalidMerchantError,
    105: AmountTooLowError,
    106: InvalidCallbackUrlError,
    107: InvalidPercentModeError,
    108: InvalidMultiplexingBeneficiariesError,
    109: InactiveMultiplexingBeneficiaryError,
    110: MissingSelfBeneficiaryError,
    111: AmountMismatchInMultiplexingError,
    112: InsufficientWalletBalanceForFeesError,
    113: AmountExceedsLimitError,
    114: InvalidNationalCodeError,
    201: AlreadyConfirmedError,
    202: PaymentNotSuccessfulError,
    203: InvalidTrackIdError,
}
