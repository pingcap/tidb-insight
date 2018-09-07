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

import multiprocessing as mp

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
        self.proc_num = args.proc_num if args.proc_num else int(
            mp.cpu_count() + 1)

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

    def exec_importer(self, file=None, chunk_size=2000):
        if not file:
            logging.fatal("No file specified.")
            return (None, "No metric dump file specified to load.")
        base_dir = os.path.join(util.pwd(), "../")
        importer = os.path.join(base_dir, "bin/prom2influx")
        cmd = [importer,
               "-db", self.db_name,
               "-host", self.host,
               "-port", "%s" % self.port,
               "-chunk", "%s" % chunk_size,  # chunk size of one write request
               "-file", file
               ]
        logging.debug("Running cmd: %s" % ' '.join(cmd))
        return util.run_cmd(cmd)

    def importer_worker(self, filename):
        # all dumped files are in 'prometheus' sub-directory
        if not filename or not filename.endswith('.json') or 'prometheus' not in filename:
            return
        stderr = self.exec_importer(filename)[1]
        if stderr and "Request Entity Too Large" in stderr.decode('utf-8'):
            logging.info("Write to DB failed, retry for once...")
            retry_stderr = self.exec_importer(filename, chunk_size=100)[1]
            if not retry_stderr:
                logging.info("Retry succeeded.")
            else:
                logging.warning("Retry failed, stderr is: '%s'" %
                                retry_stderr)
        elif stderr:
            logging.warning(stderr)

    def run_importing(self):
        logging.info("Metrics will be imported to database '%s'." %
                     self.db_name)

        def file_list(dir=None):
            f_list = []
            for file in fileopt.list_dir(dir):
                if os.path.isdir(file):
                    f_list += file_list(file)
                else:
                    f_list.append(file)
            return f_list

        pool = mp.Pool(self.proc_num)
        files = file_list(self.datadir)
        pool.map_async(unwrap_self_f, zip([self] * len(files), files))
        pool.close()
        pool.join()


# a trick to use multiprocessing.Pool inside a class
# see http://www.rueckstiess.net/research/snippets/show/ca1d7d90 for details
def unwrap_self_f(arg, **kwarg):
    return PromDump.importer_worker(*arg, **kwarg)
