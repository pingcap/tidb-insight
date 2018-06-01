# TiDB Insight

[![Build Status](https://travis-ci.org/pingcap/tidb-insight.svg?branch=master)](https://travis-ci.org/pingcap/tidb-insight)
[![Go Report Card](https://goreportcard.com/badge/github.com/pingcap/tidb-insight)](https://goreportcard.com/report/github.com/pingcap/tidb-insight)

This is a set of tools and/or scripts to collect information and metrics from all nodes of a TiDB cluster. The data is collected and archived to a tarball so that one can copy the data to anywhere convenient for further investigation.

You may find it useful when you don't have access to the machines running TiDB services, but need to troubleshooting issues related to them.

## Collector

The `collector` is a simple binary tool written in Go that collects various kinds of server information, including system information, TiDB/TiKV/PD versions, etc.

The output of `collector` is a JSON to stdout.

## Scripts

WIP: The scripts to call other tools (e.g., `collector`) and organize their results.

The `insight.py` file is the entrance of all scripts. It calls `collector` to collect basic information and then trigger other tools to gather more data.

It is recommended to run this script with the root privilege.

The following features have been implemented:

 - Record `perf` data of the whole system, TiDB modules, or specific process. (disabled by default)
 - Check the file size of TiDB modules' data directories. (enabled by default)
 - Collect and save log files of TiDB modules or system. (disabled by default)
 - Collect ans save various config files of system. (disabled by default)
 - Query PD API to collect runtime information of TiDB cluster. (enabled by default)

### Usage

    usage: insight.py [-h] [-o OUTPUT] [-p] [--pid PID] [--tidb-proc]
                    [--perf-exec PERF_EXEC] [--perf-freq PERF_FREQ]
                    [--perf-time PERF_TIME] [-l] [--syslog] [--config-file]
                    [--pd-host PD_HOST] [--pd-port PD_PORT]

    TiDB Insight Scripts

    optional arguments:
    -h, --help            show this help message and exit
    -o OUTPUT, --output OUTPUT
                            The dir to store output data of TiDB Insight, any
                            existing file will be overwritten without futher
                            confirmation.
    -p, --perf            Collect trace info with perf. Default is disabled.
    --pid PID             PID of process to run perf on, if '-p/--perf' is not
                            set, this value will be ignored and would not take any
                            effection. Multiple PIDs can be set by using more than
                            one --pid args. Default is None and means the whole
                            system.
    --tidb-proc           Collect perf data for PD/TiDB/TiKV processes instead
                            of the whole system.
    --perf-exec PERF_EXEC
                            Custom path of perf executable file.
    --perf-freq PERF_FREQ
                            Event sampling frequency of perf-record, in Hz.
    --perf-time PERF_TIME
                            Time period of perf recording, in seconds.
    -l, --log             Enable to include log files in output, PD/TiDB/TiKV
                            logs are included by default.
    --syslog              Enable to include system log in output, will be
                            ignored if -l/--log is not set. This may significantly
                            increase output size.
    --config-file         Enable to include various config files in output,
                            disabled by default.
    --pd-host PD_HOST     The host of PD server. Default to localhost.
    --pd-port PD_PORT     The port of PD API service, default to 2379.

    Note that some options would decrease system performance.

If calling `insight.py` with no argument provided, following information are collected and saved to `data` directory of current working directory:

 - `collector`, providing system information, program versions, NTP status, partition statics and process statics of TiDB modules (if present), placed under `collector` sub-directory.
 - PD API output of `config`, `diagnose`, `health`, `hotspot`, `labels`, `members`, `operators`, `regions`, `regionstats`, `schedulers` and `status`, placed under `pdctl` sub-directory in JSON format.

### Examples

A common combination of params that could be useful is: `insight.py -l --config-file`, with which the basic system information, TiDB modules' log files and several config files are collected.

If you want to collect runtime information of a TiDB cluster from PD on a remote host (instead of running the scripts on that server), set `--pd-host` to the IP address or a resolvable hostname of that host. Additionally, if PD is listening on non-default port, use `--pd-port` to set it.

System log is not collectd by default, even if `-l` is set. If it's needed, use `-l --syslog` to enable it. Both `syslog` and `systemd-journald` log are supported, note that there is no content filter available for log files, thus enabling log file collection may leads to very large output size.

## Intergration with Ansible

The tidb-insight project is designed to intergrate with [tidb-ansible](https://github.com/pingcap/tidb-ansible) playbooks.

TO DO: Documents / Links to Documents of using tidb-insight with tidb-ansible.

## Insight

TO DO: Create the analysis tool that helps process dataset.