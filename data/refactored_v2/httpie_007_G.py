# === ARP Faza 4C - refactored code ===
# sample_id: httpie_007
# condition: G
# timestamp: 2026-06-04T13:59:27
# original_cc: 24, original_mi: None
# changed_pct: 0.8649
# === END HEADER ===
def _handle_auth_from_url_credentials(self, url):
        """Extracts auth credentials from the URL if present and not already set."""
        if self.args.auth is None and not self.args.auth_type:
            if url.username is not None:
                username = url.username
                password = url.password or ''
                self.args.auth = AuthCredentials(
                    key=username,
                    value=password,
                    sep=SEPARATOR_CREDENTIALS,
                    orig=SEPARATOR_CREDENTIALS.join([username, password])
                )

    def _get_and_initialize_auth_plugin(self, default_auth_plugin):
        """Determines auth type and initializes the corresponding plugin."""
        if not self.args.auth_type:
            self.args.auth_type = default_auth_plugin.auth_type
        return plugin_manager.get_auth_plugin(self.args.auth_type)()

    def _handle_netrc_credentials(self, plugin):
        """Checks for and applies .netrc credentials if applicable."""
        if (not self.args.ignore_netrc
                and self.args.auth is None
                and plugin.netrc_parse):
            netrc_credentials = get_netrc_auth(self.args.url)
            if netrc_credentials:
                self.args.auth = AuthCredentials(
                    key=netrc_