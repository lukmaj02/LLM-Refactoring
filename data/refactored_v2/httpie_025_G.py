# === ARP Faza 4C - refactored code ===
# sample_id: httpie_025
# condition: G
# timestamp: 2026-06-04T14:07:44
# original_cc: 6, original_mi: None
# changed_pct: 0.5000
# === END HEADER ===
def _determine_url_scheme_prefix(self) -> str:
    """Determine the URL scheme prefix (e.g., 'http://' or 'https://')."""
    if os.path.basename(self.env.program_name) == 'https':
        return 'https://'
    return self.args.default_scheme + '://'

def _process_url(self):
    if self.args.url.startswith('://'):
        # Paste URL & add space shortcut: `http ://pie.dev` → `http://pie.dev`
        self.args.url = self.args.url[3:]

    if not URL_SCHEME_RE.match(self.args.url):
        scheme = self._determine_url_scheme_prefix()

        # See if we're using curl style shorthand for localhost (:3000/foo)
        shorthand = re.match(r'^:(?!:)(\d*)(/?.*)$', self.args.url)
        if shorthand:
            port = shorthand.group(1)
            rest = shorthand.group(2)
            # Construct the URL with localhost shorthand
            new_url = scheme + 'localhost'
            if port:
                new_url += ':' + port
            new_url += rest
            self.args.url = new_url
        else:
            # Prepend the determined scheme
            self.args.url = scheme + self.args.url