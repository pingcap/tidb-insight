# -*- coding: utf-8 -*-
# Export monitoring metrics from Prometheus API
# This feature reads Grafana Dashboard JSON config and querys
# Prometheus API to get data, so it's not intend to be used
# without a fully working tidb-ansible configuration.

import json
import logging
import os

from metric.base import MetricBase
from utils import fileopt
from utils import util


class PromMetrics(MetricBase):
    def __init__(self, args, basedir=None, subdir=None):
        # init self.options and prepare self.outdir
        super(PromMetrics, self).__init__(args, basedir, subdir)

        self.host = args.host if args.host else 'localhost'
        self.port = args.port if args.port else 9090
        self.api_uri = '/api/v1'
        self.url_base = 'http://%s:%s%s' % (self.host, self.port, self.api_uri)

        self.resolution = args.resolution if args.resolution else 5.0

    def get_label_names(self):
        url = '%s%s' % (self.url_base, '/label/__name__/values')
        labels = json.loads(util.read_url(url))
        if labels['status'] == 'success':
            return labels['data']
        return []

    def run_collecting(self):
        for metric in self.get_label_names():
            url = '%s/query_range?query=%s&start=%s&end=%s&step=%s' % (
                self.url_base, metric, self.start_time, self.end_time, self.options.resolution)
            matrix = json.loads(util.read_url(url))
            if not matrix['status'] == 'success':
                logging.info("Error querying for key '%s'." % metric)
                logging.debug("Output is:\n%s" % matrix)
                continue
            metric_filename = '%s_%s_to_%s_%ss.json' % (
                metric, self.start_time, self.end_time, self.options.resolution)
            fileopt.write_file(os.path.join(
                self.outdir, metric_filename), matrix['data']['result'])
