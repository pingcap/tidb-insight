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
# This script is developed under Python 3.x, although Python 2.x may
# also work in most circumstances, please use Python 3.x when possible.

import json
import os
import subprocess

from measurement import perf
from measurement import util

class Insight():
    # data output dir
    outdir = "data"

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
        full_outdir = util.CheckDir(self.outdir)
        util.WriteFile(os.path.join(full_outdir, "collector.json"),
                        json.dumps(self.collector_data, indent=2))

if __name__ == "__main__":
    util.CheckPrivilege()
    # TODO: add params to set output dir / overwriting on non-empty target dir
    insight = Insight()
    # TODO: call scripts that collect metrics of the node
    print(util.pwd(), util.cwd())
    insight.collector()