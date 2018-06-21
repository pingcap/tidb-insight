# -*- coding: utf-8 -*-
import logging
import os

from measurement.files import fileutils


def find_process_by_port(port=None):
    process_list = []
    if not port:
        logging.fatal("No process listening port specified.")
        return

    # literate over all file descriptors and build a socket address -> pid map
    def build_inode_to_pid_map():
        result = {}
        for entry in os.scandir("/proc"):
            # find all PIDs
            if str.isdigit(entry.name):
                try:
                    for _fd in os.scandir("/proc/%s/fd" % entry.name):
                        _fd_target = os.readlink(_fd.path)
                        if not str.startswith(_fd_target, "socket"):
                            continue
                        _socket = _fd_target.split(":[")[:-2]
                        try:
                            result[_socket].append(entry.name)
                        except KeyError:
                            result[_socket] = [entry.name]
                except PermissionError:
                    logging.warn(
                        "Permission Denied reading /proc/%s/fd" % entry.name)
        return result

    def find_inode_by_port(port):
        result = set()
        listen_list = fileutils.read_file("/proc/net/tcp").split("\n")
            + fileutils.read_file("/proc/net/udp").split("\n")
        for line in listen_list:
            if not line:
                continue
            _parts = line.split()
            _local_addr = _parts[1]
            _inode_addr = _parts[9]
            _local_port = int(_local_addr.split(":")[1], 16)
            if int(port) != _local_port:
                continue
            result.add(_inode_addr)
        return result

    inode_process = build_inode_to_pid_map()
    for inode in find_inode_by_port(port):
        process_list.append(inode_process[inode])

    return process_list
