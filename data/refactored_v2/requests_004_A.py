# === ARP Faza 4C - refactored code ===
# sample_id: requests_004
# condition: A
# timestamp: 2026-06-04T13:23:15
# original_cc: 19, original_mi: None
# changed_pct: 0.6239
# === END HEADER ===
def build_digest_header(self, method, url):
    """
    :rtype: str
    """
    realm, nonce, qop, algorithm, opaque = self._get_challenge_params()
    hash_utf8 = self._select_hash_function(algorithm)

    if hash_utf8 is None:
        return None

    path = self._get_request_path(url)
    A1 = f"{self.username}:{realm}:{self.password}"
    A2 = f"{method}:{path}"

    HA1 = hash_utf8(A1)
    HA2 = hash_utf8(A2)

    ncvalue, cnonce = self._update_nonce_count_and_generate_cnonce(nonce)
    if algorithm and algorithm.upper() == "MD5-SESS":
        HA1 = hash_utf8(f"{HA1}:{nonce}:{cnonce}")

    respdig = self._calculate_response_digest(HA1, HA2, nonce, ncvalue, cnonce, qop, hash_utf8)
    if respdig is None:
        return None

    self._thread_local.last_nonce = nonce
    return self._build_authorization_header(realm, nonce, path, respdig, opaque, algorithm, qop, ncvalue, cnonce)


def _get_challenge_params(self):
    return (
        self._thread_local.chal["realm"],
        self._thread_local.chal["nonce"],
        self._thread_local.chal.get("qop"),
        self._thread_local.chal.get("algorithm"),
        self._thread_local.chal.get("opaque"),
    )


def _select_hash_function(self, algorithm):
    if algorithm is None:
        _algorithm = "MD5"
    else:
        _algorithm = algorithm.upper()

    if _algorithm == "MD5" or _algorithm == "MD5-SESS":
        return lambda x: hashlib.md5(x.encode("utf-8") if isinstance(x, str) else x).hexdigest()
    elif _algorithm == "SHA":
        return lambda x: hashlib.sha1(x.encode("utf-8") if isinstance(x, str) else x).hexdigest()
    elif _algorithm == "SHA-256":
        return lambda x: hashlib.sha256(x.encode("utf-8") if isinstance(x, str) else x).hexdigest()
    elif _algorithm == "SHA-512":
        return lambda x: hashlib.sha512(x.encode("utf-8") if isinstance(x, str) else x).hexdigest()
    return None


def _get_request_path(self, url):
    p_parsed = urlparse(url)
    path = p_parsed.path or "/"
    if p_parsed.query:
        path += f"?{p_parsed.query}"
    return path


def _update_nonce_count_and_generate_cnonce(self, nonce):
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
    return ncvalue, cnonce


def _calculate_response_digest(self, HA1, HA2, nonce, ncvalue, cnonce, qop, hash_utf8):
    KD = lambda s, d: hash_utf8(f"{s}:{d}")
    if not qop:
        return KD(HA1, f"{nonce}:{HA2}")
    elif qop == "auth" or "auth" in qop.split(","):
        noncebit = f"{nonce}:{ncvalue}:{cnonce}:auth:{HA2}"
        return KD(HA1, noncebit)
    return None


def _build_authorization_header(self, realm, nonce, path, respdig, opaque, algorithm, qop, ncvalue, cnonce):
    base = (
        f'username="{self.username}", realm="{realm}", nonce="{nonce}", '
        f'uri="{path}", response="{respdig}"'
    )
    if opaque:
        base += f', opaque="{opaque}"'
    if algorithm:
        base += f', algorithm="{algorithm}"'
    if qop:
        base += f', qop="auth", nc={ncvalue}, cnonce="{cnonce}"'
    return f"Digest {base}"