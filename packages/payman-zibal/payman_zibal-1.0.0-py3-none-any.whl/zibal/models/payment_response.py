from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel

from ..enums.result_code import ResultCode


class PaymentResponse(BaseModel):
    result: ResultCode = Field(..., description="Payment status code")
    track_id: int = Field(..., description="Unique payment session ID")
    message: str = Field(..., description="Result message")

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True,
        alias_generator=to_camel,
    )

    @property
    def success(self) -> bool:
        return self.result == ResultCode.SUCCESS
