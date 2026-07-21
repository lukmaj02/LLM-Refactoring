# === ARP Faza 4C - refactored code ===
# sample_id: flask_001
# condition: C
# timestamp: 2026-06-04T14:10:21
# original_cc: 16, original_mi: None
# changed_pct: 0.5172
# === END HEADER ===
def _unpack_response_tuple(rv):
    """Unpack a tuple return value into (body, status, headers)."""
    status = None
    headers = None
    len_rv = len(rv)

    if len_rv == 3:
        rv, status, headers = rv  # type: ignore[misc]
    elif len_rv == 2:
        if isinstance(rv[1], (Headers, dict, tuple, list)):
            rv, headers = rv  # pyright: ignore
        else:
            rv, status = rv  # type: ignore[assignment,misc]
    else:
        raise TypeError(
            "The view function did not return a valid response tuple."
            " The tuple must have the form (body, status, headers),"
            " (body, status), or (body, headers)."
        )

    return rv, status, headers


def _apply_response_status_and_headers(rv, status, headers):
    """Apply status and headers to a response object."""
    rv = t.cast(Response, rv)

    if status is not None:
        if isinstance(status, (str, bytes, bytearray)):
            rv.status = status
        else:
            rv.status_code = status

    if headers:
        rv.headers.update(headers)

    return rv


def make_response(self, rv: ft.ResponseReturnValue) -> Response:
    """Convert the return value from a view function to an instance of
    :attr:`response_class`.

    :param rv: the return value from the view function. The view function
        must return a response. Returning ``None``, or the view ending
        without returning, is not allowed. The following types are allowed
        for ``view_rv``:

        ``str``
            A response object is created with the string encoded to UTF-8
            as the body.

        ``bytes``
            A response object is created with the bytes as the body.

        ``dict``
            A dictionary that will be jsonify'd before being returned.

        ``list``
            A list that will be jsonify'd before being returned.

        ``generator`` or ``iterator``
            A generator that returns ``str`` or ``bytes`` to be
            streamed as the response.

        ``tuple``
            Either ``(body, status, headers)``, ``(body, status)``, or
            ``(body, headers)``, where ``body`` is any of the other types
            allowed here, ``status`` is a string or an integer, and
            ``headers`` is a dictionary or a list of ``(key, value)``
            tuples. If ``body`` is a :attr:`response_class` instance,
            ``status`` overwrites the exiting value and ``headers`` are
            extended.

        :attr:`response_class`
            The object is returned unchanged.

        other :class:`~werkzeug.wrappers.Response` class
            The object is coerced to :attr:`response_class`.

        :func:`callable`
            The function is called as a WSGI application. The result is
            used to create a response object.

    .. versionchanged:: 2.2
        A generator will be converted to a streaming response.
        A list will be converted to a JSON response.

    .. versionchanged:: 1.1
        A dict will be converted to a JSON response.

    .. versionchanged:: 0.9
       Previously a tuple was interpreted as the arguments for the
       response object.
    """
    status = None
    headers = None

    if isinstance(rv, tuple):
        rv, status, headers = _unpack_response_tuple(rv)

    if rv is None:
        raise TypeError(
            f"The view function for {request.endpoint!r} did not"
            " return a valid response. The function either returned"
            " None or ended without a return statement."
        )

    if isinstance(rv, self.response_class):
        return _apply_response_status_and_headers(rv, status, headers)

    if isinstance(rv, (str, bytes, bytearray)) or isinstance(rv, cabc.Iterator):
        rv = self.response_class(
            rv,  # pyright: ignore
            status=status,
            headers=headers,  # type: ignore[arg-type]
        )
        return t.cast(Response, rv)

    if isinstance(rv, (dict, list)):
        rv = self.json.response(rv)
    elif isinstance(rv, BaseResponse) or callable(rv):
        try:
            rv = self.response_class.force_type(
                rv,  # type: ignore[arg-type]
                request.environ,
            )
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

    return _apply_response_status_and_headers(rv, status, headers)