# -*- coding: utf-8 -*-
# Collect infomation with TiDB API

import logging
import os

from utils import util
from utils import fileopt
from utils.measurement import MeasurementBase


class TiDBInfo(MeasurementBase):
    # default to localhost
    host = "localhost"
    port = 10080

    # The API's URI
    uri_map = {
        "info": "/info",
        "info-all": "/info/all",
        "status": "/status",
        "regions": "/regions/meta",
        "schema": "/schema",
        "settings": "/settings"
    }

    def __init__(self, args, basedir=None, subdir=None):
        # init self.options and prepare self.outdir
        super(TiDBInfo, self).__init__(args, basedir, subdir)
        if args.host:
            self.host = args.host
        if args.port:
            self.port = args.port
        self.url_base = "http://%s:%s" % (
            self.host, self.port)

    def read_api(self, url):
        result, code = util.read_url(url)
        if code == 404:
            logging.info(
                "TiDB server API is not supported by this running instance.")
            return None
        return result

    def run_collecting(self):
        for key, uri in self.uri_map.items():
            data = self.read_api(self.url_base + uri)
            if data:
                fileopt.write_file(os.path.join(
                    self.outdir, "%s_%s-tidb-%s.json" % (self.host, self.port, key)), data)
