# === ARP Faza 4C - refactored code ===
# sample_id: httpie_009
# condition: G
# timestamp: 2026-06-04T14:00:04
# original_cc: 11, original_mi: None
# changed_pct: 0.8723
# === END HEADER ===
def _set_default_method(self):
    """Set `args.method` to POST or GET based on input data when not specified."""
    # Invoked as `http URL'.
    assert not self.args.request_items
    self.args.method = HTTP_POST if self.has_input_data else HTTP_GET

def _is_potential_url_as_method(self, method_candidate: str) -> bool:
    """Check if the method candidate looks like a URL rather than a method name."""
    # FIXME: False positive, e.g., "localhost" matches but is a valid URL.
    return not re.match('^[a-zA-Z]+$', method_candidate)

def _re_evaluate_method_from_misplaced_url(self):
    """Handle the case where the URL was parsed as the method and re-infer the method."""
    # Invoked as `http URL item+'. The URL is now in `args.method`
    # and the first ITEM is now incorrectly in `args.url`.
    try:
        # Parse the URL as an ITEM and store it as the first ITEM arg.
        self.args.request_items.insert(0, KeyValueArgType(
            *SEPARATOR_GROUP_ALL_ITEMS).__call__(self.args.url))
    except argparse.ArgumentTypeError as e:
        if self.args.traceback:
            raise
        self.error(e.args[0])
    else:
        # Set the URL correctly
        self.args.url = self.args.method
        self._infer_method_from_request_items()

def _infer_method_from_request_items(self):
    """Infer the HTTP method based on the presence of request data items."""
    has_data = (
        self.has_input_data
        or any(
            item.sep in SEPARATOR_GROUP_DATA_ITEMS
            for item in self.args.request_items)
    )
    self.args.method = HTTP_POST if has_data else HTTP_GET

def _guess_method(self):
    """Set `args.method` if not specified to either POST or GET
    based on whether the request has data or not.

    """
    if self.args.method is None:
        self._set_default_method()
    elif self._is_potential_url_as_method(self.args.method):
        self._re_evaluate_method_from_misplaced_url()