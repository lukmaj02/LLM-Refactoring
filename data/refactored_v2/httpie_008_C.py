# === ARP Faza 4C - refactored code ===
# sample_id: httpie_008
# condition: C
# timestamp: 2026-06-04T14:01:49
# original_cc: 11, original_mi: None
# changed_pct: 0.2500
# === END HEADER ===
def parse_args(
    self,
    env: Environment,
    args=None,
    namespace=None
) -> argparse.Namespace:
    self.env = env
    self.env.args = namespace = namespace or argparse.Namespace()
    self.args, no_options = super().parse_known_args(args, namespace)
    if self.args.debug:
        self.args.traceback = True
    self.has_stdin_data = (
        self.env.stdin
        and not self.args.ignore_stdin
        and not self.env.stdin_isatty
    )
    self.has_input_data = self.has_stdin_data or self.args.raw is not None
    # Arguments processing and environment setup.
    self._apply_no_options(no_options)
    self._process_request_type()
    self._process_download_options()
    self._setup_standard_streams()
    self._process_output_options()
    self._process_pretty_options()
    self._process_format_options()
    self._guess_method()
    self._parse_items()
    self._process_url()
    self._process_auth()
    self._process_ssl_cert()
    self._process_request_body()
    self._validate_compress_options()
    return self.args

def _process_request_body(self):
    if self.args.raw is not None:
        self._body_from_input(self.args.raw)
    elif self.has_stdin_data:
        self._body_from_file(self.env.stdin)

def _validate_compress_options(self):
    if not self.args.compress:
        return
    # TODO: allow --compress with --chunked / --multipart
    if self.args.chunked:
        self.error('cannot combine --compress and --chunked')
    if self.args.multipart:
        self.error('cannot combine --compress and --multipart')