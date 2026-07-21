# SNAPSHOT METADATA
# sample_id: requests_028
# repo: requests
# file: data/repos/requests/src/requests/exceptions.py
# function: JSONDecodeError.__reduce__
# cc: 1 | mi: N/A | loc: 9
# extracted: 2026-05-01T11:47:36

def __reduce__(self):
    """
    The __reduce__ method called when pickling the object must
    be the one from the JSONDecodeError (be it json/simplejson)
    as it expects all the arguments for instantiation, not just
    one like the IOError, and the MRO would by default call the
    __reduce__ method from the IOError due to the inheritance order.
    """
    return CompatJSONDecodeError.__reduce__(self)
