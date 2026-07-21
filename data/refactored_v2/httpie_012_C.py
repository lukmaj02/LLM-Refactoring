# === ARP Faza 4C - refactored code ===
# sample_id: httpie_012
# condition: C
# timestamp: 2026-06-04T14:03:00
# original_cc: 10, original_mi: None
# changed_pct: 0.4872
# === END HEADER ===
def _check_output_options(self, value, option):
    unknown = set(value) - OUTPUT_OPTIONS
    if unknown:
        self.error(f'Unknown output options: {option}={",".join(unknown)}')

def _resolve_default_output_options(self):
    if self.args.verbose >= 2:
        return ''.join(OUTPUT_OPTIONS)
    if self.args.verbose == 1:
        return ''.join(BASE_OUTPUT_OPTIONS)
    if self.args.offline:
        return OUTPUT_OPTIONS_DEFAULT_OFFLINE
    if not self.env.stdout_isatty:
        return OUTPUT_OPTIONS_DEFAULT_STDOUT_REDIRECTED
    return OUTPUT_OPTIONS_DEFAULT

def _process_output_options(self):
    """Apply defaults to output options, or validate the provided ones.

    The default output options are stdout-type-sensitive.

    """
    if self.args.verbose:
        self.args.all = True

    if self.args.output_options is None:
        self.args.output_options = self._resolve_default_output_options()

    if self.args.output_options_history is None:
        self.args.output_options_history = self.args.output_options

    self._check_output_options(self.args.output_options, '--print')
    self._check_output_options(self.args.output_options_history, '--history-print')

    if self.args.download and OUT_RESP_BODY in self.args.output_options:
        # Response body is always downloaded with --download and it goes
        # through a different routine, so we remove it.
        self.args.output_options = str(
            set(self.args.output_options) - set(OUT_RESP_BODY))