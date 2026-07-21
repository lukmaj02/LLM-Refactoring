# === ARP Faza 4C - refactored code ===
# sample_id: httpie_025
# condition: T
# timestamp: 2026-06-04T14:06:45
# original_cc: 6, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def _process_url(self):
    if self.args.url.startswith('://'):
        # Paste URL & add space shortcut: `http ://pie.dev` → `http://pie.dev`
        self.args.url = self.args.url[3:]
    if not URL_SCHEME_RE.match(self.args.url):
        if os.path.basename(self.env.program_name) == 'https':
            scheme = 'https://'
        else:
            scheme = self.args.default_scheme + '://'

        # See if we're using curl style shorthand for localhost (:3000/foo)
        shorthand = re.match(r'^:(?!:)(\d*)(/?.*)$', self.args.url)
        if shorthand:
            port = shorthand.group(1)
            rest = shorthand.group(2)
            self.args.url = scheme + 'localhost'
            if port:
                self.args.url += ':' + port
            self.args.url += rest
        else:
            self.args.url = scheme + self.args.url
