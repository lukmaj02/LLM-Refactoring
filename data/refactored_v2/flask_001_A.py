# === ARP Faza 4C - refactored code ===
# sample_id: flask_001
# condition: A
# timestamp: 2026-06-04T13:16:45
# original_cc: 16, original_mi: None
# changed_pct: 0.8511
# === END HEADER ===
def make_response(self, rv: ft.ResponseReturnValue) -> Response:
    """Convert the return value from a view function to an instance of
    :attr:`response_class`.
    """
    status, headers = None, None

    if isinstance(rv, tuple):
        rv, status, headers = self._unpack_tuple(rv)

    if rv is None:
        raise TypeError(
            f"The view function for {request.endpoint!r} did not"
            " return a valid response. The function either returned"
            " None or ended without a return statement."
        )

    if not isinstance(rv, self.response_class):
        rv = self._convert_to_response(rv, status, headers)
        status = headers = None

    rv = t.cast(Response, rv)

    if status is not None:
        self._set_status(rv, status)

    if headers:
        rv.headers.update(headers)

    return rv


def _unpack_tuple(self, rv_tuple):
    len_rv = len(rv_tuple)
    if len_rv == 3:
        return rv_tuple  # type: ignore[misc]
    elif len_rv == 2:
        if isinstance(rv_tuple[1], (Headers, dict, tuple, list)):
            return rv_tuple[0], None, rv_tuple[1]  # pyright: ignore
        else:
            return rv_tuple[0], rv_tuple[1], None  # type: ignore[assignment,misc]
    else:
        raise TypeError(
            "The view function did not return a valid response tuple."
            " The tuple must have the form (body, status, headers),"
            " (body, status), or (body, headers)."
        )


def _convert_to_response(self, rv, status, headers):
    if isinstance(rv, (str, bytes, bytearray)) or isinstance(rv, cabc.Iterator):
        return self.response_class(rv, status=status, headers=headers)  # pyright: ignore
    elif isinstance(rv, (dict, list)):
        return self.json.response(rv)
    elif isinstance(rv, BaseResponse) or callable(rv):
        try:
            return self.response_class.force_type(rv, request.environ)  # type: ignore[arg-type]
        except TypeError as e:
            raise TypeError(
                f"{e}\nThe view function did not return a valid"
                " response. The return type must be a string,"
                " dict, list, tuple with headers or status,"
                " Response instance, or WSGI callable, but it"
                f" was a {type(rv).__name__}."
            ).with_traceback(sys.exc_info()[2]) from None
    else:
        raise TypeError(
            "The view function did not return a valid"
            " response. The return type must be a string,"
            " dict, list, tuple with headers or status,"
            " Response instance, or WSGI callable, but it was a"
            f" {type(rv).__name__}."
        )


def _set_status(self, rv, status):
    if isinstance(status, (str, bytes, bytearray)):
        rv.status = status
    else:
        rv.status_code = status