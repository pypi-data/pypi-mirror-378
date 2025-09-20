from ..exceptions.zibal_exceptions import ZIBAL_ERRORS, ZibalGatewayError


class ErrorMapper:
    def __init__(
        self, errors_map: dict[int, type[Exception]], base_exc: type[Exception]
    ):
        self.errors_map = errors_map
        self.base_exc = base_exc

    def map(self, response: dict) -> None:
        code = response.get("result")
        if code == 100:
            return  # Success

        exc_cls = self.errors_map.get(code, self.base_exc)
        raise exc_cls(response.get("message", f"Unknown error (code={code})"))


zibal_error_mapper = ErrorMapper(ZIBAL_ERRORS, ZibalGatewayError)
