from enum import IntEnum


class TransactionStatus(IntEnum):
    """Transaction status codes returned by Zibal."""

    VERIFIED = 1
    PAID_NOT_VERIFIED = 2
    CANCELED_BY_USER = 3
    INVALID_CARD_NUMBER = 4
    INSUFFICIENT_FUNDS = 5
    WRONG_PASSWORD = 6
    TOO_MANY_REQUESTS = 7
    DAILY_LIMIT_COUNT_EXCEEDED = 8
    DAILY_LIMIT_AMOUNT_EXCEEDED = 9
    INVALID_CARD_ISSUER = 10
    SWITCH_ERROR = 11
    CARD_NOT_ACCESSIBLE = 12
    REFUNDED = 15
    REFUNDING = 16
    REVERSED = 18
