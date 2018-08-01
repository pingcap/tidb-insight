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
    except (TypeError, AttributeError):
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
    parser = argparse.ArgumentParser(description="TiDB Insight Scripts, collect various diagnosis data.",
                                     epilog="Note that some arguments may decrease system performance.")
    parser.add_argument("-o", "--output", action="store", default=None,
                        help="The directory to store output data of TiDB Insight. Any existing file will be overwritten without futher confirmation.")
    parser.add_argument("--alias", action="store", default=get_hostname(),
                        help="The alias of this instance. This value be part of the name of output tarball.")
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="Print verbose output.")

    subparsers = parser.add_subparsers(dest="subcmd")

# Sub-command: compress
    parser_compress = subparsers.add_parser(
        "archive", help="Compress all output files to a tarball.")
    parser_compress.add_argument(
        "-x", "--extract", action="store_true", default=False, help="Extract compressed data.")
    parser_compress.add_argument(
        "--dir", help="Location of compressed data, all tarballs under directory will be extracted.")

# Sub-command: system
    parser_system = subparsers.add_parser(
        "system", help="Collect various system information.")
    parser_system.add_argument("--collector", action="store_true", default=False,
                               help="Run `collector`, which collects basic information of system, if `--log-auto` or `--config-auto` is set, collector will be called as well. Disabled by default.")

# Sub-command: runtime
    parser_runtime = subparsers.add_parser(
        "runtime", help="Collect various runtime information.")
    subparsers_runtime = parser_runtime.add_subparsers(dest="subcmd_runtime")
    parser_perf = subparsers_runtime.add_parser(
        "perf", help="Collect trace info using perf.")
    parser_perf.add_argument("--pid", type=int, action="append", default=None,
                             help="""PID of process to run perf on. If `-p`/`--perf` is not set, this value will not take effect. Multiple PIDs can be set by using more than one `--pid` argument. `None` by default which means the whole system.""")
    parser_perf.add_argument("--listen-port", action="store", type=int, default=None,
                             help="Collect perf data of process that listen on given port. This value will be ignored if `--pid` is set.")
    parser_perf.add_argument("--listen-proto", action="store", default=None,
                             help="Protocol type of listen port, available values are: tcp/udp. If not set, only TCP listening ports are checked.")
    parser_perf.add_argument("--auto", action="store_true", default=False,
                             help="Collect perf data for PD/TiDB/TiKV processes instead of the whole system.")
    parser_perf.add_argument("--freq", type=int, action="store", default=None,
                             help="Event sampling frequency of perf-record, in Hz.")
    parser_perf.add_argument("--time", type=int, action="store", default=None,
                             help="Time period of perf recording, in seconds.")
    parser_perf.add_argument("--archive", action="store_true", default=False,
                             help="Run `perf archive` after collecting data, useful when reading data on another machine. Disabled by default.")

    parser_ftrace = subparsers_runtime.add_parser(
        "ftrace", help="Collect trace info using ftrace.")
    parser_ftrace.add_argument("--ftracepoint", action="store", default=None,
                               help="Tracepoint to be traced, only support Direct Reclaim Latency now. (`--ftracepoint dr`)")
    parser_ftrace.add_argument("--time", type=int, action="store", default=None,
                               help="Time period of ftrace recording, in seconds (default 60s).")
    parser_ftrace.add_argument("--bufsize", action="store", default=None,
                               help="Ftrace ring buffer size in kb (default 4096 kb).")

    parser_vmtouch = subparsers_runtime.add_parser(
        "vmtouch", help="Collect page cache info using vmtouch.")
    parser_vmtouch.add_argument("--target", action="store", default=None,
                                help="File or dir to be diagnosed.")

    parser_blktrace = subparsers_runtime.add_parser(
        "blktrace", help="Collect traces of the i/o traffic on block devices by blktrace.")
    parser_blktrace.add_argument("--target", action="store", default=None,
                                 help="The device to trace")
    parser_blktrace.add_argument("--time", type=int, action="store", default=None,
                                 help="Time period of blktrace recording, in seconds (default 60s).")
####

# Sub-command: log
    parser_log = subparsers.add_parser(
        "log", help="Collect log files in output. PD/TiDB/TiKV logs are included by default.")
    parser_log.add_argument("--syslog", action="store_true", default=False,
                            help="Collect the system log in output. This may significantly increase output size. If `-l/--log` is not set, the system log will be ignored.")
    parser_log.add_argument("--auto", action="store_true", default=False,
                            help="Automatically detect and save log files of running PD/TiDB/TiKV processes.")
    parser_log.add_argument("--dir", action="store", default=None,
                            help="Location of log files. If `--log-auto` is set, this value will be ignored.")
    parser_log.add_argument("--prefix", action="store", default=None,
                            help="The prefix of log files, will be the directory name of all logs, will be in the name of output tarball. If `--log-auto` is set, this value will be ignored.")
    parser_log.add_argument("--retention", type=int, action="store", default=0,
                            help="The time of log retention, any log files older than given time period from current time will not be included. Value should be a number of hour(s) in positive interger. `0` by default and means no time check.")
####

# Sub-command: config
    parser_config = subparsers.add_parser(
        "config", help="Collect various configuration files in output")
    parser_config.add_argument("--auto", action="store_true", default=False,
                               help="Automatically detect and save configuration files for all running PD/TiDB/TiKV processes.")
    parser_config.add_argument("--sysctl", action="store_true", default=False,
                               help="Save kernel config by collecting output of `sysctl -a`.")
    parser_config.add_argument("--dir", action="store", default=None,
                               help="Location of config files. If `--config-auto` is set, this value will be ingored.")
    parser_config.add_argument("--prefix", action="store", default=None,
                               help="The prefix of config files, will be directory name of all config files, will be in the name of output tarball. If `--config-auto` is set, the value will be ignored.")
####

# Sub-command: tidb
    parser_tidb = subparsers.add_parser(
        "tidb", help="Collect various information of running TiDB/TiKV/PD services.")
    subparsers_tidb = parser_tidb.add_subparsers(dest="subcmd_tidb")
    parser_pdctl = subparsers_tidb.add_parser(
        "pdctl", help="Collect data from PD's control API.")
    parser_pdctl.add_argument("--host", action="store", default=None,
                              help="The host of the PD server. `localhost` by default.")
    parser_pdctl.add_argument("--port", type=int, action="store", default=None,
                              help="The port of PD API service, `2379` by default.")
####

# Sub-command: metric
    parser_metric = subparsers.add_parser(
        "metric", help="Collect metric data from monitoring systems.")
    subparser_metric = parser_metric.add_subparsers(dest="subcmd_metric")
    parser_prom = subparser_metric.add_parser(
        "prom", help="Collect data from Prometheus API.")
    parser_prom.add_argument("--host", action="store", default=None,
                             help="The host of Prometheus API, `localhost` by default.")
    parser_prom.add_argument("--port", type=int, action="store", default=None,
                             help="The port of Prometheus API, `9090` by default.")
    parser_prom.add_argument("--retention", type=float, action="store", default=None,
                             help="Collect metric of past N hours, N=2 by default. If `--retention` is set, `--start` and `--end` will be ignored.")
    parser_prom.add_argument("--start", action="store", default=None,
                             help="Start timestamp of time range, format: '%%Y-%%m-%%d %%H:%%M:%%S' (local time).")
    parser_prom.add_argument("--end", action="store", default=None,
                             help="End timestamp of time range, format: '%%Y-%%m-%%d %%H:%%M:%%S' (local time).")
    parser_prom.add_argument("--resolution", type=float, default=None,
                             help="Query resolution step width of Prometheus in seconds, 15.0 by default.")
####

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


def parse_timestamp(time_string):
    # if it's already a numeric timestamp, just return it
    try:
        if time_string.isdigit():
            return int(time_string)
    except (AttributeError, ValueError):
        pass
    format_guess = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H",
        "%Y-%m-%d",
        "%m-%d",
        "%H:%M:%S",
        "%H:%M",
        "%H"
    ]
    for time_format in format_guess:
        try:
            # Convert to timestamp (in seconds)
            return time.mktime(time.strptime(time_string, time_format))
        except ValueError:
            pass
    raise ValueError(
        "time data '%s' does not match any supported format." % time_string)
