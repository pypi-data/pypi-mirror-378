from .callback import Callback
from .redirector import PaymentRedirector
from .payment_inquiry import PaymentInquiry
from .lazy_payment import LazyPayment
from .payment_initiator import PaymentInitiator
from .verify_payment import VerifyPayment


class Methods(
    Callback,
    PaymentRedirector,
    PaymentInquiry,
    LazyPayment,
    PaymentInitiator,
    VerifyPayment,
):
    pass
