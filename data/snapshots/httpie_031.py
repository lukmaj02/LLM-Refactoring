# SNAPSHOT METADATA
# sample_id: httpie_031
# repo: httpie
# file: data/repos/httpie/httpie/cli/argparser.py
# function: HTTPieArgumentParser._body_from_input
# cc: 1 | mi: N/A | loc: 7
# extracted: 2026-05-01T11:47:36

def _body_from_input(self, data):
    """Read the data from the CLI.

    """
    self._ensure_one_data_source(self.has_stdin_data, self.args.data,
                                 self.args.files)
    self.args.data = data.encode()
