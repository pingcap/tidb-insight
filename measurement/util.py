# -*- coding: utf-8 -*-
# simple utilities

import argparse
import logging
import os

from subprocess import Popen, PIPE


def read_file(filename):
    data = None
    with open(filename, 'r') as f:
        data = f.read()
    f.close()
    return data


def write_file(filename, data):
    with open(filename, 'w') as f:
        try:
            f.write(str(data, 'utf-8'))
        except TypeError:
            f.write(data)
    f.close()


def is_root_privilege():
    return os.getuid() == 0


def create_dir(path):
    try:
        os.mkdir(path)
        return path
    except OSError as e:
        # There is FileExistsError (devided from OSError) in Python 3.3+,
        # but only OSError in Python 2, so we use errno to check if target
        # dir already exists.
        import errno
        if e.errno == errno.EEXIST and os.path.isdir(path):
            return path
        else:
            logging.fatal("Can not prepare output dir, error is: %s" % str(e))
            exit(e.errno)
    return None


# full directory path of this script
def pwd():
    return os.path.dirname(os.path.realpath(__file__))


# full path of current working directory
def cwd():
    return os.getcwd()


def run_cmd(cmd):
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    return p.communicate()


def parse_cmdline(cmdline):
    result = {}
    try:
        cmd = cmdline.split()
    except TypeError:
        return None
    for arg in cmd:
        # parse args that start with '--something'
        if arg.startswith("--"):
            argkv = arg.split("=")
            try:
                result[argkv[0][2:]] = argkv[1]
            except IndexError:
                pass
    return result


def parse_insight_opts():
    parser = argparse.ArgumentParser(description="TiDB Insight Scripts",
                                     epilog="Note that some options would decrease system performance.")
    parser.add_argument("-o", "--output", action="store", default=None,
                        help="""The dir to store output data of TiDB Insight, any existing file
                        will be overwritten without futher confirmation.""")

    parser.add_argument("-p", "--perf", action="store_true", default=False,
                        help="Collect trace info with perf. Default is disabled.")
    parser.add_argument("--pid", type=int, action="append", default=None,
                        help="""PID of process to run perf on, if '-p/--perf' is not set, this
                        value will be ignored and would not take any effection.
                        Multiple PIDs can be set by using more than one --pid args.
                        Default is None and means the whole system.""")
    parser.add_argument("--tidb-proc", action="store_true", default=False,
                        help="Collect perf data for PD/TiDB/TiKV processes instead of the whole system.")
    parser.add_argument("--perf-exec", type=int, action="store", default=None,
                        help="Custom path of perf executable file.")
    parser.add_argument("--perf-freq", type=int, action="store", default=None,
                        help="Event sampling frequency of perf-record, in Hz.")
    parser.add_argument("--perf-time", type=int, action="store", default=None,
                        help="Time period of perf recording, in seconds.")
    parser.add_argument("-l", "--log", action="store_true", default=False,
                        help="Enable to include log files in output, PD/TiDB/TiKV logs are included by default.")
    parser.add_argument("--syslog", action="store_true", default=False,
                        help="Enable to include system log in output, will be ignored if -l/--log is not set.")

    return parser.parse_args()
