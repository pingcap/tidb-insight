# TiDB Insight

[![Build Status](https://travis-ci.org/pingcap/tidb-insight.svg?branch=master)](https://travis-ci.org/pingcap/tidb-insight)
[![Go Report Card](https://goreportcard.com/badge/github.com/pingcap/tidb-insight)](https://goreportcard.com/report/github.com/pingcap/tidb-insight)

This is a set of tools and/or scripts to collect information and metrics from all nodes of a TiDB cluster. The data is collected and archived to a tarball so that one can copy the data to anywhere convenient for further investigation.

You may find it useful when you don't have access to the machines running TiDB services, but need to troubleshooting issues related to them.

## Collector

The `collector` is a simple binary tool that collects various kinds of server information, including system information, TiDB/TiKV/PD versions, etc.

The output of `collector` is a JSON to stdout.

## Scripts

WIP: The scripts to call other tools (e.g., `collector`) and organize their results.

The `insight.py` file is the entrance of all scripts. It calls `collector` to collect basic information and then trigger other tools to gather more data.

It is recommended to run this script with the root privilege.

The following features have been implemented:

 - Record `perf` data of the whole system, TiDB modules, or specific process. (disabled by default)
 - Check the file size of TiDB modules' data directories. (enabled by default)

## Insight

TO DO: Create the analysis tool that helps process dataset.