#!/usr/bin/python3
import os
import time
import argparse
import subprocess

parser = argparse.ArgumentParser(
    description="Change all files in the current working directory to be owned by the given UID/GID")
parser.add_argument("UID", type=int, help="UID to set")
parser.add_argument("GID", type=int, help="GID to set")
parser.add_argument("PATH", type=str)


def run(args=None):  # pragma: cover if posix
    opts = parser.parse_args(args=args)
    started = time.time()
    os.chdir(opts.PATH)
    cmdline = ["chown", "-R", "-h", f"{str(opts.UID)}.{str(opts.GID)}", "."]
    print(f"Restoring ownership of {os.getcwd()} to {str(opts.UID)}.{str(opts.GID)}..")
    subprocess.check_call(cmdline, shell=False)
    ended = time.time()
    print(f"Ownerships restored ({int(ended - started)} sec).")


if __name__ == "__main__":
    run()
