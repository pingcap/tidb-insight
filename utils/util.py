# -*- coding: utf-8 -*-
# simple utilities

import logging
import os
import sys
import time

from subprocess import Popen, PIPE
try:
    # For Python 2
    import urllib2 as urlreq
    from urllib2 import HTTPError, URLError
except ImportError:
    # For Python 3
    import urllib.request as urlreq
    from urllib.error import HTTPError, URLError


def is_root_privilege():
    return os.getuid() == 0


# full directory path of this script
def pwd():
    return os.path.dirname(os.path.realpath(__file__))


# full path of current working directory
def cwd():
    return os.getcwd()


def chdir(nwd):
    return os.chdir(nwd)


def is_abs_path(path):
    return os.path.isabs(path)


def run_cmd(cmd, shell=False, input=None):
    p = Popen(cmd, shell=shell, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    return p.communicate(input=input)


def run_cmd_for_a_while(cmd, duration, shell=False):
    p = Popen(cmd, shell=shell)
    time.sleep(duration)
    p.kill()


def parse_cmdline(cmdline):
    result = {}
    try:
        cmd = cmdline.split()
    except (TypeError, AttributeError):
        return None
    for arg in cmd:
        # parse args that start with '--something'
        if arg.startswith("--"):
            argkv = arg.split("=")
            try:
                result[argkv[0][2:]] = argkv[1]
            except IndexError:
                pass
    return result


def get_init_type():
    try:
        init_exec = os.readlink("/proc/1/exe")
    except OSError:
        logging.warning("Unable to detect init type, am I running with root?")
        return None
    return init_exec.split("/")[-1]


def read_url(url, data=None):
    if not url or url == "":
        return None, None

    try:
        logging.debug("Requesting URL: %s" % url)
        response = urlreq.urlopen(url, data)
        return response.read(), response.getcode()
    except HTTPError as e:
        logging.debug("HTTP Error: %s" % e.read())
        return e.read(), e.getcode()
    except URLError as e:
        logging.warning("Reading URL %s error: %s" % (url, e))
        return None, None


def get_hostname():
    # This function is merely used, so only import socket package when necessary
    import socket
    return socket.gethostname()


def python_version():
    # get a numeric Python version
    return sys.version_info[0] + sys.version_info[1] * 0.1


def parse_timestamp(time_string):
    # if it's already a numeric timestamp, just return it
    try:
        if time_string.isdigit():
            return int(time_string)
    except (AttributeError, ValueError):
        pass
    format_guess = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H",
        "%Y-%m-%d",
        "%m-%d",
        "%H:%M:%S",
        "%H:%M",
        "%H"
    ]
    for time_format in format_guess:
        try:
            # Convert to timestamp (in seconds)
            return time.mktime(time.strptime(time_string, time_format))
        except (TypeError, ValueError):
            pass
    raise ValueError(
        "time data '%s' does not match any supported format." % time_string)


def format_size_bytes(size):
    # 2**10 = 1024
    power = 2**10
    i = 0
    unit = ['', 'K', 'M', 'G', 'T', 'P', 'E']
    while size > power:
        size /= power
        i += 1
    return '%.1f%s' % (size, unit[i])
