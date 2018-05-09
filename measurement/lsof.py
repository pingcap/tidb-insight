# -*- coding: utf-8 -*-
# List open files of process by `lsof`

from measurement import util


# list open files of process by `lsof`
def lsof(pid):
    cmd = ["lsof", "-p",
           "%s" % pid]
    return util.run_cmd(cmd)
