# -*- coding: utf-8 -*-
# Collect infomation with PD Controller

from glob import glob

from measurement import util

class PDCtl():
    # default to localhost
    pd_host = "localhost"
    pd_port = 2379

    # The `pdctl` API base URI
    base_uri = "/pd/api"

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
        if not host:
            self.pd_host = host
        if not port:
            self.pd_port = port
        if not api_ver:
            self.api_ver = api_ver
