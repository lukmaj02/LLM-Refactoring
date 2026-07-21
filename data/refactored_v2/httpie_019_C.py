# === ARP Faza 4C - refactored code ===
# sample_id: httpie_019
# condition: C
# timestamp: 2026-06-04T14:05:42
# original_cc: 6, original_mi: None
# changed_pct: 0.6383
# === END HEADER ===
def _fork_or_exit(exit_code: int) -> None:
    try:
        pid = os.fork()
        if pid > 0:
            os._exit(exit_code)
    except OSError:
        os._exit(1)


def _close_standard_streams() -> None:
    sys.stdin.close()
    sys.stdout.close()
    sys.stderr.close()


def _run_detached_task(args: List[str], process_context: ProcessContext) -> None:
    from httpie.core import main

    if platform.system() == 'Darwin':
        process = _start_process(args, env=process_context)
        process.communicate()
    else:
        os.environ.update(process_context)
        with suppress(BaseException):
            main(['http'] + args)


def _spawn_posix(args: List[str], process_context: ProcessContext) -> None:
    """
    Perform a double fork procedure* to detach from the parent
    process so that we don't block the user even if their original
    command's execution is done but the release fetcher is not.

    [1]: https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap11.html#tag_11_01_03
    """
    try:
        pid = os.fork()
        if pid > 0:
            return
    except OSError:
        os._exit(1)

    os.setsid()
    _fork_or_exit(exit_code=0)
    _close_standard_streams()
    _run_detached_task(args, process_context)
    os._exit(0)