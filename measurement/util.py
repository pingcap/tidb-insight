# -*- coding: utf-8 -*-
# simple utilities

import argparse
import logging
import os

from subprocess import Popen, PIPE
try:
    # For Python 2
    import urllib2 as urlreq
    from urllib2 import HTTPError, URLError
except ImportError:
    # For Python 3
    import urllib.request as urlreq
    from urllib.error import HTTPError, URLError


def is_root_privilege():
    return os.getuid() == 0


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
                        help="Enable to include system log in output, will be ignored if -l/--log is not set. This may significantly increase output size.")
    parser.add_argument("--config-file", action="store_true", default=False,
                        help="Enable to include various config files in output, disabled by default.")
    parser.add_argument("--pd-host", action="store", default=None,
                        help="The host of PD server. Default to localhost.")
    parser.add_argument("--pd-port", type=int, action="store", default=None,
                        help="The port of PD API service, default to 2379.")

    return parser.parse_args()


def get_init_type():
    try:
        init_exec = os.readlink("/proc/1/exe")
    except OSError:
        logging.warning("Unable to detect init type, am I running with root?")
        return None
    return init_exec.split("/")[-1]


def read_url(url, data=None):
    if not url or url == "":
        return None

    try:
        response = urlreq.urlopen(url, data)
        return response.read()
    except HTTPError as e:
        return e.read()
    except URLError as e:
        logging.critical("Reading URL %s error: %s" % (url, e))
        return None
