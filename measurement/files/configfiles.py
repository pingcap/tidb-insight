# -*- coding: utf-8 -*-
# Get various config files

import os
import shutil

from glob import glob

from measurement import util
from measurement.files import fileutils


class InsightConfigFiles():
    # options about logfiles
    config_options = {}

    # output dir
    config_dir = "conf"

    def __init__(self, options={}):
        self.config_options = options

    def save_sysctl(self, outputdir=None):
        cmd = ["sysctl", "-a"]
        full_outputdir = fileutils.build_full_output_dir(
            basedir=outputdir, subdir=self.config_dir)
        stdout, stderr = util.run_cmd(cmd)
        if stdout:
            fileutils.write_file(os.path.join(full_outputdir, "sysctl.conf"), stdout)
        if stderr:
            fileutils.write_file(os.path.join(full_outputdir, "sysctl.err"), stderr)
