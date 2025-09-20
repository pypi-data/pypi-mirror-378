from typing import Literal

from pydantic import BaseModel, ConfigDict, HttpUrl, Field
from pydantic.alias_generators import to_camel

from .multiplexing_info import MultiplexingInfo
from .types import AmountType, MobileStr, CardNumberStr, NationalCodeStr, OrderIdStr


class PaymentRequest(BaseModel):
    amount: AmountType = Field(..., description="Amount in Rial, minimum 100")
    callback_url: HttpUrl = Field(..., description="Merchant callback URL")
    description: str | None = Field(None, description="Payment description")
    order_id: OrderIdStr | None = Field(None, description="Merchant order ID")
    mobile: MobileStr | None = Field(None, description="Customer mobile number")
    allowed_cards: list[CardNumberStr] | None = Field(
        None, description="Allowed card numbers"
    )
    ledger_id: str | None = Field(None, description="Ledger identifier")
    national_code: NationalCodeStr | None = Field(
        None, description="Customer national code"
    )
    check_mobile_with_card: bool | None = Field(
        None, description="Enable card-mobile matching"
    )
    percent_mode: Literal[0, 1] = Field(0, description="0=Amount mode, 1=Percent mode")
    fee_mode: Literal[0, 1, 2] = Field(0, description="Fee payer mode")
    multiplexing_infos: list[MultiplexingInfo] = Field(default_factory=list)

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )
