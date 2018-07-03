# -*- coding: utf-8 -*-
import logging
import os

from measurement.files import fileutils


def find_process_by_port(port=None, protocol=None):
    if not protocol:
        protocol = "tcp"
    process_list = []
    if not port:
        logging.fatal("No process listening port specified.")
        return

    # iterate over all file descriptors and build a socket address -> pid map
    def build_inode_to_pid_map():
        result = {}
        for entry in fileutils.list_dir("/proc"):
            # find all PIDs
            fname = entry.split('/')[-1]
            if str.isdigit(fname):
                for _fd in fileutils.list_dir("/proc/%s/fd" % fname):
                    try:
                        _fd_target = os.readlink(_fd)
                    except OSError as e:
                        import errno
                        if e.errno == errno.ENOENT:
                            pass
                        raise e
                    if not str.startswith(_fd_target, "socket"):
                        continue
                    _socket = _fd_target.split(":[")[-1][:-1]
                    try:
                        result[_socket].append(int(fname))
                    except KeyError:
                        result[_socket] = [int(fname)]
        return result

    def find_inode_by_port(port, protocol):
        result = set()
        netstat_files = {
            "tcp": ["/proc/net/tcp",
                    "/proc/net/tcp6"],
            "udp": ["/proc/net/udp",
                    "/proc/net/udp6"]
        }
        listen_list = []
        for netstat_file in netstat_files[protocol]:
            listen_list += fileutils.read_file(netstat_file).split("\n")
        for line in listen_list:
            if not line or "local_address" in line:
                continue
            _parts = line.split()
            _local_addr = _parts[1]
            _socket_st = _parts[3]
            _inode_addr = _parts[9]
            _local_port = int(_local_addr.split(":")[1], 16)
            # st of '0A' is TCP_LISTEN, and '07' is for UDP (TCP_CLOSE)
            # see linux/include/net/tcp_states.h for difinitions of other states
            if _socket_st != '0A' and _socket_st != '07':
                continue
            if int(port) != _local_port:
                continue
            result.add(_inode_addr)
        return result

    inode_process = build_inode_to_pid_map()
    for inode in find_inode_by_port(port, protocol):
        try:
            process_list += inode_process[inode]
        except KeyError:
            pass

    return set(process_list)  # de-duplicate
