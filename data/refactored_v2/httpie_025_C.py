# === ARP Faza 4C - refactored code ===
# sample_id: httpie_025
# condition: C
# timestamp: 2026-06-04T14:07:29
# original_cc: 6, original_mi: None
# changed_pct: 0.8333
# === END HEADER ===
def _get_scheme(self):
    if os.path.basename(self.env.program_name) == 'https':
        return 'https://'
    return self.args.default_scheme + '://'

def _expand_localhost_shorthand(self, url, scheme):
    shorthand = re.match(r'^:(?!:)(\d*)(/?.*)$', url)
    if not shorthand:
        return scheme + url
    port = shorthand.group(1)
    rest = shorthand.group(2)
    expanded = scheme + 'localhost'
    if port:
        expanded += ':' + port
    return expanded + rest

def _process_url(self):
    if self.args.url.startswith('://'):
        # Paste URL & add space shortcut: `http ://pie.dev` → `http://pie.dev`
        self.args.url = self.args.url[3:]
    if URL_SCHEME_RE.match(self.args.url):
        return
    scheme = self._get_scheme()
    self.args.url = self._expand_localhost_shorthand(self.args.url, scheme)