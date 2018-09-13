# -*- coding: utf-8 -*-
# cmd arguments

import argparse

from utils import util


def parse_insight_opts():
    parser = argparse.ArgumentParser(description="TiDB Insight Scripts, collect various diagnosis data.",
                                     epilog="Note that some arguments may decrease system performance.")
    parser.add_argument("-o", "--output", action="store", default=None,
                        help="The directory to store output data of TiDB Insight. Any existing file will be overwritten without futher confirmation.")
    parser.add_argument("--alias", action="store", default=util.get_hostname(),
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
    parser_log.add_argument("--systemd", action="store_true", default=False,
                            help="Collect systemd journald logs, disabled by default.")
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
    parser_tidbinfo = subparsers_tidb.add_parser(
        "tidbinfo", help="Collect data from TiDB's server API.")
    parser_tidbinfo.add_argument("--host", action="store", default=None,
                                 help="The host of the TiDB server, `localhost` by default.")
    parser_tidbinfo.add_argument("--port", type=int, action="store", default=None,
                                 help="The port of TiDB server API port, `10080` by default.")
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
                             help="Start time point of time range, format: '%%Y-%%m-%%d %%H:%%M:%%S' (local time).")
    parser_prom.add_argument("--end", action="store", default=None,
                             help="End time point of time range, format: '%%Y-%%m-%%d %%H:%%M:%%S' (local time).")
    parser_prom.add_argument("--resolution", type=float, default=None,
                             help="Query resolution step width of Prometheus in seconds, 15.0 by default.")
    parser_prom.add_argument("--proc-num", type=int, action="store", default=None,
                             help="Number of parallel queries to run, 'CPU count / 2 + 1' by default.")

    parser_load = subparser_metric.add_parser(
        "load", help="Load dumped metrics to local influxdb.")
    parser_load.add_argument("--host", action="store", default=None,
                             help="The host of local influxdb, `localhost` by default.")
    parser_load.add_argument("--port", type=int, action="store",
                             default=None, help="The port of local TSDB, `8086` by default.")
    parser_load.add_argument("--dir", action="store", default=None,
                             help="The directory of dumped data, `data` by default.")
    parser_load.add_argument("--db", action="store", default=None,
                             help="The database of imported metrics, if not set, a unique name will be auto generated by default.")
    parser_load.add_argument("--user", action="store", default=None,
                             help="The user with priviledge to create database, empty (no authentication needed) by default.")
    parser_load.add_argument("--passwd", action="store", default=None,
                             help="The password of user, empty (no authentication needed) by default.")
    parser_load.add_argument("--proc-num", type=int, action="store", default=None,
                             help="Number of parallel importer processes to run, 'CPU count + 1' by default.")
####

# Sub-commad: show
    parser_show = subparsers.add_parser("show", help="Display information.")
    subparser_show = parser_show.add_subparsers(dest="subcmd_show")
    parser_servers = subparser_show.add_parser(
        "servers", help="List servers in a cluster.")
    parser_servers.add_argument("--dir", action="store", default=None,
                                help="Directory where all collected data stored. None by default and will raise an exception.")
####

    return parser.parse_args()
