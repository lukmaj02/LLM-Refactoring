# SNAPSHOT METADATA
# sample_id: httpie_030
# repo: httpie
# file: data/repos/httpie/httpie/downloads.py
# function: DownloadStatus.__init__
# cc: 1 | mi: N/A | loc: 7
# extracted: 2026-05-01T11:47:36

def __init__(self, env):
    self.env = env
    self.downloaded = 0
    self.total_size = None
    self.resumed_from = 0
    self.time_started = None
    self.time_finished = None
