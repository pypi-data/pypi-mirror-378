from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel

from payman.interfaces.callback import CallbackBase

from ..enums.transaction_status import TransactionStatus


class CallbackParams(BaseModel, CallbackBase):
    track_id: int = Field(..., description="Transaction ID from callback")
    success: int = Field(..., description="1 = success, 0 = failure")
    order_id: str = Field(..., description="Merchant order ID")
    status: TransactionStatus = Field(..., description="Transaction status code")

    @property
    def is_success(self) -> bool:
        return self.success == TransactionStatus.VERIFIED

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        use_enum_values=True,
    )
