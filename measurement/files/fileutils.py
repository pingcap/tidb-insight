# -*- coding: utf-8 -*-
# simple file related utilities

import logging
import os

from measurement import util


# read data from file
def read_file(filename):
    data = None
    with open(filename, 'r') as f:
        data = f.read()
    f.close()
    return data


# write data to file, in plain text
def write_file(filename, data):
    with open(filename, 'w') as f:
        try:
            f.write(str(data, 'utf-8'))
        except TypeError:
            f.write(data)
    f.close()


# create target directory, do nothing if it already exists
def create_dir(path):
    try:
        os.mkdir(path)
        return path
    except OSError as e:
        # There is FileExistsError (devided from OSError) in Python 3.3+,
        # but only OSError in Python 2, so we use errno to check if target
        # dir already exists.
        import errno
        if e.errno == errno.EEXIST and os.path.isdir(path):
            return path
        else:
            logging.fatal("Can not prepare output dir, error is: %s" % str(e))
            exit(e.errno)
    return None


def build_full_output_dir(basedir=None, subdir=None):
    if basedir is None and subdir is None:
        # default to current working directory
        return util.cwd()

    if basedir is None:
        # if no basedir set, use subdir at cwd
        return create_dir(subdir)
    else:
        # full path of basedir/subdir
        return create_dir(os.path.join(basedir, subdir))
