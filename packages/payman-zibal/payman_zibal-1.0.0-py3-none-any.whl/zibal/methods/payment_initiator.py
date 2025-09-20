from payman.utils import to_model_instance

from ..models import PaymentRequest, PaymentResponse


class PaymentInitiator:
    async def initiate_payment(
        self: "Zibal",
        params: PaymentRequest | dict | None = None,
        **kwargs,
    ) -> PaymentResponse:
        """Initiate a new payment.

        Args:
            params: Payment details (`amount`, `callback_url`, optional `mobile`).
                Can be a model, dict, or keyword arguments.

        Returns:
            PaymentResponse with result code and track ID.
        """

        parsed = to_model_instance(params, PaymentRequest, **kwargs)
        response = await self.client.post(
            "/request", parsed.model_dump(by_alias=True, mode="json")
        )
        return PaymentResponse(**response)
