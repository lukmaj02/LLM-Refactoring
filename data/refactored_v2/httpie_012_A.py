# === ARP Faza 4C - refactored code ===
# sample_id: httpie_012
# condition: A
# timestamp: 2026-06-04T14:03:00
# original_cc: 10, original_mi: None
# changed_pct: 0.6842
# === END HEADER ===
def _process_output_options(self):
    """Apply defaults to output options, or validate the provided ones.

    The default output options are stdout-type-sensitive.

    """
    if self.args.verbose:
        self.args.all = True

    self.args.output_options = self._determine_output_options()
    self.args.output_options_history = self.args.output_options_history or self.args.output_options

    self._check_options(self.args.output_options, '--print')
    self._check_options(self.args.output_options_history, '--history-print')

    if self.args.download and OUT_RESP_BODY in self.args.output_options:
        self.args.output_options = str(set(self.args.output_options) - set(OUT_RESP_BODY))


def _determine_output_options(self):
    if self.args.output_options is not None:
        return self.args.output_options

    if self.args.verbose >= 2:
        return ''.join(OUTPUT_OPTIONS)
    if self.args.verbose == 1:
        return ''.join(BASE_OUTPUT_OPTIONS)
    if self.args.offline:
        return OUTPUT_OPTIONS_DEFAULT_OFFLINE
    if not self.env.stdout_isatty:
        return OUTPUT_OPTIONS_DEFAULT_STDOUT_REDIRECTED
    return OUTPUT_OPTIONS_DEFAULT


def _check_options(self, value, option):
    unknown = set(value) - OUTPUT_OPTIONS
    if unknown:
        self.error(f'Unknown output options: {option}={",".join(unknown)}')