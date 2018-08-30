# -*- coding: utf-8 -*-
# Re-import dumped Prometheus metric data (in plain or compressed
# JSON format) to a local influxdb instance.
# Imported data will be put into a dedicated (or specified) database
# for futher analysis.

import datetime
import json
import logging
import os
import random
import string
import zlib

from utils import fileopt
from utils import util


class PromDump():
    def __init__(self, args):
        # if db_name, else db_name = prom_dump_`date`
        self.host = args.host if args.host else 'localhost'
        self.port = args.port if args.port else 8086
        self.datadir = args.dir if args.dir else 'data'
        self.db_name = args.db if args.db else self.unique_dbname()
        self.user = args.user
        self.passwd = args.passwd

    # unique_dbname() generates a unique database name for importing, to prevents
    # overwritting of previous imported data
    def unique_dbname(self):
        dbname = []
        # universal prefix
        dbname.append('tidb_insight_prom')
        # current time
        dbname.append(datetime.datetime.now().strftime("%Y%m%d%H%M"))
        # a 4 digits random string
        dbname.append(''.join(random.choice(
            string.ascii_lowercase + string.digits) for _ in range(4)))

        return '_'.join(dbname)

    def load_dump(self):
        def file_list(dir=None):
            f_list = []
            for file in fileopt.list_dir(dir):
                if os.path.isdir(file):
                    f_list += file_list(file)
                else:
                    f_list.append(file)
            return f_list

        for file in file_list(self.datadir):
            if file.endswith('.json'):
                raw = fileopt.read_file(file)
            elif file.endswith('.dat'):
                raw = zlib.decompress(fileopt.read_file(file, 'rb'))
            else:
                logging.debug("Skip unrecorgnized file '%s'" % file)
                continue
            yield json.loads(raw)

    def exec_importer(self, data, chunk_size=2000):
        base_dir = os.path.join(util.pwd(), "../")
        importer = os.path.join(base_dir, "bin/prom2influx")
        cmd = [importer,
               "-db", self.db_name,
               "-host", self.host,
               "-port", "%s" % self.port,
               "-chunk", "%s" % chunk_size,  # chunk size of one write request
               ]
        logging.debug("Running cmd: %s" % ' '.join(cmd))
        return util.run_cmd(cmd, input=json.dumps(data).encode('utf-8'))

    def run_importing(self):
        logging.info("Metrics will be imported to database '%s'." %
                     self.db_name)

        for series in self.load_dump():
            if not series:
                continue
            stderr = self.exec_importer(series)[1]
            if stderr and "Request Entity Too Large" in stderr.decode('utf-8'):
                metric_name = series[0]["metric"]["__name__"]
                logging.info("Write to DB failed, retry for once...")
                retry_stderr = self.exec_importer(series, chunk_size=100)[1]
                if not retry_stderr:
                    logging.info("Retry succeeded for metric '%s'." %
                                 metric_name)
                else:
                    logging.warn("Retry failed for metric '%s', stderr is: '%s'" % (
                        metric_name, retry_stderr))
            elif stderr:
                logging.warn(stderr)
