# SNAPSHOT METADATA
# sample_id: httpie_007
# repo: httpie
# file: data/repos/httpie/httpie/cli/argparser.py
# function: HTTPieArgumentParser._process_auth
# cc: 24 | mi: N/A | loc: 74
# extracted: 2026-05-01T11:47:36

def _process_auth(self):
    # TODO: refactor & simplify this method.
    self.args.auth_plugin = None
    default_auth_plugin = plugin_manager.get_auth_plugins()[0]
    auth_type_set = self.args.auth_type is not None
    url = urlsplit(self.args.url)

    if self.args.auth is None and not auth_type_set:
        if url.username is not None:
            # Handle http://username:password@hostname/
            username = url.username
            password = url.password or ''
            self.args.auth = AuthCredentials(
                key=username,
                value=password,
                sep=SEPARATOR_CREDENTIALS,
                orig=SEPARATOR_CREDENTIALS.join([username, password])
            )

    if self.args.auth is not None or auth_type_set:
        if not self.args.auth_type:
            self.args.auth_type = default_auth_plugin.auth_type
        plugin = plugin_manager.get_auth_plugin(self.args.auth_type)()

        if (not self.args.ignore_netrc
                and self.args.auth is None
                and plugin.netrc_parse):
            # Only host needed, so it’s OK URL not finalized.
            netrc_credentials = get_netrc_auth(self.args.url)
            if netrc_credentials:
                self.args.auth = AuthCredentials(
                    key=netrc_credentials[0],
                    value=netrc_credentials[1],
                    sep=SEPARATOR_CREDENTIALS,
                    orig=SEPARATOR_CREDENTIALS.join(netrc_credentials)
                )

        if plugin.auth_require and self.args.auth is None:
            self.error('--auth required')

        plugin.raw_auth = self.args.auth
        self.args.auth_plugin = plugin
        already_parsed = isinstance(self.args.auth, AuthCredentials)

        if self.args.auth is None or not plugin.auth_parse:
            self.args.auth = plugin.get_auth()
        else:
            if already_parsed:
                # from the URL
                credentials = self.args.auth
            else:
                credentials = parse_auth(self.args.auth)

            if (not credentials.has_password()
                    and plugin.prompt_password):
                if self.args.ignore_stdin:
                    # Non-tty stdin read by now
                    self.error(
                        'Unable to prompt for passwords because'
                        ' --ignore-stdin is set.'
                    )
                credentials.prompt_password(url.netloc)

            if (credentials.key and credentials.value):
                plugin.raw_auth = credentials.key + ":" + credentials.value

            self.args.auth = plugin.get_auth(
                username=credentials.key,
                password=credentials.value,
            )
    if not self.args.auth and self.args.ignore_netrc:
        # Set a no-op auth to force requests to ignore .netrc
        # <https://github.com/psf/requests/issues/2773#issuecomment-174312831>
        self.args.auth = ExplicitNullAuth()
