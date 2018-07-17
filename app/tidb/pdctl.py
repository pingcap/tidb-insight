# -*- coding: utf-8 -*-
# Collect infomation with PD Controller

import os

from utils import util
from utils import fileopt


class PDCtl():
    # default output dir name
    pdctl_dir = "pdctl"

    # default to localhost
    pd_host = "localhost"
    pd_port = 2379

    # The `pdctl` API base URI
    base_uri = "/pd/api"
    base_url = ""

    # The `pdctl` API version
    api_ver = "1"
    api_path = "/v%s" % api_ver

    # The `pdctl` API URIs and relevant readable names, for full list of API
    # routes, see: https://github.com/pingcap/pd/blob/master/server/api/router.go
    # NOTE: All requests are GET
    api_map = {
        "config": "/config",
        "operators": "/operators",
        "schedulers": "/schedulers",
        "labels": "/labels",
        "hotspot": "/hotspot/stores",
        "regions": "/regions",
        "regionstats": "/stats/region",
        "status": "/status",
        "members": "/members",
    }

    # primary info of PD
    pd_health_uri = "/health"
    pd_diagnose_uri = "/diagnose"

    def __init__(self, host=None, port=None, api_ver=None):
        if host:
            self.pd_host = host
        if port:
            self.pd_port = port
        if api_ver:
            self.api_ver = api_ver
        self.base_url = "http://%s:%s%s%s" % (
            self.pd_host, self.pd_port, self.base_uri, self.api_path)

    def read_health(self):
        url = "http://%s:%s/pd%s" % (self.pd_host,
                                     self.pd_port, self.pd_health_uri)
        return util.read_url(url)

    def read_diagnose(self):
        url = "http://%s:%s/pd%s" % (self.pd_host,
                                     self.pd_port, self.pd_diagnose_uri)
        return util.read_url(url)

    def read_runtime_info(self):
        def build_url(uri):
            return "%s/%s" % (self.base_url, uri)

        runtime_info = {}
        for key, uri in self.api_map.items():
            runtime_info[key] = util.read_url(build_url(uri))
        return runtime_info

    def save_info(self, basedir=None):
        full_outputdir = fileopt.build_full_output_dir(
            basedir=basedir, subdir=self.pdctl_dir)
        pd_health = self.read_health()
        if pd_health:
            fileopt.write_file(os.path.join(
                full_outputdir, "%s_%s-health.json" % (self.pd_host, self.pd_port)), pd_health)
        pd_diagnose = self.read_diagnose()
        if pd_diagnose:
            fileopt.write_file(os.path.join(
                full_outputdir, "%s_%s-diagnose.json" % (self.pd_host, self.pd_port)), pd_diagnose)

        for key, info in self.read_runtime_info().items():
            if not info:
                continue
            fileopt.write_file(os.path.join(
                full_outputdir, "%s_%s-%s.json" % (self.pd_host, self.pd_port, key)), info)
