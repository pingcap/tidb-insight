# -*- coding: utf-8 -*-
# simple utilities

import argparse
import logging
import os
import sys
import time

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


def chdir(nwd):
    return os.chdir(nwd)


def is_abs_path(path):
    return os.path.isabs(path)

def run_cmd(cmd, shell=False):
    p = Popen(cmd, shell=shell, stdout=PIPE, stderr=PIPE)
    return p.communicate()


def run_cmd_for_a_while(cmd, duration, shell=False):
    p = Popen(cmd, shell=shell)
    time.sleep(duration)
    p.kill()


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
                                     epilog="Note that some arguments may decrease system performance.")
    parser.add_argument("-o", "--output", action="store", default=None,
                        help="The directory to store output data of TiDB Insight. Any existing file will be overwritten without futher confirmation.")
    parser.add_argument("--alias", action="store", default=None,
                        help="The alias of this instance. This value be part of the name of output tarball.")
    parser.add_argument("-c", "--compress", action="store_true", default=False,
                        help="Compress all output files to a tarball, disabled by default.")

    parser.add_argument("-p", "--perf", action="store_true", default=False,
                        help="Collect trace info using perf. Disabled by default.")
    parser.add_argument("--pid", type=int, action="append", default=None,
                        help="""PID of process to run perf on. If `-p`/`--perf` is not set, this value will not take effect. Multiple PIDs can be set by using more than one `--pid` argument. `None` by default which means the whole system.""")
    parser.add_argument("--proc-listen-port", action="store", type=int, default=None,
                        help="Collect perf data of process that listen on given port. This value will be ignored if `--pid` is set.")
    parser.add_argument("--proc-listen-proto", action="store", default=None,
                        help="Protocol type of listen port, available values are: tcp/udp. If not set, only TCP listening ports are checked.")
    parser.add_argument("--tidb-proc", action="store_true", default=False,
                        help="Collect perf data for PD/TiDB/TiKV processes instead of the whole system.")
    parser.add_argument("--perf-exec", type=int, action="store", default=None,
                        help="Custom path of perf executable file.")
    parser.add_argument("--perf-freq", type=int, action="store", default=None,
                        help="Event sampling frequency of perf-record, in Hz.")
    parser.add_argument("--perf-time", type=int, action="store", default=None,
                        help="Time period of perf recording, in seconds.")
    parser.add_argument("--perf-archive", action="store_true", default=False,
                        help="Run `perf archive` after collecting data, useful when reading data on another machine. Disabled by default.")

    parser.add_argument("-l", "--log", action="store_true", default=False,
                        help="Collect log files in output. PD/TiDB/TiKV logs are included by default.")
    parser.add_argument("--syslog", action="store_true", default=False,
                        help="Collect the system log in output. This may significantly increase output size. If `-l/--log` is not set, the system log will be ignored.")
    parser.add_argument("--log-auto", action="store_true", default=False,
                        help="Automatically detect and save log files of running PD/TiDB/TiKV processes.")
    parser.add_argument("--log-dir", action="store", default=None,
                        help="Location of log files. If `--log-auto` is set, this value will be ignored.")
    parser.add_argument("--log-prefix", action="store", default=None,
                        help="The prefix of log files, will be the directory name of all logs, will be in the name of output tarball. If `--log-auto` is set, this value will be ignored.")
    parser.add_argument("--log-retention", action="store", type=int, default=0,
                        help="The time of log retention, any log files older than given time period from current time will not be included. Value should be a number of hour(s) in positive interger. `0` by default and means no time check.")

    parser.add_argument("--config-file", action="store_true", default=False,
                        help="Collect various configuration files in output, disabled by default.")
    parser.add_argument("--config-auto", action="store_true", default=False,
                        help="Automatically detect and save configuration files for all running PD/TiDB/TiKV processes.")
    parser.add_argument("--config-sysctl", action="store_true", default=False,
                        help="Save kernel config by collecting output of `sysctl -a`.")
    parser.add_argument("--config-dir", action="store", default=None,
                        help="Location of config files. If `--config-auto` is set, this value will be ingored.")
    parser.add_argument("--config-prefix", action="store", default=None,
                        help="The prefix of config files, will be directory name of all config files, will be in the name of output tarball. If `--config-auto` is set, the value will be ignored.")

    parser.add_argument("--pdctl", action="store_true", default=False,
                        help="Enable collecting data from PD API. Disabled by default.")
    parser.add_argument("--pd-host", action="store", default=None,
                        help="The host of the PD server. `localhost` by default.")
    parser.add_argument("--pd-port", type=int, action="store", default=None,
                        help="The port of PD API service, `2379` by default.")
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="Print verbose output.")

    parser.add_argument("-f", "--ftrace", action="store_true", default=False,
                        help="Collect trace info using ftrace. Disabled by default.")
    parser.add_argument("--ftracepoint",  action="store", default=None,
                        help="Tracepoint to be traced (only support to trace direct reclaim latency).")
    parser.add_argument("--ftrace-time", type=int, action="store", default=None,
                        help="Time period of ftrace recording, in seconds (default 60s).")
    parser.add_argument("--ftrace-bufsize", action="store", default=None,
                        help="Ftrace ring buffer size in kb (default 4096 kb).")

    parser.add_argument("--vmtouch", action="store_true", default=False,
                        help="Collect page cache info using vmtouch. Disabled by default.")
    parser.add_argument("--vmtouch-target", action="store", default=None,
                        help="File or dir to be diagnosed.")

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
        logging.debug("Requesting URL: %s" % url)
        response = urlreq.urlopen(url, data)
        return response.read()
    except HTTPError as e:
        logging.debug("HTTP Error: %s" % e.read())
        return e.read()
    except URLError as e:
        logging.warning("Reading URL %s error: %s" % (url, e))
        return None


def get_hostname():
    # This function is merely used, so only import socket package when necessary
    import socket
    return socket.gethostname()

def python_version():
    # get a numeric Python version
    return sys.version_info[0] + sys.version_info[1] * 0.1
