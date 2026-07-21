# === ARP Faza 4C - refactored code ===
# sample_id: httpie_031
# condition: A
# timestamp: 2026-06-04T14:09:17
# original_cc: 1, original_mi: None
# changed_pct: 0.4444
# === END HEADER ===
def _body_from_input(self, data):
    """Read the data from the CLI.

    """
    self._ensure_one_data_source(self.has_stdin_data, self.args.data, self.args.files)
    self._set_encoded_data(data)

def _set_encoded_data(self, data):
    self.args.data = data.encode()