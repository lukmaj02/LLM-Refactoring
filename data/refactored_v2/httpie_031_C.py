# === ARP Faza 4C - refactored code ===
# sample_id: httpie_031
# condition: C
# timestamp: 2026-06-04T14:09:01
# original_cc: 1, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def _body_from_input(self, data):
    """Read the data from the CLI.

    """
    self._ensure_one_data_source(self.has_stdin_data, self.args.data,
                                 self.args.files)
    self.args.data = data.encode()