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
    uri = "/info/all"

    def __init__(self, args, basedir=None, subdir=None):
        # init self.options and prepare self.outdir
        super(TiDBInfo, self).__init__(args, basedir, subdir)
        if args.host:
            self.host = args.host
        if args.port:
            self.port = args.port
        self.url = "http://%s:%s%s" % (
            self.host, self.port, self.uri)

    def read_api(self):
        result, code = util.read_url(self.url)
        if code == 404:
            logging.info(
                "TiDB server API is not supported by this running instance.")
            return None
        return result

    def run_collecting(self):
        info = self.read_api()
        if info:
            fileopt.write_file(os.path.join(
                self.outdir, "%s_%s-tidb-info.json" % (self.host, self.port)), info)
