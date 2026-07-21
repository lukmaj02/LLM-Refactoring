# === ARP Faza 4C - refactored code ===
# sample_id: httpie_011
# condition: A
# timestamp: 2026-06-04T14:02:47
# original_cc: 10, original_mi: None
# changed_pct: 0.7561
# === END HEADER ===
def _setup_standard_streams(self):
    """
    Modify `env.stdout` and `env.stdout_isatty` based on args, if needed.

    """
    self.args.output_file_specified = bool(self.args.output_file)

    if self.args.download:
        self._setup_download_streams()
    elif self.args.output_file:
        self._setup_output_file_streams()

    if self.args.quiet:
        self._setup_quiet_mode()

def _setup_download_streams(self):
    if not self.args.output_file and not self.env.stdout_isatty:
        self.args.output_file = self.env.stdout
    self.env.stdout = self.env.stderr
    self.env.stdout_isatty = self.env.stderr_isatty

def _setup_output_file_streams(self):
    self.args.output_file.seek(0)
    try:
        self.args.output_file.truncate()
    except OSError as e:
        if e.errno != errno.EINVAL:
            raise
    self.env.stdout = self.args.output_file
    self.env.stdout_isatty = False

def _setup_quiet_mode(self):
    self.env.quiet = self.args.quiet
    self.env.stderr = self.env.devnull
    if not (self.args.output_file_specified and not self.args.download):
        self.env.stdout = self.env.devnull
    self.env.apply_warnings_filter()