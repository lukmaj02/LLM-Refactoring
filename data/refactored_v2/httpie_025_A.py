# === ARP Faza 4C - refactored code ===
# sample_id: httpie_025
# condition: A
# timestamp: 2026-06-04T14:07:35
# original_cc: 6, original_mi: None
# changed_pct: 0.8261
# === END HEADER ===
def _process_url(self):
    self._remove_leading_colons()
    if not URL_SCHEME_RE.match(self.args.url):
        scheme = self._determine_scheme()
        self.args.url = self._process_shorthand(scheme) or scheme + self.args.url

def _remove_leading_colons(self):
    if self.args.url.startswith('://'):
        self.args.url = self.args.url[3:]

def _determine_scheme(self):
    return 'https://' if os.path.basename(self.env.program_name) == 'https' else self.args.default_scheme + '://'

def _process_shorthand(self, scheme):
    shorthand = re.match(r'^:(?!:)(\d*)(/?.*)$', self.args.url)
    if shorthand:
        port = shorthand.group(1)
        rest = shorthand.group(2)
        url = scheme + 'localhost'
        if port:
            url += ':' + port
        return url + rest
    return None