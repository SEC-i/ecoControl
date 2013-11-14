import os

# checks if pid belongs to a running process
def pid_is_running(pid):
    try:
        os.kill(pid, 0)

    except OSError:
        return

    else:
        return pid

# writes pid to pidfile but returns false if pidfile belongs to running process
def write_pidfile_or_fail(path_to_pidfile):
    if os.path.exists(path_to_pidfile):
        pid = int(open(path_to_pidfile).read())

        if pid_is_running(pid):
            # print("Sorry, found a pidfile!  Process {0} is still running.".format(pid))
            return False

        else:
            os.remove(path_to_pidfile)

    open(path_to_pidfile, 'w').write(str(os.getpid()))
    return path_to_pidfile