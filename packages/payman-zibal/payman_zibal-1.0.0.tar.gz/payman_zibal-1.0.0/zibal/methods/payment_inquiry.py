from payman.utils import to_model_instance

from ..models import InquiryRequest, InquiryResponse


class PaymentInquiry:
    async def inquiry(
        self: "Zibal",
        params: InquiryRequest | dict | None = None,
        **kwargs,
    ) -> InquiryResponse:
        """Check the latest status of a transaction.

        Args:
            params: Input with `track_id` or `order_id`. Can be a Pydantic
                model, a dict, or keyword arguments.

        Returns:
            Transaction status details.
        """

        parsed = to_model_instance(params, InquiryRequest, **kwargs)
        response = await self.client.post(
            "/inquiry", parsed.model_dump(by_alias=True, mode="json")
        )
        return InquiryResponse(**response)
