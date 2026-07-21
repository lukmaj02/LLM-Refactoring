# === ARP Faza 4C - refactored code ===
# sample_id: httpie_019
# condition: G
# timestamp: 2026-06-04T14:05:39
# original_cc: 6, original_mi: None
# changed_pct: 0.3265
# === END HEADER ===
def _perform_fork_and_exit_on_error() -> int:
    """Performs a single fork and exits the child process with 1 on OSError."""
    try:
        return os.fork()
    except OSError:
        os._exit(1)


def _spawn_posix(args: List[str], process_context: ProcessContext) -> None:
    """
    Perform a double fork procedure* to detach from the parent
    process so that we don't block the user even if their original
    command's execution is done but the release fetcher is not.

    [1]: https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap11.html#tag_11_01_03
    """

    from httpie.core import main

    # First fork: parent returns, child continues
    pid = _perform_fork_and_exit_on_error()
    if pid > 0:
        return

    os.setsid()

    # Second fork: parent (of the daemon) exits, child continues as the daemon
    pid = _perform_fork_and_exit_on_error()
    if pid > 0:
        os._exit(0)

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