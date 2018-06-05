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
usage: insight.py [-h] [-o OUTPUT] [-p] [--pid PID] [--tidb-proc]
                  [--perf-exec PERF_EXEC] [--perf-freq PERF_FREQ]
                  [--perf-time PERF_TIME] [-l] [--syslog] [--config-file]
                  [--pd-host PD_HOST] [--pd-port PD_PORT]

TiDB Insight Scripts

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        The directory to store output data of TiDB Insight.
                        Any existing file will be overwritten without futher
                        confirmation.
  -p, --perf            Collect trace info using perf. Disabled by default.
  --pid PID             PID of process to run perf on. If `-p`/`--perf` is not
                        set, this value will not take effect. Multiple PIDs
                        can be set by using more than one `--pid` argument.
                        `None` by default which means the whole system.
  --tidb-proc           Collect perf data for PD/TiDB/TiKV processes instead
                        of the whole system.
  --perf-exec PERF_EXEC
                        Custom path of perf executable file.
  --perf-freq PERF_FREQ
                        Event sampling frequency of perf-record, in Hz.
  --perf-time PERF_TIME
                        Time period of perf recording, in seconds.
  -l, --log             Collect log files in output. PD/TiDB/TiKV logs are
                        included by default.
  --syslog              Collect the system log in output. This may
                        significantly increase output size. If `-l/--log` is
                        not set, the system log will be ignored.
  --config-file         Collect various configuration files in output,
                        disabled by default.
  --pd-host PD_HOST     The host of the PD server. `localhost` by default.
  --pd-port PD_PORT     The port of PD API service, `2379` by default.

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