# === ARP Faza 4C - refactored code ===
# sample_id: requests_004
# condition: C
# timestamp: 2026-06-04T13:23:04
# original_cc: 19, original_mi: None
# changed_pct: 0.6216
# === END HEADER ===
def _get_hash_func(algorithm):
    """Return a UTF-8 hash function for the given algorithm name, or None."""
    _ALGORITHM_MAP = {
        "MD5": hashlib.md5,
        "MD5-SESS": hashlib.md5,
        "SHA": hashlib.sha1,
        "SHA-256": hashlib.sha256,
        "SHA-512": hashlib.sha512,
    }
    hash_impl = _ALGORITHM_MAP.get(algorithm)
    if hash_impl is None:
        return None

    def hash_utf8(x):
        if isinstance(x, str):
            x = x.encode("utf-8")
        return hash_impl(x).hexdigest()

    return hash_utf8


def _build_digest_path(url):
    """Extract the request-uri path (with optional query) from a URL."""
    p_parsed = urlparse(url)
    path = p_parsed.path or "/"
    if p_parsed.query:
        path += f"?{p_parsed.query}"
    return path


def _compute_respdig(hash_utf8, qop, HA1, HA2, nonce, ncvalue, cnonce):
    """Compute the response digest value, or return None for unsupported qop."""
    KD = lambda s, d: hash_utf8(f"{s}:{d}")  # noqa:E731
    if not qop:
        return KD(HA1, f"{nonce}:{HA2}")
    if qop == "auth" or "auth" in qop.split(","):
        noncebit = f"{nonce}:{ncvalue}:{cnonce}:auth:{HA2}"
        return KD(HA1, noncebit)
    # XXX handle auth-int.
    return None


def _build_digest_base(username, realm, nonce, path, respdig, opaque, algorithm, entdig, qop, ncvalue, cnonce):
    """Assemble the Digest header base string."""
    base = (
        f'username="{username}", realm="{realm}", nonce="{nonce}", '
        f'uri="{path}", response="{respdig}"'
    )
    if opaque:
        base += f', opaque="{opaque}"'
    if algorithm:
        base += f', algorithm="{algorithm}"'
    if entdig:
        base += f', digest="{entdig}"'
    if qop:
        base += f', qop="auth", nc={ncvalue}, cnonce="{cnonce}"'
    return base


def build_digest_header(self, method, url):
    """
    :rtype: str
    """
    realm = self._thread_local.chal["realm"]
    nonce = self._thread_local.chal["nonce"]
    qop = self._thread_local.chal.get("qop")
    algorithm = self._thread_local.chal.get("algorithm")
    opaque = self._thread_local.chal.get("opaque")

    _algorithm = algorithm.upper() if algorithm else "MD5"
    hash_utf8 = _get_hash_func(_algorithm)

    if hash_utf8 is None:
        return None

    # XXX not implemented yet
    entdig = None
    path = _build_digest_path(url)

    A1 = f"{self.username}:{realm}:{self.password}"
    A2 = f"{method}:{path}"

    HA1 = hash_utf8(A1)
    HA2 = hash_utf8(A2)

    if nonce == self._thread_local.last_nonce:
        self._thread_local.nonce_count += 1
    else:
        self._thread_local.nonce_count = 1
    ncvalue = f"{self._thread_local.nonce_count:08x}"

    s = str(self._thread_local.nonce_count).encode("utf-8")
    s += nonce.encode("utf-8")
    s += time.ctime().encode("utf-8")
    s += os.urandom(8)
    cnonce = hashlib.sha1(s).hexdigest()[:16]

    if _algorithm == "MD5-SESS":
        HA1 = hash_utf8(f"{HA1}:{nonce}:{cnonce}")

    respdig = _compute_respdig(hash_utf8, qop, HA1, HA2, nonce, ncvalue, cnonce)
    if respdig is None:
        return None

    self._thread_local.last_nonce = nonce

    base = _build_digest_base(
        self.username, realm, nonce, path, respdig,
        opaque, algorithm, entdig, qop, ncvalue, cnonce
    )
    return f"Digest {base}"