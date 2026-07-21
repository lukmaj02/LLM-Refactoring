# === ARP Faza 4C - refactored code ===
# sample_id: httpie_007
# condition: A
# timestamp: 2026-06-04T14:01:31
# original_cc: 24, original_mi: None
# changed_pct: 0.7253
# === END HEADER ===
def _process_auth(self):
    self.args.auth_plugin = None
    default_auth_plugin = plugin_manager.get_auth_plugins()[0]
    auth_type_set = self.args.auth_type is not None
    url = urlsplit(self.args.url)

    self._set_auth_from_url(url, auth_type_set)

    if self.args.auth is not None or auth_type_set:
        self._set_auth_plugin(default_auth_plugin)
        plugin = self.args.auth_plugin

        if self._should_use_netrc(plugin):
            self._set_auth_from_netrc()

        if plugin.auth_require and self.args.auth is None:
            self.error('--auth required')

        plugin.raw_auth = self.args.auth
        already_parsed = isinstance(self.args.auth, AuthCredentials)

        if self.args.auth is None or not plugin.auth_parse:
            self.args.auth = plugin.get_auth()
        else:
            credentials = self._get_credentials(already_parsed)
            self._handle_password_prompt(credentials, url, plugin)
            self._set_plugin_raw_auth(credentials, plugin)
            self.args.auth = plugin.get_auth(
                username=credentials.key,
                password=credentials.value,
            )

    if not self.args.auth and self.args.ignore_netrc:
        self.args.auth = ExplicitNullAuth()


def _set_auth_from_url(self, url, auth_type_set):
    if self.args.auth is None and not auth_type_set:
        if url.username is not None:
            username = url.username
            password = url.password or ''
            self.args.auth = AuthCredentials(
                key=username,
                value=password,
                sep=SEPARATOR_CREDENTIALS,
                orig=SEPARATOR_CREDENTIALS.join([username, password])
            )


def _set_auth_plugin(self, default_auth_plugin):
    if not self.args.auth_type:
        self.args.auth_type = default_auth_plugin.auth_type
    self.args.auth_plugin = plugin_manager.get_auth_plugin(self.args.auth_type)()


def _should_use_netrc(self, plugin):
    return (not self.args.ignore_netrc
            and self.args.auth is None
            and plugin.netrc_parse)


def _set_auth_from_netrc(self):
    netrc_credentials = get_netrc_auth(self.args.url)
    if netrc_credentials:
        self.args.auth = AuthCredentials(
            key=netrc_credentials[0],
            value=netrc_credentials[1],
            sep=SEPARATOR_CREDENTIALS,
            orig=SEPARATOR_CREDENTIALS.join(netrc_credentials)
        )


def _get_credentials(self, already_parsed):
    if already_parsed:
        return self.args.auth
    return parse_auth(self.args.auth)


def _handle_password_prompt(self, credentials, url, plugin):
    if not credentials.has_password() and plugin.prompt_password:
        if self.args.ignore_stdin:
            self.error(
                'Unable to prompt for passwords because'
                ' --ignore-stdin is set.'
            )
        credentials.prompt_password(url.netloc)


def _set_plugin_raw_auth(self, credentials, plugin):
    if credentials.key and credentials.value:
        plugin.raw_auth = credentials.key + ":" + credentials.value