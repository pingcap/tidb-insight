# -*- coding: utf-8 -*-
# simple file related utilities

import logging
import os
import tarfile

from utils import util

# read data from file


def read_file(filename, mode='r'):
    data = None
    with open(filename, mode) as f:
        data = f.read()
    f.close()
    return data


# write data to file
def write_file(filename, data, mode='w'):
    with open(filename, mode) as f:
        try:
            f.write(str(data, 'utf-8'))
        except TypeError:
            f.write(data)
    f.close()


# create target directory, do nothing if it already exists
def create_dir(path):
    try:
        os.makedirs(path)
        return path
    except OSError as e:
        # There is FileExistsError (devided from OSError) in Python 3.3+,
        # but only OSError in Python 2, so we use errno to check if target
        # dir already exists.
        import errno
        if e.errno == errno.EEXIST and os.path.isdir(path):
            logging.info("Target path \"%s\" already exists." % path)
            return path
        else:
            logging.fatal("Can not prepare output dir, error is: %s" % str(e))
            exit(e.errno)
    return None


# os.scandir() is added in Python 3.5 and has better performance than os.listdir()
# so we try to use it if available, and fall back to os.listdir() for older versions
def list_dir(path):
    file_list = []
    try:
        if util.python_version() >= 3.5:
            for entry in os.scandir(path):
                file_list.append("%s/%s" % (path, entry.name))
        else:
            for file in os.listdir(path):
                file_list.append("%s/%s" % (path, file))
    except OSError as e:
        # There is PermissionError in Python 3.3+, but only OSError in Python 2
        import errno
        if e.errno == errno.EACCES or e.errno == errno.EPERM:
            logging.warn("Permission Denied reading %s" % path)
        elif e.errno == errno.ENOENT:
            # when a process just exited
            pass
    return file_list


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


def compress_tarball(output_base=None, output_name=None):
    # compress output files to tarball
    os.chdir(output_base)
    cmd = ["tar",
           "--remove-files",
           "-zcf",
           "%s.tar.gz" % output_name,
           output_name]
    stdout, stderr = util.run_cmd(cmd)
    if not stderr and stderr != '':
        logging.info("tar stderr: %s" % stderr)
    if not stdout and stdout != '':
        logging.debug("tar output: %s" % stdout)


def decompress_tarball_recursive(srcdir=None, dstdir=None):
    if not srcdir:
        srcdir = util.cwd()
    if not dstdir:
        dstdir = util.cwd()

    # find tarballs
    for file in list_dir(srcdir):
        if file.endswith('.tar.gz'):
            tar = tarfile.open(file)
            tar.extractall(dstdir)
            tar.close()
        elif os.path.isdir(file):
            subdir = create_dir(os.path.join(dstdir, file.split('/')[-1]))
            decompress_tarball_recursive(file, subdir)
        else:
            pass
