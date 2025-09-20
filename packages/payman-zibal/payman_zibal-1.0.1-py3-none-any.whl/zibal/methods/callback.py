from payman.utils import to_model_instance

from ..models import CallbackParams, VerifyResponse


class Callback:
    async def callback_verify(
        self: "Zibal",
        callback: CallbackParams | dict | None = None,
        **kwargs,
    ) -> VerifyResponse:
        """Verify Zibal's server-to-server callback for lazy payment verification.

        Confirms the payment result after Zibal sends a callback to your server,
        typically used in delayed verification scenarios.

        Args:
            callback: Payload received from Zibal's callback request. Can be:
                - `CallbackParams` (Pydantic model)
                - `dict`
                - `None` → raises error
            **kwargs: Extra arguments passed to `to_model_instance`.

        Returns:
            VerifyResponse: Parsed transaction verification result.
        """

        parsed = to_model_instance(callback, CallbackParams, **kwargs)
        response = await self.client.post(
            endpoint="/callback/verify",
            payload=parsed.model_dump(by_alias=True, mode="json"),
        )
        return VerifyResponse(**response)
