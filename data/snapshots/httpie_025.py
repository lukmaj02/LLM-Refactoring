# SNAPSHOT METADATA
# sample_id: httpie_025
# repo: httpie
# file: data/repos/httpie/httpie/cli/argparser.py
# function: HTTPieArgumentParser._process_url
# cc: 6 | mi: N/A | loc: 21
# extracted: 2026-05-01T11:47:36

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
