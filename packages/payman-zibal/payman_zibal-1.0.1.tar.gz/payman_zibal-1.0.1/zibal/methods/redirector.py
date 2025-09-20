class PaymentRedirector:
    def get_payment_redirect_url(self: "Zibal", track_id: int) -> str:
        """Build the redirect URL for sending the user to Zibal's gateway.

        Args:
            track_id: Unique track ID from a successful `payment()` or `lazy_payment()` call.

        Returns:
            Full URL to redirect the user for payment.
        """

        return f"{self.BASE_URL}/start/{track_id}"
