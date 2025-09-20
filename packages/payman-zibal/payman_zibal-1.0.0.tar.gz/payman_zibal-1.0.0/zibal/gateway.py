from typing import ClassVar

from payman.core.http.client import AsyncHttpClient
from payman.interfaces.gateway_base import GatewayInterface

from .adapters.http_client import ZibalClient
from .adapters.error_mapper import zibal_error_mapper
from .methods import Methods
from .models import PaymentRequest, PaymentResponse


class Zibal(Methods, GatewayInterface[PaymentRequest, PaymentResponse]):
    """Zibal payment gateway client for initiating, verifying, and inquiring payments.

    API Reference: https://help.zibal.ir/IPG/API/
    """

    BASE_URL: ClassVar[str] = "https://gateway.zibal.ir"

    def __init__(
        self,
        merchant_id: str,
        version: int = 1,
        http_client: AsyncHttpClient = None,
        **client_options,
    ):
        """Initialize Zibal client.

        Args:
            merchant_id: Merchant ID provided by Zibal.
            version: API version (default: 1).
            client_options: Options for internal HTTP client, e.g.,
                timeout, max_retries, retry_delay, logging options, default_headers.

        Raises:
            ValueError: If `merchant_id` is empty or invalid.
        """

        if not isinstance(merchant_id, str) or not merchant_id:
            raise ValueError("`merchant_id` must be a non-empty string")

        self.merchant_id = merchant_id
        self.base_url = f"{self.BASE_URL}/v{version}"
        self.error_handler = zibal_error_mapper

        if http_client is None:
            http_client = AsyncHttpClient(base_url=self.base_url, **client_options)

        self.client = ZibalClient(
            merchant_id=self.merchant_id,
            base_url=self.base_url,
            http_client=http_client,
            error_mapper=self.error_handler,
        )

    def __repr__(self) -> str:
        return f"<Zibal merchant_id={self.merchant_id!r} base_url={self.base_url!r}>"
