# -*- coding: utf-8 -*-
# Export monitoring metrics from Prometheus API
# This feature queries Prometheus API to get all metric key and data,
# then store them as files in the output directory.

import json
import logging
import os
import zlib

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

        self.resolution = args.resolution if args.resolution else 15.0

    def get_label_names(self):
        result = []
        url = '%s%s' % (self.url_base, '/label/__name__/values')
        labels = json.loads(util.read_url(url))
        if labels['status'] == 'success':
            result = labels['data']
        logging.debug("Found %s available metric keys..." % len(result))
        return result

    def run_collecting(self):
        if self.resolution < 15.0:
            logging.warn(
                "Sampling resolution < 15s don't increase accuracy but data size.")
        for metric in self.get_label_names():
            url = '%s/query_range?query=%s&start=%s&end=%s&step=%s' % (
                self.url_base, metric, self.start_time, self.end_time, self.resolution)
            matrix = json.loads(util.read_url(url))
            if not matrix['status'] == 'success':
                logging.info("Error querying for key '%s'." % metric)
                logging.debug("Output is:\n%s" % matrix)
                continue
            if self.options.compress:
                metric_filename = '%s_%s_to_%s_%ss.dat' % (
                    metric, self.start_time, self.end_time, self.resolution)
                fileopt.write_file(os.path.join(self.outdir, metric_filename), zlib.compress(
                    json.dumps(matrix['data']['result'])))
            else:
                metric_filename = '%s_%s_to_%s_%ss.json' % (
                    metric, self.start_time, self.end_time, self.resolution)
                fileopt.write_file(os.path.join(
                    self.outdir, metric_filename), json.dumps(matrix['data']['result']))
            logging.debug("Saved data for key '%s'." % metric)
