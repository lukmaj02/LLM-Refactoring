# === ARP Faza 4C - refactored code ===
# sample_id: requests_001
# condition: G
# timestamp: 2026-06-04T13:21:10
# original_cc: 19, original_mi: None
# changed_pct: 0.6916
# === END HEADER ===
def _prepare_timeout(self, timeout):
    """Prepares the timeout object for urllib3's urlopen call."""
    if isinstance(timeout, tuple):
        try:
            connect, read = timeout
            return TimeoutSauce(connect=connect, read=read)
        except ValueError:
            raise ValueError(
                f"Invalid timeout {timeout}. Pass a (connect, read) timeout tuple, "
                f"or a single float to set both timeouts to the same value."
            )
    elif isinstance(timeout, TimeoutSauce):
        return timeout
    else:
        return TimeoutSauce(connect=timeout, read=timeout)

def _handle_max_retry_error(self, e, request):
    """Handles MaxRetryError and raises appropriate Requests exceptions."""
    if isinstance(e.reason, ConnectTimeoutError):
        # TODO: Remove this in 3.0.0: see #2811
        if not isinstance(e.reason, NewConnectionError):
            raise ConnectTimeout(e, request=request)

    if isinstance(e.reason, ResponseError):
        raise RetryError(e, request=request)

    if isinstance(e.reason, _ProxyError):
        raise ProxyError(e, request=request)

    if isinstance(e.reason, _SSLError):
        # This branch is for urllib3 v1.22 and later.
        raise SSLError(e, request=request)

    raise ConnectionError(e, request=request)

def _handle_urllib3_http_error(self, e, request):
    """Handles various urllib3 HTTP errors and raises appropriate Requests exceptions."""
    if isinstance(e, _SSLError):
        # This branch is for urllib3 versions earlier than v1.22
        raise SSLError(e, request=request)
    elif isinstance(e, ReadTimeoutError):
        raise ReadTimeout(e, request=request)
    elif isinstance(e, _InvalidHeader):
        raise InvalidHeader(e, request=request)
    else:
        raise

def _send_and_raise_requests_exceptions(self, conn, request, url, chunked, timeout):
    """Performs the actual urlopen call and translates urllib3 exceptions to Requests exceptions."""
    try:
        resp = conn.urlopen(
            method=request.method,
            url=url,
            body=request.body,
            headers=request.headers,
            redirect=False,
            assert_same_host=False,
            preload_content=False,
            decode_content=False,
            retries=self.max_retries,
            timeout=timeout,
            chunked=chunked,
        )
        return resp
    except (ProtocolError, OSError) as err:
        raise ConnectionError(err, request=request)
    except MaxRetryError as e:
        self._handle_max_retry_error(e, request)
    except ClosedPoolError as e:
        raise ConnectionError(e, request=request)
    except _ProxyError as e:
        raise ProxyError(e)
    except (_SSLError, _HTTPError) as e:
        self._handle_urllib3_http_error(e, request