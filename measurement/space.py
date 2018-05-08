# -*- coding: utf-8 -*-
# Check file space usage with `du`

from glob import glob
from os import path

from measurement import util

# check total size of filepath with `du`
def du_total(filepath):
    # TODO: support relative path, this require `collector` to output cwd of process
    cmd = ["du", "-s", filepath]
    return util.run_cmd(cmd)

def du_subfiles(filepath):
    # TODO: support relative path, this require `collector` to output cwd of process
    filelist = glob(filepath+"/*")
    cmd = ["du", "-s"] + filelist
    return util.run_cmd(cmd)
