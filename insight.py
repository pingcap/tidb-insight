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

import os

def check_privilege():
    if os.getuid() != 0:
        print('''Warning: Running TiDB Insight with non-superuser privilege may result
         in lack of some information or data in the final output, if
         you find certain data missing or empty in result, please try
         to run this script again with root.''')

class Insight():
    # full directory path of this script
    def pwd(this):
        return os.path.dirname(os.path.realpath(__file__))

    # full path of current working directory
    def cwd(this):
        return os.getcwd()

    # data collected by `collector`
    collector_data = {}
    # collect data with `collector` and store it to disk
    def collector(this):
        # TODO: check existance of output dir
        # TODO: warn on non-empty output dir
        # TODO: call `collector` and store data to output dir
        return

if __name__ == "__main__":
    check_privilege()
    # TODO: add params to set output dir / overwriting on non-empty target dir
    insight = Insight()
    # TODO: call scripts that collect metrics of the node
    print(insight.pwd())
