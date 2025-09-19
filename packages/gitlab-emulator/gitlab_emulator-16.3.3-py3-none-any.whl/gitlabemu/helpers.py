"""
Various useful common funcs
"""
from __future__ import print_function

import os.path
import time
from select import select
from threading import Thread, Lock
import sys
import re
import platform
import subprocess
from prompt_toolkit import print_formatted_text, HTML

from typing import Optional, List, Dict, Union, Tuple
from urllib.parse import urlparse

from .errors import DockerExecError
from .resnamer import resource_owner_alive, is_gle_resource
from .logmsg import info, debug
from .localstats import get_duration


class ProcessLineProxyThread(Thread):
    def __init__(self, process, stdout, linehandler=None):
        super(ProcessLineProxyThread, self).__init__()
        self.errors = []
        self.process = process
        self.stdout = stdout
        self.linehandler = linehandler
        self.daemon = True

    def writeout(self, data):
        retval = None
        if self.stdout and data:
            encoding = "ascii"
            if hasattr(self.stdout, "encoding"):
                encoding = self.stdout.encoding
            try:
                decoded = data.decode(encoding, "namereplace")
                self.stdout.write(decoded)
                retval = decoded
            except (TypeError, UnicodeError):
                # codec cant handle namereplace or the codec cant represent this.
                # decode it to utf-8 and replace non-printable ascii with
                # chars with '?'
                decoded = data.decode("utf-8", "replace")
                text = re.sub(r'[^\x00-\x7F]', "?", decoded)
                self.stdout.write(text)
                retval = text

            if self.linehandler:
                try:
                    self.linehandler(data)
                except DockerExecError as err:
                    self.errors.append(err)
        return retval

    def run(self):
        """Pump stdout Wait for a job to end """
        # do nothing for interactive jobs
        while self.process.stdout is not None:
            data = None
            if not is_windows():
                select([self.process.stdout], [], [], 1)
            try:
                data = self.process.stdout.readline()
            except ValueError:  # pragma: no cover
                pass
            except Exception as err:  # pragma: no cover
                self.errors.append(err)
                raise
            finally:
                if data:
                    self.writeout(data)
            if self.process.poll() is not None:
                break

        if hasattr(self.stdout, "flush"):
            self.stdout.flush()


class PrettyProcessLineProxyThread(ProcessLineProxyThread):
    """format job output and logs using color outputs"""

    def __init__(self, process, stdout, linehandler=None):
        super().__init__(process, stdout, linehandler=None)
        self.spinner_state = 0
        self.spinner_chars = ["|", "/", "-", "\\"]
        self.lock = Lock()
        self.last_msg = None
        self.frontend = Thread(target=self.frontend_thread, daemon=True)
        self.timings = {}

    @staticmethod
    def get_current_job() -> str:
        """Get the name of the current job"""
        return GLE_RUNTIME_GLOBALS.current_job.name

    @staticmethod
    def get_current_job_elapsed() -> int:
        """Get how long the current job was startede"""
        return GLE_RUNTIME_GLOBALS.get_elasped_job_time()

    def get_estimated_job_duration(self) -> int:
        """Get how long this job should probably take based on history"""
        name = self.get_current_job()
        if name:
            timing = self.timings.get(name, None)
            if timing is None:
                timing = get_duration(self.get_current_job())
                self.timings[name] = timing
            return timing
        return 0

    def run(self):
        self.frontend.start()
        super().run()
        self.frontend.join()

    def print_last_frontend(self):
        if self.last_msg is not None:
            print("\r" + len(self.last_msg) * " " + " \r", end="")
            print_formatted_text(HTML(self.last_msg), end="")

    def frontend_thread(self):
        while self.process.returncode is None:
            time.sleep(0.5)
            progress = ""
            total = self.get_estimated_job_duration()
            elapsed = self.get_current_job_elapsed()
            remaining = max(total - elapsed, 0)
            if total > 10:
                fraction = min(elapsed / total, 1)
                progress = f"({fraction:4.0%}) "
                if remaining > 0:
                    if remaining > 100:
                        # report mins
                        progress += f"{int(remaining / 60)} mins"
                    else:
                        # report in seconds
                        progress += f"{int(remaining)} sec"
                    progress += " remaining"

            msg = (f"<b bg='ansiblue'>GLE {GLE_RUNTIME_GLOBALS.current_job.name} "
                   + f"{self.spinner()} {progress} </b>  ")
            with self.lock:
                print("\r" + len(msg) * " " + " \r", end="")
                self.last_msg = msg
                self.print_last_frontend()

    def spinner(self) -> str:
        text = self.spinner_chars[self.spinner_state]
        self.spinner_state = (1 + self.spinner_state) % len(self.spinner_chars)
        return text

    def writeout(self, data):
        with self.lock:
            if self.last_msg:
                print("\r" + len(self.last_msg) * " " + " \r", end="")
            super(PrettyProcessLineProxyThread, self).writeout(data)
            self.print_last_frontend()


def communicate(process,
                stdout=sys.stdout,
                script=None,
                throw=False,
                linehandler=None):
    """
    Write output incrementally to stdout, waits for process to end
    :param process: a Popened child process
    :param stdout: a file-like object to write to
    :param script: a script (ie, bytes) to stream to stdin
    :param throw: raise an exception if the process exits non-zero
    :param linehandler: if set, pass the line to this callable
    :return:
    """
    linethread_factory = GLE_RUNTIME_GLOBALS.output_thread_type

    if process.stdout is None:  # pragma: no cover
        # interactive job, just wait
        process.wait()
        return

    data = None
    if script is not None:
        process.stdin.write(script)
        process.stdin.flush()
        process.stdin.close()

    comm_thread = linethread_factory(process, stdout, linehandler=linehandler)
    thread_started = False
    try:
        comm_thread.start()
        thread_started = True
    except RuntimeError:  # pragma: no cover
        # could not create the thread, so use a loop
        pass

    # use a thread to stream build output if we can (hpux can't)
    if comm_thread and thread_started:
        while process.poll() is None:
            if comm_thread.is_alive():
                comm_thread.join(timeout=5)

        if comm_thread.is_alive():
            comm_thread.join()

    # either the task has ended or we could not create a thread, either way,
    # stream the remaining stdout data
    while True:
        try:
            if process.stdout is not None:
                data = process.stdout.readline()
        except ValueError:  # pragma: no cover
            pass
        if data:
            # we can still use our proxy object to decode and write the data
            comm_thread.writeout(data)

        if process.poll() is not None:
            break

    # process has definitely already ended, read all the lines, this wont deadlock
    while True:
        line = None
        if process.stdout is not None:
            line = process.stdout.readline()
        if line:
            comm_thread.writeout(line)
        else:
            break

    if throw:
        if process.returncode != 0:
            args = []
            if hasattr(process, "args"):
                args = process.args
            raise subprocess.CalledProcessError(process.returncode, cmd=args)

    if comm_thread:
        for err in comm_thread.errors:  # pragma: cover if windows
            if isinstance(err, DockerExecError) or throw:
                raise err


def is_windows():
    return platform.system() == "Windows"


def is_linux():
    return platform.system() == "Linux"


def is_apple():
    return platform.system() == "Darwin"


def parse_timeout(text):
    """
    Decode a human-readable time to seconds.
    eg, 1h 30m

    default is minutes without any suffix
    """
    if isinstance(text, int):
        text = str(text)
    # collapse the long form
    text = text.replace(" hours", "h")
    text = text.replace(" minutes", "m")

    words = text.split()
    seconds = 0

    if len(words) == 1:
        # plain single time
        word = words[0]
        try:
            mins = float(word)
            # plain bare number, use it as minutes
            return int(60.0 * mins)
        except ValueError:
            pass

    pattern = re.compile(r"([\d.]+)\s*([hm])")

    for word in words:
        m = pattern.search(word)
        if m and m.groups():
            num, suffix = m.groups()
            num = float(num)
            if suffix == "h":
                if seconds > 0:
                    raise ValueError("Unexpected h value {}".format(text))
                seconds += num * 60 * 60
            elif suffix == "m":
                seconds += num * 60

    if seconds == 0:
        raise ValueError("Cannot decode timeout {}".format(text))
    return seconds


def git_worktree(path: str) -> Optional[str]:
    """
    If the given path contains a git worktree, return the path to it
    :param path:
    :return:
    """
    gitpath = os.path.join(path, ".git")

    if os.path.isfile(gitpath):  # pragma: no cover
        # this is an odd case where you have .git files instead of folders
        with open(gitpath, "r") as fd:
            full = fd.read()
            for line in full.splitlines():
                name, value = line.split(":", 1)
                if name == "gitdir":
                    value = value.strip()
                    realpath = value
                    # keep going upwards until we find a .git folder
                    for _ in value.split(os.sep):
                        realpath = os.path.dirname(realpath)
                        gitdir = os.path.join(realpath, ".git")
                        if os.path.isdir(gitdir):
                            return gitdir
    return None


def make_path_slug(text: str) -> str:
    """Convert a string into one suitable for a folder basename"""
    return re.sub(r"[^a-zA-Z0-9\-.]", "_", text)


def clean_leftovers():
    """Clean up any unused leftover docker containers or networks"""
    from .docker import DockerTool, DockerToolFailed
    tool = DockerTool()
    for container in tool.containers:  # pragma: no cover
        name = tool.container_name(container)
        pid = is_gle_resource(name)
        if pid is not None:
            if not resource_owner_alive(name):
                # kill this container
                info(f"Killing leftover docker container: {name}")
                tool.docker_call("kill", container)
    try:
        tool.docker_call("network", "rm", "gle-service-network")
    except DockerToolFailed:
        pass


class DockerVolume:
    def __init__(self, host, mount, mode):
        if host != "/":
            host = host.rstrip(os.sep)
        self.host = host
        self.mount = mount.rstrip(os.sep)
        assert mode in ["rw", "ro"]
        self.mode = mode

    def __str__(self):
        return f"{self.host}:{self.mount}:{self.mode}"


def plausible_docker_volume(text: str) -> Optional[DockerVolume]:
    """Decode a docker volume string or return None"""
    mode = "rw"
    parts = text.split(":")
    src = None
    mount = None
    if len(parts) >= 4:
        import ntpath
        # c:\thing:c:\container
        # c:\thing:c:\container[:mode]
        if len(parts) == 5:
            # has mode
            mode = parts[-1]
        src = ntpath.abspath(f"{parts[0]}:{parts[1]}")
        mount = ntpath.abspath(f"{parts[2]}:{parts[3]}")
    else:
        if len(parts) >= 2:
            import posixpath
            # /host/path:/mount/path[:mode]
            src = posixpath.abspath(parts[0])
            mount = posixpath.abspath(parts[1])
            if len(parts) == 3:
                mode = parts[2]
    if not src:
        return None
    return DockerVolume(src, mount, mode)


def sensitive_varname(name) -> bool:
    """Return True if the variable might be a sensitive/secret one"""
    for check in ["PASSWORD", "TOKEN", "PRIVATE"]:
        if check in name:
            return True
    return False


def trim_quotes(text: str) -> str:
    """If the string is wrapped in quotes, strip them off"""
    if text:
        if text[0] in ["'", "\""]:
            if text[0] == text[-1]:
                text = text[1:-1]
    return text


def powershell_escape(text: str, variables=False) -> str:  # pragma: cover if windows
    # taken from: http://www.robvanderwoude.com/escapechars.php
    text = text.replace("`", "``")
    text = text.replace("\a", "`a")
    text = text.replace("\b", "`b")
    text = text.replace("\f", "^f")
    text = text.replace("\r", "`r")
    text = text.replace("\n", "`n")
    text = text.replace("\t", "^t")
    text = text.replace("\v", "^v")
    text = text.replace("#", "`#")
    text = text.replace("'", "`'")
    text = text.replace("\"", "`\"")
    text = f"\"{text}\""
    if variables:
        text = text.replace("$", "`$")
        text = text.replace("``e", "`e")
    return text


def die(msg):
    """print an error and exit"""
    print("error: " + str(msg), file=sys.stderr)
    sys.exit(1)


def note(msg):
    """Print to stderr"""
    print(msg, file=sys.stderr, flush=True)


def git_uncommitted_changes(path: str) -> bool:
    """Return True if the given repo has uncommitted changes to tracked files"""
    topdir = git_top_level(path)
    output = subprocess.check_output(
        ["git", "-C", topdir, "status", "--porcelain", "--untracked=no"],
        encoding="utf-8", stderr=subprocess.DEVNULL).strip()
    for _ in output.splitlines(keepends=False):
        return True
    return False


def git_current_branch(path: str) -> str:
    """Get the current branch"""
    return subprocess.check_output(
        ["git", "-C", path, "rev-parse", "--abbrev-ref", "HEAD"], encoding="utf-8", stderr=subprocess.DEVNULL
    ).strip()


def git_commit_sha(path: str) -> str:
    """Get the current commit hash"""
    return subprocess.check_output(
        ["git", "-C", path, "rev-parse", "HEAD"], encoding="utf-8", stderr=subprocess.DEVNULL
    ).strip()


def git_remotes(path: str) -> List[str]:
    """Get the remote names of the given git repo"""
    try:
        output = subprocess.check_output(
            ["git", "-C", path, "remote"], encoding="utf-8", stderr=subprocess.DEVNULL)
        return list(output.splitlines(keepends=False))
    except subprocess.CalledProcessError:
        return []


def git_remote_url(path: str, remote: str) -> str:
    """Get the URL of the given git remote"""
    return subprocess.check_output(
        ["git", "-C", path, "remote", "get-url", remote], encoding="utf-8", stderr=subprocess.DEVNULL).strip()


def get_git_remote_urls(repo: str) -> Dict[str, str]:
    """Return all the git remotes defined in the given git repo"""
    remotes = git_remotes(repo)
    urls = {}
    for item in remotes:
        urls[item] = git_remote_url(repo, item)
    return urls


def git_top_level(repo: str) -> str:
    """Get the top folder of the git repo"""
    return subprocess.check_output(
        ["git", "-C", repo, "rev-parse", "--show-toplevel"], encoding="utf-8", stderr=subprocess.DEVNULL).strip()


def git_push_force_upstream(repo: str, remote: str, branch: str):  # pragma: no cover
    subprocess.check_call(["git", "-C", repo, "push", "--force", "-q", "--set-upstream", remote, branch])


def stringlist_if_string(value: Union[str, list]) -> list:
    """If value is a string, return a one element list, else return value"""
    if isinstance(value, str):
        return [value]
    return value


def remote_servers(remotes: Dict[str, str]) -> Dict[str, str]:
    """From a map of git remotes, Get a map of git remotes to server addresses"""
    servers: Dict[str, str] = {}
    for remote_name in remotes:
        remote_url = remotes[remote_name]
        if remote_url.startswith("git@") and remote_url.endswith(".git"):
            if ":" in remote_url:
                lhs, rhs = remote_url.split(":", 1)
                host = lhs.split("@", 1)[1]
                project_path = rhs.rsplit(".", 1)[0].lstrip("/")
                servers[remote_name] = f"{host}/{project_path}"
        elif "://" in remote_url and remote_url.startswith("http"):
            parsed = urlparse(remote_url)
            host = parsed.hostname
            project_path = parsed.path.rsplit(".", 1)[0].lstrip("/")
            servers[remote_name] = f"{host}/{project_path}"
    return servers


def has_rootless_docker() -> bool:
    """
    Return True if this system can run docker containers in rootless mode or
    if docker command is not found (assuming rootless emulator)
    """
    if not has_docker():
        return True
    stdout = subprocess.check_output(["docker", "info"], stderr=subprocess.STDOUT)
    try:
        stdout.strip().decode().index("rootless: true")
        debug("rootless docker detected")
        return True
    except ValueError:
        return False


def has_docker(docker_cli = "docker") -> bool:
    """
    Return True if this system can run docker containers
    :return:
    """
    # noinspection PyBroadException
    try:
        subprocess.check_output([docker_cli, "info"], stderr=subprocess.STDOUT)
        debug("docker detected")
        return True
    except Exception as err:  # pragma: no cover
        pass
    return False  # pragma: no cover


def warning(text: str) -> None:
    print(f"warning: {text}", file=sys.stderr, flush=True)


def notice(text: str) -> None:
    print(f"notice: {text}", file=sys.stderr, flush=True)


def setenv_string(text: str) -> Tuple[str, str]:
    parts = text.split("=", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    raise ValueError(f"{text} is not in the form NAME=VALUE")


class RuntimeGlobals:

    def __init__(self):
        self.output_thread_type: Optional[type] = ProcessLineProxyThread
        self.current_job: Optional[str] = None
        self.requested_jobs: List[str] = []
        self.session_start_time = 0
        self.job_start_time = 0
        self.reset()

    def reset(self):
        self.output_thread_type = ProcessLineProxyThread
        self.current_job = None
        self.requested_jobs = []
        self.session_start_time = time.monotonic()
        self.job_start_time = time.monotonic()

    def get_estimated_job_time_remaining(self) -> int:
        """Return an estimate for how many more seconds are left in the current job"""
        if self.current_job:
            job_time = get_duration(self.current_job)
            remaining = int(job_time - self.get_elasped_job_time())
            if remaining > 0:
                return remaining

        return 0

    def get_elapsed_session_time(self) -> int:
        """Return the number of seconds gle has been running this build session"""
        now = time.monotonic()
        return int(now - self.session_start_time)

    def get_elasped_job_time(self) -> int:
        """Return the number of seconds gle has been running this job"""
        now = time.monotonic()
        return int(now - self.job_start_time)


GLE_RUNTIME_GLOBALS = RuntimeGlobals()
