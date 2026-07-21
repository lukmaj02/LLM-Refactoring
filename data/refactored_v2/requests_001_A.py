# === ARP Faza 4C - refactored code ===
# sample_id: requests_001
# condition: A
# timestamp: 2026-06-04T13:20:58
# original_cc: 19, original_mi: None
# changed_pct: 0.4237
# === END HEADER ===
def send(
    self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None
):
    """Sends PreparedRequest object. Returns Response object.

    :param request: The :class:`PreparedRequest <PreparedRequest>` being sent.
    :param stream: (optional) Whether to stream the request content.
    :param timeout: (optional) How long to wait for the server to send
        data before giving up, as a float, or a :ref:`(connect timeout,
        read timeout) <timeouts>` tuple.
    :type timeout: float or tuple or urllib3 Timeout object
    :param verify: (optional) Either a boolean, in which case it controls whether
        we verify the server's TLS certificate, or a string, in which case it
        must be a path to a CA bundle to use
    :param cert: (optional) Any user-provided SSL certificate to be trusted.
    :param proxies: (optional) The proxies dictionary to apply to the request.
    :rtype: requests.Response
    """

    try:
        conn = self.get_connection_with_tls_context(
            request, verify, proxies=proxies, cert=cert
        )
    except LocationValueError as e:
        raise InvalidURL(e, request=request)

    self.cert_verify(conn, request.url, verify, cert)
    url = self.request_url(request, proxies)
    self.add_headers(
        request,
        stream=stream,
        timeout=timeout,
        verify=verify,
        cert=cert,
        proxies=proxies,
    )

    chunked = not (request.body is None or "Content-Length" in request.headers)
    timeout = self._get_timeout(timeout)

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

    except (ProtocolError, OSError) as err:
        raise ConnectionError(err, request=request)

    except MaxRetryError as e:
        self._handle_max_retry_error(e, request)

    except ClosedPoolError as e:
        raise ConnectionError(e, request=request)

    except _ProxyError as e:
        raise ProxyError(e)

    except (_SSLError, _HTTPError) as e:
        self._handle_ssl_http_error(e, request)

    return self.build_response(request, resp)


def _get_timeout(self, timeout):
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


def _handle_ssl_http_error(self, e, request):
    if isinstance(e, _SSLError):
        # This branch is for urllib3 versions earlier than v1.22
        raise SSLError(e, request=request)
    elif isinstance(e, ReadTimeoutError):
        raise ReadTimeout(e, request=request)
    elif isinstance(e, _InvalidHeader):
        raise InvalidHeader(e, request=request)
    else:
        raise