from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel

from .multiplexing_info import MultiplexingInfo
from ..enums.transaction_status import TransactionStatus
from ..enums.result_code import ResultCode
from .types import PositiveAmountType, TrackIdType


class VerifyResponse(BaseModel):
    result: ResultCode = Field(..., description="Gateway response status code")
    message: str = Field(..., description="Result message")
    amount: PositiveAmountType | None = Field(None, description="Paid amount in Rial")
    status: TransactionStatus | None = Field(
        None, description="Bank transaction status"
    )
    paid_at: str | None = Field(
        None, description="Payment timestamp in ISO 8601 format"
    )
    card_number: str | None = Field(
        None, description="Masked card number used for payment"
    )
    ref_number: str | None = Field(None, description="Bank reference number")
    order_id: str | None = Field(None, description="Merchant order ID")
    description: str | None = Field(None, description="Optional description")
    track_id: TrackIdType | None = Field(
        None, description="Zibal transaction tracking ID"
    )
    multiplexing_infos: list[MultiplexingInfo] = Field(default_factory=list)

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        use_enum_values=True,
    )

    @property
    def success(self) -> bool:
        return self.result == ResultCode.SUCCESS

    @property
    def already_verified(self) -> bool:
        return self.status == TransactionStatus.VERIFIED
