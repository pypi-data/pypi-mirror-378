import re
import subprocess
import sys
import os
import argparse
import time
from typing import Dict, Any, Optional

import gitlabemu.errors
from . import configloader
from .docker import DockerJob
from .gitlab_client_api import PipelineError, PipelineInvalid, PipelineNotFound, posix_cert_fixup
from .jobs import Job
from .jobtypes import JobFactory, ScriptJobFactory
from .localfiles import restore_path_ownership
from .helpers import (is_linux, is_windows,
                      git_worktree, clean_leftovers,
                      die, note, has_rootless_docker,
                      GLE_RUNTIME_GLOBALS, PrettyProcessLineProxyThread)
from .localstats import put_duration
from .logmsg import debugrule, enable_rule_debug, info
from .pipelines import pipelines_cmd, generate_pipeline, print_pipeline_jobs, export_cmd
from .userconfig import USER_CFG_ENV, get_user_config_context
from .userconfigdata import UserContext
from .glp.types import Match
from .yamlloader import ordered_dump

CONFIG_DEFAULT = ".gitlab-ci.yml"

parser = argparse.ArgumentParser(prog="{} -m gitlabemu".format(os.path.basename(sys.executable)))
list_mutex = parser.add_mutually_exclusive_group()
list_mutex.add_argument("--list", "-l", dest="LIST", default=False,
                        action="store_true",
                        help="List runnable jobs")
parser.add_argument("--version", default=False, action="store_true")
parser.add_argument("--hidden", default=False, action="store_true",
                    help="Show hidden jobs in --list(those that start with '.')")
parser.add_argument("--noop", "-n", default=False, action="store_true",
                    help="Execute a pipeline but print each command instead of running")
list_mutex.add_argument("--full", "-r", dest="FULL", default=False,
                        action="store_true",
                        help="Run any jobs that are dependencies")
parser.add_argument("--config", "-c", dest="CONFIG", default=CONFIG_DEFAULT,
                    type=str,
                    help="Use an alternative gitlab yaml file")
parser.add_argument("--settings", "-s", dest="USER_SETTINGS", type=str, default=None,
                    help="Load gitlab emulator settings from a file")
parser.add_argument("--chdir", "-C", dest="chdir", default=None, type=str, metavar="DIR",
                    help="Change to this directory before running")

run_mutex = parser.add_mutually_exclusive_group()
run_mutex.add_argument("--enter", "-i", dest="enter_shell", default=False, action="store_true",
                    help="Run an interactive shell but do not run the build"
                    )
run_mutex.add_argument("--exec", default=False, action="store_true",
                    help="Execute the job using 'gitlab-runner exec' if possible. Note, this "
                         "feature is experimental")
parser.add_argument("--pretty", "-t", default=False, action="store_true",
                    help="Run with a more pretty output and status display - for non-script use only")

parser.add_argument("--before-script", "-b", dest="only_before_script", default=False,
                    action="store_true",
                    help="Run only the 'before_script' commands"
                    )
parser.add_argument("--image", type=str, default=None,
                    help="Replace the 'image'. Can be used to force running a shell job in a container or to change "
                         "the container a job uses")
parser.add_argument("--timeout", type=int, default=None,
                    help="Set/unset a timeout (minutes). set to 0 to disable timeouts")
parser.add_argument("--user", "-u", dest="shell_is_user", default=False, action="store_true",
                    help="Run the interactive shell as the current user instead of root (non-windows only)")

parser.add_argument("--shell-on-error", "-e", dest="error_shell", type=str,
                    help="If a docker job fails, execute this process (can be a shell)")

parser.add_argument("--ignore-docker", dest="no_docker", action="store_true", default=False,
                    help="If set, run jobs using the local system as a shell job instead of docker"
                    )
parser.add_argument("--gen-script", dest="gen_script", choices=["sh", "powershell"], default=None,
                    help="Generate a sh or powershell script to execute a job without gle")

parser.add_argument("--docker-pull", dest="docker_pull", type=str,
                    choices=["always", "if-not-present", "never"],
                    default=None,
                    help="Force set the docker pull policy")

parser.add_argument("--debug-rules", default=False, action="store_true",
                    help="Print log messages relating to include and job rule processing")
parser.add_argument("--var", dest="var", type=str, default=[], action="append",
                    help="Set a pipeline variable, eg DEBUG or DEBUG=1")

parser.add_argument("--revar", dest="revars", metavar="REGEX", type=str, default=[], action="append",
                    help="Set pipeline variables that match the given regex")

parser.add_argument("--parallel", type=str,
                    help="Run JOB as one part of a parallel axis (eg 2/4 runs job 2 in a 4 parallel matrix)")

parser.add_argument("--pipeline", default=False, action="store_true",
                    help="Run JOB on or list pipelines from a gitlab server")

parser.add_argument("--from", type=str, dest="FROM",
                    metavar="SERVER/PROJECT/PIPELINE",
                    help="Fetch needed artifacts for the current job from "
                         "the given pipeline, eg server/grp/project/41881, "
                         "=master, 23156")

list_mutex.add_argument("--download", default=False, action="store_true",
                        help="Instead of building JOB, download the artifacts of JOB from gitlab (requires --from)")

list_mutex.add_argument("--export", type=str, dest="export", metavar="EXPORT",
                        help="Download JOB logs and artifacts to EXPORT/JOBNAME (requires --from)")

parser.add_argument("--completed", default=False, action="store_true",
                    help="Show all currently completed jobs in the --from pipeline or all "
                         "completed pipelines with --pipeline --list")

parser.add_argument("--match", default=None, type=Match,
                    metavar="X=Y",
                    help="when using --pipeline with --list or --cancel, filter the results with this expression")

parser.add_argument("--insecure", "-k", dest="insecure", default=False, action="store_true",
                    help="Ignore TLS certificate errors when fetching from remote servers")

list_mutex.add_argument("--clean", dest="clean", default=False, action="store_true",
                        help="Clean up any leftover docker containers or networks")
list_mutex.add_argument("--cancel", default=False, action="store_true",
                        help="Cancel pipelines that match --match x=y, (requires --pipeline)")


if is_windows():  # pragma: cover if windows
    shellgrp = parser.add_mutually_exclusive_group()
    shellgrp.add_argument("--powershell",
                          dest="windows_shell",
                          action="store_const",
                          const="powershell",
                          help="Force use of powershell for windows jobs (default)")
    shellgrp.add_argument("--cmd", default=None,
                          dest="windows_shell",
                          action="store_const",
                          const="cmd",
                          help="Force use of cmd for windows jobs")

parser.add_argument("JOB", type=str, default=None,
                    nargs="?",
                    help="Run this named job")

parser.add_argument("EXTRA_JOBS", type=str,
                    nargs="*",
                    help=argparse.SUPPRESS)


def apply_user_config(loader: configloader.Loader, is_docker: bool):
    """
    Add the user config values to the loader
    :param loader:
    :param is_docker:
    :return:
    """
    ctx: UserContext = get_user_config_context()
    if ".gle-extra_variables" not in loader.config:
        loader.config[".gle-extra_variables"] = {}

    for name in ctx.variables:
        loader.config[".gle-extra_variables"][name] = ctx.variables[name]


def gitlab_runner_exec(jobobj: Job):
    """Execute a job locally using 'gitlab-runner exec"""
    loader = configloader.Loader()
    loader.config.update(jobobj.copy_config())

    result = generate_pipeline(loader, jobobj.name,
                               dump_only=True,
                               use_from=None,
                               tls_verify=True)

    # ensure that all variables are strings as gitlab-runner exec doesnt like the ints used for KUBERNETES settings
    def ensure_strings(dictionary: dict):
        copied = dict(dictionary)
        for varname in copied:
            dictionary[varname] = str(copied[varname])
    if "variables" in result:
        ensure_strings(result["variables"])

    for name in result:
        if isinstance(result[name], dict):
            if "variables" in result[name]:
                ensure_strings(result[name]["variables"])

    # save the config
    temp_pipeline_file = os.path.join(os.getcwd(), ".temp-pipeline.yml")
    try:
        with open(temp_pipeline_file, "w") as tempcfg:
            tempcfg.write(ordered_dump(result))
        cmdline = ["gitlab-runner", "exec"]
        repo_dir = os.getcwd()
        repo_parent = os.path.dirname(repo_dir)

        if isinstance(jobobj, DockerJob):
            cmdline.append("docker")
            # volume trickery, as our repo will be mounted r/o
            rebind_volume = f"{repo_parent}:/builds:rw"
            repo_parent = "/builds"
            repo_dir = os.path.join(repo_parent, os.path.basename(repo_dir))
            cmdline.extend(["--docker-volumes", rebind_volume])
            cmdline.extend(["--pre-build-script", f"git config --global --add safe.directory {repo_dir}"])
        else:
            cmdline.append("shell")

        cmdline.extend(["--cicd-config-file", temp_pipeline_file,
                        "--env", "GIT_STRATEGY=none",
                        "--env", f"GIT_CLONE_PATH={repo_dir}",
                        "--custom_build_dir-enabled",
                        "--builds-dir", repo_parent,
                        jobobj.name])
        info(f"Running {' '.join(cmdline)}")
        subprocess.check_call(cmdline)

    finally:
        os.unlink(temp_pipeline_file)


def execute_job(config: Dict[str, Any],
                jobname: str,
                seen=None,
                recurse=False,
                use_runner=False,
                noop=False,
                options: Optional[Dict[str, Any]] = None,
                overrides: Optional[Dict[str, Any]] = None,
                jobfactory: Optional[JobFactory] = None,
                chown=True,
                pretty=False,
                ):
    """
    Run a job, optionally run required dependencies
    :param jobfactory:
    :param config: the config dictionary
    :param jobname: the job to start
    :param seen: completed jobs are added to this set
    :param recurse: if True, execute in dependency order
    :param use_runner: if True, execute using "gitlab-runner exec"
    :param noop: if True, print instead of execute commands
    :param options: If given, set attributes on the job before use.
    :param overrides: If given, replace properties in the top level of a job dictionary.
    :param chown: If True and if using docker, attempt to restore the folder ownership.
    :param pretty: If True, print output in a more visually friendly way
    :return:
    """

    if seen is None:
        seen = set()
    if jobname not in seen:
        jobobj = configloader.load_job(config, jobname, overrides=overrides, jobfactory=jobfactory)
        if options:
            for name in options:
                setattr(jobobj, name, options[name])

        if pretty and not use_runner:
            GLE_RUNTIME_GLOBALS.output_thread_type = PrettyProcessLineProxyThread

        if recurse:
            for need in jobobj.dependencies:
                execute_job(config, need, seen=seen, recurse=True, noop=noop, jobfactory=jobfactory, chown=chown)
        print(f">>> execute {jobobj.name}:", file=sys.stderr)

        if noop:
            if isinstance(jobobj, DockerJob):
                print(f"image: {jobobj.docker_image}")
            for envname, envvalue in jobobj.get_envs().items():
                print(f"setenv {envname}={envvalue}")

            for line in jobobj.before_script + jobobj.script:
                print(f"script {line}")
        else:
            started_time = time.monotonic()
            GLE_RUNTIME_GLOBALS.current_job = jobobj
            GLE_RUNTIME_GLOBALS.job_start_time = started_time

            try:
                if use_runner:
                    gitlab_runner_exec(jobobj)
                else:
                    jobobj.run()
            finally:
                if chown:
                    restore_path_ownership(os.getcwd())

            put_duration(jobname, int(time.monotonic() - started_time))
        seen.add(jobname)


def do_pipeline(options: argparse.Namespace, loader):
    """Run/List/Cancel gitlab pipelines in the current project"""
    matchers = {}
    if options.completed:
        matchers["status"] = "success"

    if options.match:
        matchers[options.match.name] = options.match.value

    elif options.cancel:
        die("--pipeline --cancel requires --match x=y")

    jobs = []
    if options.JOB:
        jobs.append(options.JOB)
    jobs.extend(options.EXTRA_JOBS)

    note("notice! `gle --pipeline' is deprecated in favor of `glp'")
    if not jobs:
        return pipelines_cmd(tls_verify=not options.insecure,
                             matchers=matchers,
                             do_cancel=options.cancel,
                             do_list=options.LIST)

    return generate_pipeline(loader, *jobs,
                             use_from=options.FROM,
                             tls_verify=not options.insecure)


def do_gitlab_from(options: argparse.Namespace, loader):
    """Perform actions using a gitlab server artifacts"""
    from .gitlab_client_api import get_pipeline
    from .gitlab_client_api import do_gitlab_fetch

    if options.download and not options.FROM:
        die("--download requires --from PIPELINE")
    if options.FROM:
        try:
            if options.LIST:
                # print the jobs in the pipeline
                gitlab, project, pipeline = get_pipeline(options.FROM, secure=not options.insecure)
                if not pipeline:
                    raise PipelineInvalid(options.FROM)
                print_pipeline_jobs(pipeline, completed=options.completed)
            elif options.export:
                # export a pipeline
                note(f"Export full '{options.FROM}' pipeline")
                export_cmd(options.FROM,
                           options.export,
                           tls_verify=not options.insecure,
                           )
            elif options.JOB:
                # download a job, or artifacts needed by a job
                jobobj: Job = configloader.load_job(loader.config, options.JOB)
                if options.download:
                    # download a job's artifacts
                    if options.parallel:
                        download_jobs = [f"{options.JOB} {options.parallel}/{jobobj.parallel}"]
                    else:
                        download_jobs = [options.JOB]
                    note(f"Download '{download_jobs[0]}' artifacts")
                else:
                    # download jobs needed by a job
                    note(f"Download artifacts required by '{options.JOB}'")
                    download_jobs = jobobj.dependencies

                # download what we need
                outdir = os.getcwd()
                do_gitlab_fetch(options.FROM,
                                download_jobs,
                                tls_verify=not options.insecure,
                                download_to=outdir)
            else:
                die("--from PIPELINE requires JOB or --export")
        except PipelineNotFound:
            die(str(PipelineNotFound(options.FROM)))
        except PipelineError as error:
            die(str(error))


def get_version():
    dist = "gitlab-emulator"
    try:
        import importlib.metadata
        return importlib.metadata.distribution(dist).version
    except ImportError:
        pass

    try:
        # python 3.7 and earlier
        import pkg_resources
        try:
            return pkg_resources.get_distribution(dist).version
        except pkg_resources.DistributionNotFound:
            return "local"
    except ImportError:
        pass
    return "unknown"


def do_version():
    """Print the current package version"""
    ver = get_version()
    print(ver)
    sys.exit(0)


def get_loader(variables: Dict[str, str], **kwargs) -> configloader.Loader:
    loader = configloader.Loader(**kwargs)
    apply_user_config(loader, is_docker=False)
    for name in variables:
        loader.config[".gle-extra_variables"][name] = str(variables[name])
    return loader


def run(args=None):
    options = parser.parse_args(args)
    yamlfile = options.CONFIG
    jobname = options.JOB

    variables = {}

    if options.debug_rules:
        enable_rule_debug()

    if options.version:
        do_version()

    if options.clean:
        clean_leftovers()
        sys.exit()

    if options.chdir:
        if not os.path.exists(options.chdir):
            die(f"Cannot change to {options.chdir}, no such directory")
        os.chdir(options.chdir)

    if not os.path.exists(yamlfile):
        note(f"{configloader.DEFAULT_CI_FILE} not found.")
        find = configloader.find_ci_config(os.getcwd())
        if find:
            topdir = os.path.abspath(os.path.dirname(find))
            note(f"Found config: {find}")
            die(f"Please re-run from {topdir}")
        sys.exit(1)

    if options.USER_SETTINGS:
        os.environ[USER_CFG_ENV] = options.USER_SETTINGS

    for item in options.revars:
        patt = re.compile(item)
        for name in os.environ:
            if patt.search(name):
                variables[name] = os.environ.get(name)

    for item in options.var:
        var = item.split("=", 1)
        if len(var) == 2:
            name, value = var[0], var[1]
        else:
            name = var[0]
            value = os.environ.get(name, None)

        if value is not None:
            variables[name] = value

    ctx = get_user_config_context()
    fullpath = os.path.abspath(yamlfile)
    rootdir = os.path.dirname(fullpath)
    os.chdir(rootdir)
    loader = get_loader(variables)
    hide_dot_jobs = not options.hidden
    try:
        if options.pipeline or options.FROM:
            loader = get_loader(variables, emulator_variables=False)
            loader.load(fullpath)
            with posix_cert_fixup():
                if options.pipeline:
                    do_pipeline(options, loader)
                    return

                if options.FULL and options.parallel:
                    die("--full and --parallel cannot be used together")

                if options.FROM:
                    do_gitlab_from(options, loader)
                    return
        else:
            loader.load(fullpath)
    except gitlabemu.jobs.NoSuchJob as err:
        die(f"Job error: {err}")
    except gitlabemu.errors.ConfigLoaderError as err:
        die(f"Config error: {err}")

    if is_windows():  # pragma: cover if windows
        windows_shell = "powershell"
        if ctx.windows.cmd:
            windows_shell = "cmd"
        if options.windows_shell:
            # command line option given, use that
            windows_shell = options.windows_shell
        loader.config[".gitlabemu-windows-shell"] = windows_shell

    if options.LIST:
        for jobname in sorted(loader.get_jobs()):
            if jobname.startswith(".") and hide_dot_jobs:
                continue
            job = loader.load_job(jobname)
            if job.check_skipped():
                debugrule(f"{jobname} skipped by rules: {job.skipped_reason}")
            print(jobname)
    elif not jobname:
        parser.print_usage()
        sys.exit(1)
    else:
        jobs = sorted(loader.get_jobs())
        if jobname not in jobs:
            die(f"No such job {jobname}")
        job_options = {}

        if options.parallel:
            if loader.config[jobname].get("parallel", None) is None:
                die(f"Job {jobname} is not a parallel enabled job")

            pindex, ptotal = options.parallel.split("/", 1)
            pindex = int(pindex)
            ptotal = int(ptotal)
            if pindex < 1:
                die("CI_NODE_INDEX must be > 0")
            if ptotal < 1:
                die("CI_NODE_TOTAL must be > 1")
            if pindex > ptotal:
                die("CI_NODE_INDEX must be <= CI_NODE_TOTAL, (got {}/{})".format(pindex, ptotal))

            loader.config[".gitlabemu-parallel-index"] = pindex
            loader.config[".gitlabemu-parallel-total"] = ptotal

        fix_ownership = not has_rootless_docker()
        if options.no_docker:
            loader.config["hide_docker"] = True
            fix_ownership = False

        docker_job = loader.get_docker_image(jobname)
        apply_docker_config = False
        if docker_job:
            apply_docker_config = True
            if options.docker_pull is not None:
                job_options["docker_pull_policy"] = options.docker_pull
            gwt = git_worktree(rootdir)
            if gwt:  # pragma: no cover
                note(f"f{rootdir} is a git worktree, adding {gwt} as a docker volume.")
                # add the real git repo as a docker volume
                volumes = ctx.docker.runtime_volumes()
                volumes.append(f"{gwt}:{gwt}:ro")
                ctx.docker.volumes = volumes
        else:
            fix_ownership = False

        overrides = {}
        if options.image:
            overrides["image"] = options.image
        if options.timeout:
            if options.timeout == 0:
                overrides["timeout"] = None
            else:
                overrides["timeout"] = options.timeout

        apply_user_config(loader, is_docker=apply_docker_config)

        if not is_linux():
            fix_ownership = False

        if options.enter_shell:
            if options.FULL:
                die("-i is not compatible with --full")

        if options.only_before_script:
            job_options["script"] = []
            job_options["after_script"] = []

        if options.enter_shell:  # pragma: no cover
            overrides["timeout"] = None
            job_options["enter_shell"] = True
            if not options.only_before_script:
                job_options["before_script"] = []
                job_options["script"] = []

        if options.shell_is_user and not is_windows():
            job_options["shell_is_user"] = True
        loader.config["ci_config_file"] = os.path.relpath(fullpath, rootdir)

        if options.error_shell:  # pragma: no cover
            job_options["error_shell"] = [options.error_shell]
            overrides["timeout"] = None

        jobfactory = JobFactory()
        if options.gen_script:
            jobfactory = ScriptJobFactory()

        GLE_RUNTIME_GLOBALS.reset()

        executed_jobs = set()
        execute_job(loader.config, jobname,
                    seen=executed_jobs,
                    use_runner=options.exec,
                    recurse=options.FULL,
                    noop=options.noop,
                    options=job_options,
                    overrides=overrides,
                    jobfactory=jobfactory,
                    chown=fix_ownership,
                    pretty=options.pretty,
                    )

        if not options.gen_script:
            print("Build complete!")
