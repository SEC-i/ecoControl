import os

def pid_is_running(pid):
    """
    checks if pid belongs to a running process
    """
    try:
        os.kill(pid, 0)

    except OSError:
        return

    else:
        return pid


def write_pidfile_or_fail(path_to_pidfile):
    """
    writes pid to pidfile but returns false
    if pidfile belongs to running process
    """
    if os.path.exists(path_to_pidfile):
        pid = int(open(path_to_pidfile).read())

        if pid_is_running(pid):
            return False

        else:
            os.remove(path_to_pidfile)

    open(path_to_pidfile, 'w').write(str(os.getpid()))
    return path_to_pidfile
