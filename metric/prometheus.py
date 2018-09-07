# -*- coding: utf-8 -*-
# Export monitoring metrics from Prometheus API
# This feature queries Prometheus API to get all metric key and data,
# then store them as files in the output directory.

import json
import logging
import os

import multiprocessing as mp

from metric.base import MetricBase
from utils import fileopt
from utils import util


class PromMetrics(MetricBase):
    def __init__(self, args, basedir=None, subdir=None):
        # init self.options and prepare self.outdir
        super(PromMetrics, self).__init__(args, basedir, subdir)

        self.host = args.host if args.host else 'localhost'
        self.port = args.port if args.port else 9090
        self.proc_num = args.proc_num if args.proc_num else int(
            mp.cpu_count() / 2 + 1)

        self.api_uri = '/api/v1'
        self.url_base = 'http://%s:%s%s' % (self.host, self.port, self.api_uri)

        self.resolution = args.resolution if args.resolution else 15.0

    def get_label_names(self):
        result = []
        url = '%s%s' % (self.url_base, '/label/__name__/values')
        labels = json.loads(util.read_url(url)[0])
        if labels['status'] == 'success':
            result = labels['data']
        logging.debug("Found %s available metric keys..." % len(result))
        return result

    def query_worker(self, metric):
        url = '%s/query_range?query=%s&start=%s&end=%s&step=%s' % (
            self.url_base, metric, self.start_time, self.end_time, self.resolution)
        response = util.read_url(url)[0]
        if 'success' not in response[:20].decode('utf-8'):
            logging.error("Error querying for key '%s'." % metric)
            logging.debug("Output is:\n%s" % response)
            return
        metric_filename = '%s_%s_to_%s_%ss.json' % (
            metric, self.start_time, self.end_time, self.resolution)
        fileopt.write_file(os.path.join(
            self.outdir, metric_filename), response)
        logging.debug("Saved data for key '%s'." % metric)

    def run_collecting(self):
        if self.resolution < 15.0:
            logging.warning(
                "Sampling resolution < 15s don't increase accuracy but data size.")
        pool = mp.Pool(self.proc_num)
        metric_names = self.get_label_names()
        pool.map_async(unwrap_self_f, zip(
            [self] * len(metric_names), metric_names))
        pool.close()
        pool.join()


# a trick to use multiprocessing.Pool inside a class
# see http://www.rueckstiess.net/research/snippets/show/ca1d7d90 for details
def unwrap_self_f(arg, **kwarg):
    return PromMetrics.query_worker(*arg, **kwarg)
