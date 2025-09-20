from payman.utils import to_model_instance

from ..models import VerifyRequest, VerifyResponse


class VerifyPayment:
    async def verify_payment(
        self: "Zibal",
        params: VerifyRequest | dict | None = None,
        **kwargs,
    ) -> VerifyResponse:
        """Verify a completed payment.

        Args:
            params: Verification input (usually `track_id`).
                Can be a model, dict, or keyword arguments.

        Returns:
            VerifyResponse with transaction details.
        """

        parsed = to_model_instance(params, VerifyRequest, **kwargs)
        response = await self.client.post(
            "/verify", parsed.model_dump(by_alias=True, mode="json")
        )
        return VerifyResponse(**response)
