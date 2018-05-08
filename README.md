# TiDB Insight

[![Build Status](https://travis-ci.org/pingcap/tidb-insight.svg?branch=master)](https://travis-ci.org/pingcap/tidb-insight)
[![Go Report Card](https://goreportcard.com/badge/github.com/pingcap/tidb-insight)](https://goreportcard.com/report/github.com/pingcap/tidb-insight)

This is a set of tools and/or scripts to collect infomation and metrics from all nodes of a TiDB cluster, the data are collected and archived to a tarball, so that one can copy the data to anywhere convenient for further invesgating.

You may find it useful when you don't have access to the machines running TiDB services, but need to throubleshooting issues related to them.

## Collector

The `collector` is a simple binary tool that collects various infomation of the server, including system infomation, TiDB/TiKV/PD versions, etc.

The output of `collector` is a JSON to stdout.

## Scripts

WIP: The scripts to call other tools (e.g., collector) and organize their results.

`insight.py` file is the entrance of all scripts, it calls `collector` to collect basic infomation and then trigger other tools to gather more data.

It's recommended to run this script with root priviledge.

Now implemented:

 - Record `perf` data of whole system, or TiDB modules, or specific process. (disabled by default)
 - Check file size of TiDB modules' data dirs (enabled by default)

## Insight

TODO: the analyse tool that helps processing dataset.
