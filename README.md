# TiDB Insight

[![Build Status](https://travis-ci.org/pingcap/tidb-insight.svg?branch=master)](https://travis-ci.org/pingcap/tidb-insight)
[![Go Report Card](https://goreportcard.com/badge/github.com/pingcap/tidb-insight)](https://goreportcard.com/report/github.com/pingcap/tidb-insight)

TiDB Insight is a set of tools and/or scripts to collect information and metrics from all nodes of a TiDB cluster. The data is collected and archived to a tarball so that one can copy the data anywhere for further investigation.

TiDB Insight is designed to help you troubleshoot and diagnose machines within a TiDB cluster when you don't have access to the cluster.

## Collector

The `collector` is a simple binary tool written in Go that collects various kinds of server information, including system information, TiDB/TiKV/PD versions, etc.

`collector` prints a JSON to stdout.

## Scripts

WIP: The scripts to call other tools (e.g., `collector`) and organize their results.

The `insight.py` file is the entrance of all scripts. It calls `collector` to collect basic information and then trigger other tools to gather more data.

It is recommended to run this script with the root privilege.

The following features have been implemented:

 - Record `perf` data of the whole system, TiDB modules, or specific process. (disabled by default)
 - Check the file size of TiDB modules' data directories. (enabled by default)
 - Collect and save log files of TiDB modules or system. (disabled by default)
 - Collect and save various configuration files of system. (disabled by default)
 - Query PD API to collect runtime information of the TiDB cluster. (enabled by default)

### Usage

For a full list of arguments, you may refer to the output of `insight.py -h`:

```
usage: insight.py [-h] [-o OUTPUT] [--alias ALIAS] [-c] [-p] [--pid PID]
                  [--proc-listen-port PROC_LISTEN_PORT]
                  [--proc-listen-proto PROC_LISTEN_PROTO] [--tidb-proc]
                  [--perf-exec PERF_EXEC] [--perf-freq PERF_FREQ]
                  [--perf-time PERF_TIME] [--perf-archive] [-l] [--syslog]
                  [--log-auto] [--log-dir LOG_DIR] [--log-prefix LOG_PREFIX]
                  [--log-retention LOG_RETENTION] [--config-file]
                  [--config-auto] [--config-sysctl] [--config-dir CONFIG_DIR]
                  [--config-prefix CONFIG_PREFIX] [--pdctl]
                  [--pd-host PD_HOST] [--pd-port PD_PORT] [-v] [--ftrace]
                  [--ftracepoint FTRACEPOINT] [--ftrace-time FTRACE_TIME]
                  [--ftrace-bufsize FTRACE_BUFSIZE] [--vmtouch]
                  [--vmtouch-target VMTOUCH_TARGET] [--blktrace]
                  [--blktrace-target BLKTRACE_TARGET]
                  [--blktrace-time BLKTRACE_TIME]

TiDB Insight Scripts

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        The directory to store output data of TiDB Insight.
                        Any existing file will be overwritten without futher
                        confirmation.
  --alias ALIAS         The alias of this instance. This value be part of the
                        name of output tarball. If not set, the hostname of
                        server will be used by default.
  -c, --compress        Compress all output files to a tarball and delete
                        temporary files, disabled by default.
  -p, --perf            Collect trace info using perf. Disabled by default.
  --pid PID             PID of process to run perf on. If `-p`/`--perf` is not
                        set, this value will not take effect. Multiple PIDs
                        can be set by using more than one `--pid` argument.
                        `None` by default which means the whole system.
  --proc-listen-port PROC_LISTEN_PORT
                        Collect perf data of process that listen on given
                        port. This value will be ignored if `--pid` is set.
  --proc-listen-proto PROC_LISTEN_PROTO
                        Protocol type of listen port, available values are:
                        tcp/udp. If not set, only TCP listening ports are
                        checked.
  --tidb-proc           Collect perf data for PD/TiDB/TiKV processes instead
                        of the whole system.
  --perf-exec PERF_EXEC
                        Custom path of perf executable file.
  --perf-freq PERF_FREQ
                        Event sampling frequency of perf-record, in Hz.
  --perf-time PERF_TIME
                        Time period of perf recording, in seconds.
  --perf-archive        Run `perf archive` after collecting data, useful when
                        reading data on another machine, may cause large
                        output file size. Disabled by default.
  -l, --log             Collect log files in output. PD/TiDB/TiKV logs are
                        included by default if no other argument given.
  --syslog              Collect the system log in output. This may
                        significantly increase output size. If `-l/--log` is
                        not set, the system log will be ignored.
  --log-auto            Automatically detect and save log files of running
                        PD/TiDB/TiKV processes.
  --log-dir LOG_DIR     Location of log files. If `--log-auto` is set, this
                        value will be ignored.
  --log-prefix LOG_PREFIX
                        The prefix of log files, will be the directory name of
                        all logs, will be in the name of output tarball. If
                        `--log-auto` is set, this value will be ignored.
  --log-retention LOG_RETENTION
                        The time of log retention, any log files older than
                        given time period from current time will not be
                        included. Value should be a number of hour(s) in
                        positive interger. `0` by default and means no time
                        check.
  --config-file         Collect various configuration files in output,
                        disabled by default.
  --config-auto         Automatically detect and save configuration files for
                        all running PD/TiDB/TiKV processes.
  --config-sysctl       Save kernel config by collecting output of `sysctl
                        -a`.
  --config-dir CONFIG_DIR
                        Location of config files. If `--config-auto` is set,
                        this value will be ingored.
  --config-prefix CONFIG_PREFIX
                        The prefix of config files, will be directory name of
                        all config files, will be in the name of output
                        tarball. If `--config-auto` is set, the value will be
                        ignored.
  --pdctl               Enable collecting data from PD API. Disabled by
                        default.
  --pd-host PD_HOST     The host of the PD server. `localhost` by default.
  --pd-port PD_PORT     The port of PD API service, `2379` by default.
  -v, --verbose         Print verbose output.
  --ftrace              Collect trace info using ftrace. Disabled by default.
  --ftracepoint FTRACEPOINT
                        Tracepoint to be traced (only support to trace direct
                        reclaim latency).
  --ftrace-time FTRACE_TIME
                        Time period of ftrace recording, in seconds (default
                        60s).
  --ftrace-bufsize FTRACE_BUFSIZE
                        Ftrace ring buffer size in kb (default 4096 kb).
  --vmtouch             Collect page cache info using vmtouch. Disabled by
                        default.
  --vmtouch-target VMTOUCH_TARGET
                        File or dir to be diagnosed.
  --blktrace            Collect traces of the i/o traffic on block devices by
                        blktrace. Disabled by default.
  --blktrace-target BLKTRACE_TARGET
                        The device to trace
  --blktrace-time BLKTRACE_TIME
                        Time period of blktrace recording, in seconds (default
                        60s).

Note that some arguments may decrease system performance.
```

If `insight.py` is called with no argument provided, the following information is collected and saved to `data` directory in the current working directory:

 - `collector`, which provides the system information, program versions, NTP status, partition statistics and process statistics of TiDB modules (if present), placed in the `collector` sub-directory.
 - PD API output of `config`, `diagnose`, `health`, `hotspot`, `labels`, `members`, `operators`, `regions`, `regionstats`, `schedulers` and `status`, placed in the `pdctl` sub-directory in JSON format.

Using `-o` can set another location to store output data except the default `data`.

### Examples

Take `insight.py -l --config-file`, a common combination of arguments as an example. It is used to collect the basic system information, TiDB modules' log files and several config files.

If you want to collect runtime information of a TiDB cluster from PD on a remote host (instead of running the scripts on that server), set `--pd-host` to the IP address or a resolvable hostname of that host. Additionally, if PD is listening on non-default port, use `--pd-port` to set it.

The system log is not collectd by default, even if `-l` is set. If needed, use `-l --syslog` to enable it. Both `syslog` and `systemd-journald` logs are supported and automatically detected. Note that there is no content filter available for log files, thus enabling log file collecting may lead to a very large output size.

## Intergration with Ansible

The `tidb-insight` project is designed to intergrate with [tidb-ansible](https://github.com/pingcap/tidb-ansible) playbooks.

> All collecting features will be disabled by default after the development of intergration is finished, so it's highly recommended to specify all the arguments needed when using `tidb-insight` now, even if the feature is currently enabled by default.

TO DO: Add documents/links to documents of using `tidb-insight` with `tidb-ansible`.

## Insight

TO DO: Create the analysis tool that helps process dataset.