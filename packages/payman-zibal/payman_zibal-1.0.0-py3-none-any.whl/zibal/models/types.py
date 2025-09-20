from pydantic import conint, constr


AmountType = conint(ge=100)  # For PaymentRequest amount
PositiveAmountType = conint(gt=0)  # For Multiplexing & responses
TrackIdType = conint(gt=0)

MobileStr = constr(min_length=11, max_length=11, pattern=r"^09\d{9}$")

CardNumberStr = constr(min_length=16, max_length=16, pattern=r"^\d{16}$")

NationalCodeStr = constr(min_length=10, max_length=10, pattern=r"^\d{10}$")

LedgerIdStr = constr(min_length=1, max_length=64)

OrderIdStr = constr(min_length=1, max_length=128)
