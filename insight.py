#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 PingCAP, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This script is developed under Python 3.6 and compatiable with 3.2 and
# above, although Python 2 with version 2.7 and above may also work in
# most circumstances, please use latest Python 3 when possible.

import argparse
import json
import os
import subprocess

from measurement import perf
from measurement import util

class Insight():
    # data output dir
    outdir = "data"
    full_outdir = ""

    def __init__(self, outdir=None):
        self.full_outdir = util.CheckDir(self.outdir)

    # data collected by `collector`
    collector_data = {}
    # collect data with `collector` and store it to disk
    def collector(self):
        # TODO: check existance of output dir
        # TODO: warn on non-empty output dir

        # WIP: call `collector` and store data to output dir
        base_dir = os.path.join(util.pwd(), "../")
        collector_exec = os.path.join(base_dir, "bin/collector")

        f = subprocess.Popen(collector_exec, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = f.communicate()
        try:
            self.collector_data = json.loads(stdout)
        except json.JSONDecodeError:
            # TODO: unified output: "Error collecting system info.\n%s" % stderr
            return
        util.WriteFile(os.path.join(self.full_outdir, "collector.json"),
                        json.dumps(self.collector_data, indent=2))
    
    def run_perf(self, args):
        if not args.perf:
            return

        # "--tidb-proc" has the highest priority
        if args.tidb_proc:
            perf_proc = perf.format_proc_info(self.collector_data["proc_stats"])
            insight_perf = perf.InsightPerf(perf_proc, args)
            insight_perf.run()
        # parse pid list
        elif len(args.pid) > 0:
            perf_proc = {}
            for _pid in args.pid:
                perf_proc[_pid] = None
            insight_perf = perf.InsightPerf(perf_proc, args)
            insight_perf.run()
        else:
            insight_perf = perf.InsightPerf(options=args)
            insight_perf.run()

def parse_opts():
    parser = argparse.ArgumentParser(description="TiDB Insight Scripts",
            epilog="Note that some options would decrease system performance.")
    parser.add_argument("-O", "--output", action="store", default=None,
                        help='''The dir to store output data of TiDB Insight, any existing file
                        will be overwritten without futher confirmation.''')

    parser.add_argument("-p", "--perf", action="store_true", default=False,
                        help="Collect trace info with perf. Default is disabled.")
    parser.add_argument("--pid", type=int, action="append", default=None,
                        help='''PID of process to run perf on, if '-p/--perf' is not set, this
                        value will be ignored and would not take any effection.
                        Multiple PIDs can be set by using more than one --pid args.
                        Default is None and means the whole system.''')
    parser.add_argument("--tidb-proc", action="store_true", default=False,
                        help="Collect perf data for PD/TiDB/TiKV processes instead of the whole system.")
    parser.add_argument("--perf-exec", type=int, action="store", default=None,
                        help="Custom path of perf executable file.")
    parser.add_argument("--perf-freq", type=int, action="store", default=None,
                        help="Event sampling frequency of perf-record, in Hz.")
    parser.add_argument("--perf-time", type=int, action="store", default=None,
                        help="Time period of perf recording, in seconds.")
    
    return parser.parse_args()

if __name__ == "__main__":
    util.CheckPrivilege()
    insight = Insight()

    # WIP: add params to set output dir / overwriting on non-empty target dir
    args = parse_opts()
    if args.output:
        insight.outdir = args.output

    insight.collector()
    # WIP: call scripts that collect metrics of the node
    insight.run_perf(args)