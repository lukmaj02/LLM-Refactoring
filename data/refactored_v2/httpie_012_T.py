# === ARP Faza 4C - refactored code ===
# sample_id: httpie_012
# condition: T
# timestamp: 2026-06-04T14:04:15
# original_cc: 10, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def _process_output_options(self):
    """Apply defaults to output options, or validate the provided ones.

    The default output options are stdout-type-sensitive.

    """

    def check_options(value, option):
        unknown = set(value) - OUTPUT_OPTIONS
        if unknown:
            self.error(f'Unknown output options: {option}={",".join(unknown)}')

    if self.args.verbose:
        self.args.all = True

    if self.args.output_options is None:
        if self.args.verbose >= 2:
            self.args.output_options = ''.join(OUTPUT_OPTIONS)
        elif self.args.verbose == 1:
            self.args.output_options = ''.join(BASE_OUTPUT_OPTIONS)
        elif self.args.offline:
            self.args.output_options = OUTPUT_OPTIONS_DEFAULT_OFFLINE
        elif not self.env.stdout_isatty:
            self.args.output_options = OUTPUT_OPTIONS_DEFAULT_STDOUT_REDIRECTED
        else:
            self.args.output_options = OUTPUT_OPTIONS_DEFAULT

    if self.args.output_options_history is None:
        self.args.output_options_history = self.args.output_options

    check_options(self.args.output_options, '--print')
    check_options(self.args.output_options_history, '--history-print')

    if self.args.download and OUT_RESP_BODY in self.args.output_options:
        # Response body is always downloaded with --download and it goes
        # through a different routine, so we remove it.
        self.args.output_options = str(
            set(self.args.output_options) - set(OUT_RESP_BODY))
