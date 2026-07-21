# === ARP Faza 4C - refactored code ===
# sample_id: requests_002
# condition: G
# timestamp: 2026-06-04T13:21:30
# original_cc: 12, original_mi: None
# changed_pct: 0.9444
# === END HEADER ===
def _set_server_cert_options(self, conn, url, verify):
        """Sets server certificate verification options on the connection.

        :param conn: The urllib3 connection object.
        :param url: The requested URL.
        :param verify: Controls server TLS certificate verification.
        """
        if not url.lower().startswith("https") or not verify:
            conn.cert_reqs = "CERT_NONE"
            conn.ca_certs = None
            conn.ca_cert_dir = None
            return

        conn.cert_reqs = "CERT_REQUIRED"
        # Only load the CA certificates if 'verify' is a string indicating the CA bundle to use.