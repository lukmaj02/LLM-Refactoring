# SNAPSHOT METADATA
# sample_id: httpie_019
# repo: httpie
# file: data/repos/httpie/httpie/internal/daemons.py
# function: _spawn_posix
# cc: 6 | mi: N/A | loc: 45
# extracted: 2026-05-01T11:47:36

def _spawn_posix(args: List[str], process_context: ProcessContext) -> None:
    """
    Perform a double fork procedure* to detach from the parent
    process so that we don't block the user even if their original
    command's execution is done but the release fetcher is not.

    [1]: https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap11.html#tag_11_01_03
    """

    from httpie.core import main

    try:
        pid = os.fork()
        if pid > 0:
            return
    except OSError:
        os._exit(1)

    os.setsid()

    try:
        pid = os.fork()
        if pid > 0:
            os._exit(0)
    except OSError:
        os._exit(1)

    # Close all standard inputs/outputs
    sys.stdin.close()
    sys.stdout.close()
    sys.stderr.close()

    if platform.system() == 'Darwin':
        # Double-fork is not reliable on MacOS, so we'll use a subprocess
        # to ensure the task is isolated properly.
        process = _start_process(args, env=process_context)
        # Unlike windows, since we already completed the fork procedure
        # we can simply join the process and wait for it.
        process.communicate()
    else:
        os.environ.update(process_context)
        with suppress(BaseException):
            main(['http'] + args)

    os._exit(0)
