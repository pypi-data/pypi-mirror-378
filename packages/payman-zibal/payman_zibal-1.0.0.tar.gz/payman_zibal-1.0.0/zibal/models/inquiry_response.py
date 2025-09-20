from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel

from .multiplexing_info import MultiplexingInfo
from ..enums.result_code import ResultCode
from ..enums.transaction_status import TransactionStatus
from .types import PositiveAmountType


class InquiryResponse(BaseModel):
    result: ResultCode = Field(..., description="API status code")
    message: str = Field(..., description="Status message")
    ref_number: str | None = Field(None, description="Bank reference number")
    paid_at: str | None = Field(None, description="Payment timestamp (ISO 8601)")
    verified_at: str | None = Field(None, description="Verification timestamp")
    status: TransactionStatus | None = Field(None, description="Payment status")
    amount: PositiveAmountType | None = Field(None, description="Transaction amount")
    order_id: str = Field(..., description="Merchant order ID")
    description: str = Field(..., description="Description of the transaction")
    card_number: str | None = Field(None, description="Masked card number")
    wage: PositiveAmountType | None = Field(None, description="Transaction wage")
    created_at: str = Field(..., description="Response creation timestamp")
    multiplexing_infos: list[MultiplexingInfo] = Field(default_factory=list)

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        alias_generator=to_camel,
    )

    @property
    def success(self) -> bool:
        return self.result == ResultCode.SUCCESS

    @property
    def already_verified(self) -> bool:
        return self.status == TransactionStatus.VERIFIED
