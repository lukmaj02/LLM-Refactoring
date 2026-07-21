# SNAPSHOT METADATA
# sample_id: httpie_009
# repo: httpie
# file: data/repos/httpie/httpie/cli/argparser.py
# function: HTTPieArgumentParser._guess_method
# cc: 11 | mi: N/A | loc: 38
# extracted: 2026-05-01T11:47:36

def _guess_method(self):
    """Set `args.method` if not specified to either POST or GET
    based on whether the request has data or not.

    """
    if self.args.method is None:
        # Invoked as `http URL'.
        assert not self.args.request_items
        if self.has_input_data:
            self.args.method = HTTP_POST
        else:
            self.args.method = HTTP_GET

    # FIXME: False positive, e.g., "localhost" matches but is a valid URL.
    elif not re.match('^[a-zA-Z]+$', self.args.method):
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
            # Infer the method
            has_data = (
                self.has_input_data
                or any(
                    item.sep in SEPARATOR_GROUP_DATA_ITEMS
                    for item in self.args.request_items)
            )
            self.args.method = HTTP_POST if has_data else HTTP_GET
