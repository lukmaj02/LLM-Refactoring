# === ARP Faza 4C - refactored code ===
# sample_id: requests_002
# condition: A
# timestamp: 2026-06-04T13:21:35
# original_cc: 12, original_mi: None
# changed_pct: 0.6949
# === END HEADER ===
def cert_verify(self, conn, url, verify, cert):
    """Verify a SSL certificate. This method should not be called from user
    code, and is only exposed for use when subclassing the
    :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

    :param conn: The urllib3 connection object associated with the cert.
    :param url: The requested URL.
    :param verify: Either a boolean, in which case it controls whether we verify
        the server's TLS certificate, or a string, in which case it must be a path
        to a CA bundle to use
    :param cert: The SSL certificate to verify.
    """
    if url.lower().startswith("https") and verify:
        conn.cert_reqs = "CERT_REQUIRED"
        if verify is not True:
            _set_ca_certificates(conn, verify)
    else:
        _disable_cert_verification(conn)

    if cert:
        _set_client_certificates(conn, cert)


def _set_ca_certificates(conn, cert_loc):
    if not os.path.exists(cert_loc):
        raise OSError(
            f"Could not find a suitable TLS CA certificate bundle, "
            f"invalid path: {cert_loc}"
        )

    if not os.path.isdir(cert_loc):
        conn.ca_certs = cert_loc
    else:
        conn.ca_cert_dir = cert_loc


def _disable_cert_verification(conn):
    conn.cert_reqs = "CERT_NONE"
    conn.ca_certs = None
    conn.ca_cert_dir = None


def _set_client_certificates(conn, cert):
    if not isinstance(cert, basestring):
        conn.cert_file = cert[0]
        conn.key_file = cert[1]
    else:
        conn.cert_file = cert
        conn.key_file = None

    if conn.cert_file and not os.path.exists(conn.cert_file):
        raise OSError(
            f"Could not find the TLS certificate file, "
            f"invalid path: {conn.cert_file}"
        )
    if conn.key_file and not os.path.exists(conn.key_file):
        raise OSError(
            f"Could not find the TLS key file, invalid path: {conn.key_file}"
        )