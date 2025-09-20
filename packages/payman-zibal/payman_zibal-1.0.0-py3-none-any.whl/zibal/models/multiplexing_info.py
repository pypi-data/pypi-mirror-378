from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel

from .types import PositiveAmountType


class MultiplexingInfo(BaseModel):
    amount: PositiveAmountType = Field(..., description="Amount to split")
    bank_account: str | None = Field(None, description="Target bank account")
    sub_merchant_id: str | None = Field(None, description="Sub-merchant identifier")
    wallet_id: str | None = Field(None, description="Wallet identifier")
    wage_payer: bool | None = Field(
        None, description="If True, wage is paid by this target"
    )

    @model_validator(mode="after")
    def at_least_one_target(cls, values):
        if not any([values.bank_account, values.sub_merchant_id, values.wallet_id]):
            raise ValueError(
                "At least one of 'bank_account', 'sub_merchant_id', or 'wallet_id' must be provided."
            )
        return values

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )
