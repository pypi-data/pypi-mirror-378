from payman.core.http.client import AsyncHttpClient

from .error_mapper import zibal_error_mapper


class ZibalClient:
    """Zibal-specific HTTP client wrapper.

    Handles merchant identification and centralized error mapping
    via `ErrorMapper`.
    """

    def __init__(
        self,
        merchant_id: str,
        base_url: str,
        http_client: AsyncHttpClient,
        error_mapper=zibal_error_mapper,
    ) -> None:
        """Initialize Zibal API client.

        Args:
            merchant_id: Merchant identifier for requests.
            base_url: Base URL of Zibal API.
            http_client: Generic async HTTP client instance.
            error_mapper: Maps response codes to exceptions.
        """

        self.merchant_id = merchant_id
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client
        self.error_mapper = error_mapper

    async def post(self, endpoint: str, payload: dict) -> dict:
        """Send a POST request to Zibal API with merchant info injected.

        Args:
            endpoint: API path (appended to base_url).
            payload: Request payload.

        Returns:
            Parsed JSON response.

        Raises:
            Exception: If Zibal error code is returned (mapped via ErrorMapper).
        """

        payload = {"merchant": self.merchant_id, **payload}
        path = f"{self.base_url}{endpoint}"

        response = await self.http_client.request(
            method="POST",
            endpoint=path,
            json_data=payload,
        )

        self.error_mapper.map(response)
        return response
