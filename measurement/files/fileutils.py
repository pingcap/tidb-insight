# -*- coding: utf-8 -*-
# simple file related utilities

import os


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
    except OSError:
        if os.path.isdir(path):
            return path
    return None
