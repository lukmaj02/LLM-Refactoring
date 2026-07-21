# === ARP Faza 4C - refactored code ===
# sample_id: httpie_007
# condition: C
# timestamp: 2026-06-04T14:01:16
# original_cc: 24, original_mi: None
# changed_pct: 0.6988
# === END HEADER ===
def _make_auth_credentials(key, value):
    return AuthCredentials(
        key=key,
        value=value,
        sep=SEPARATOR_CREDENTIALS,
        orig=SEPARATOR_CREDENTIALS.join([key, value])
    )


def _process_auth(self):
    self.args.auth_plugin = None
    default_auth_plugin = plugin_manager.get_auth_plugins()[0]
    auth_type_set = self.args.auth_type is not None
    url = urlsplit(self.args.url)

    if self.args.auth is None and not auth_type_set:
        self._try_auth_from_url(url)

    if self.args.auth is not None or auth_type_set:
        if not self.args.auth_type:
            self.args.auth_type = default_auth_plugin.auth_type
        plugin = plugin_manager.get_auth_plugin(self.args.auth_type)()

        self._try_auth_from_netrc(plugin)

        if plugin.auth_require and self.args.auth is None:
            self.error('--auth required')

        plugin.raw_auth = self.args.auth
        self.args.auth_plugin = plugin

        self.args.auth = self._resolve_auth(plugin, url)

    if not self.args.auth and self.args.ignore_netrc:
        # Set a no-op auth to force requests to ignore .netrc
        # <https://github.com/psf/requests/issues/2773#issuecomment-174312831>
        self.args.auth = ExplicitNullAuth()


def _try_auth_from_url(self, url):
    if url.username is not None:
        # Handle http://username:password@hostname/
        self.args.auth = _make_auth_credentials(
            key=url.username,
            value=url.password or '',
        )


def _try_auth_from_netrc(self, plugin):
    if self.args.ignore_netrc or self.args.auth is not None or not plugin.netrc_parse:
        return
    # Only host needed, so it's OK URL not finalized.
    netrc_credentials = get_netrc_auth(self.args.url)
    if netrc_credentials:
        self.args.auth = _make_auth_credentials(
            key=netrc_credentials[0],
            value=netrc_credentials[1],
        )


def _resolve_auth(self, plugin, url):
    if self.args.auth is None or not plugin.auth_parse:
        return plugin.get_auth()

    already_parsed = isinstance(self.args.auth, AuthCredentials)
    credentials = self.args.auth if already_parsed else parse_auth(self.args.auth)

    if not credentials.has_password() and plugin.prompt_password:
        if self.args.ignore_stdin:
            # Non-tty stdin read by now
            self.error(
                'Unable to prompt for passwords because'
                ' --ignore-stdin is set.'
            )
        credentials.prompt_password(url.netloc)

    if credentials.key and credentials.value:
        plugin.raw_auth = credentials.key + ":" + credentials.value

    return plugin.get_auth(
        username=credentials.key,
        password=credentials.value,
    )