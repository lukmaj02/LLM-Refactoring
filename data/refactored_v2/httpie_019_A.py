# === ARP Faza 4C - refactored code ===
# sample_id: httpie_019
# condition: A
# timestamp: 2026-06-04T14:05:47
# original_cc: 6, original_mi: None
# changed_pct: 0.2889
# === END HEADER ===
def _spawn_posix(args: List[str], process_context: ProcessContext) -> None:
    """
    Perform a double fork procedure* to detach from the parent
    process so that we don't block the user even if their original
    command's execution is done but the release fetcher is not.

    [1]: https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap11.html#tag_11_01_03
    """

    from httpie.core import main

    def fork_and_exit_parent():
        try:
            pid = os.fork()
            if pid > 0:
                os._exit(0)
        except OSError:
            os._exit(1)

    fork_and_exit_parent()
    os.setsid()
    fork_and_exit_parent()

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