# === ARP Faza 4C - refactored code ===
# sample_id: httpie_009
# condition: A
# timestamp: 2026-06-04T14:02:12
# original_cc: 11, original_mi: None
# changed_pct: 0.7632
# === END HEADER ===
def _guess_method(self):
    """Set `args.method` if not specified to either POST or GET
    based on whether the request has data or not.

    """
    if self.args.method is None:
        self._set_method_based_on_input_data()
    elif not re.match('^[a-zA-Z]+$', self.args.method):
        self._handle_invalid_method()

def _set_method_based_on_input_data(self):
    assert not self.args.request_items
    self.args.method = HTTP_POST if self.has_input_data else HTTP_GET

def _handle_invalid_method(self):
    try:
        self._parse_url_as_item()
    except argparse.ArgumentTypeError as e:
        if self.args.traceback:
            raise
        self.error(e.args[0])
    else:
        self._set_url_and_infer_method()

def _parse_url_as_item(self):
    self.args.request_items.insert(0, KeyValueArgType(
        *SEPARATOR_GROUP_ALL_ITEMS).__call__(self.args.url))

def _set_url_and_infer_method(self):
    self.args.url = self.args.method
    has_data = (
        self.has_input_data
        or any(
            item.sep in SEPARATOR_GROUP_DATA_ITEMS
            for item in self.args.request_items)
    )
    self.args.method = HTTP_POST if has_data else HTTP_GET