# -*- coding: utf-8 -*-
# Re-import dumped Prometheus metric data (in plain or compressed
# JSON format) to a local influxdb instance.
# Imported data will be put into a dedicated (or specified) database
# for futher analysis.

import datetime
import influxdb
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
                logging.debug("Skipped unrecorgnized file '%s'" % file)
                continue
            yield json.loads(raw)

    def build_series(self):
        def format_prom_metric(key=None):
            points = []
            point = {'fields': {}}
            # build point header
            for metric in key:
                point['measurement'] = metric['metric']['__name__']
                point['tags'] = {
                    'cluster': self.db_name,
                    'monitor': 'prometheus',
                }
                for k, v in metric['metric'].items():
                    point['tags'][k] = v
                # build point values
                for value in metric['values']:
                    point['time'] = datetime.datetime.utcfromtimestamp(
                        value[0]).strftime('%Y-%m-%dT%H:%M:%SZ')
                    try:
                        point['fields']['value'] = float(value[1])
                    except ValueError:
                        point['fields']['value'] = value[1]
                    points.append(point.copy())
            return points

        for metric in self.load_dump():
            if not metric:
                continue
            fileopt.write_file("test", json.dumps(metric))
            cmd = ["/home/allen/dev/pingcap/tidb-insight/tools/prom2influx",
                        "-db", self.db_name,
                        "-host", self.host,
                        "-port", str(self.port)]
            logging.debug("Running cmd: %s" % ' '.join(cmd))
            stdout, stderr = util.run_cmd(cmd, input=json.dumps(metric))
            logging.debug("stdout: %s\nstderr: %s" % (len(stdout), len(stderr)))
            if stderr:
                logging.warn(stderr)
            yield format_prom_metric(metric)

    def write2influxdb(self):
        #client = influxdb.InfluxDBClient(
        #    host=self.host, port=self.port, username=self.user, password=self.passwd,
        #    database=self.db_name, timeout=30)
        # create_database has no effect if the database already exist
        #client.create_database(self.db_name)
        logging.info("Metrics will be imported to database '%s'." %
                     self.db_name)

        for series in self.build_series():
            if not series:
                continue
            try:
                print("series size: %s" % len(series))
                #fileopt.write_file("test", json.dumps(series))
                #client.write_points(series, batch_size=2000)
            except influxdb.exceptions.InfluxDBClientError as e:
                logging.warn(
                    "Write error for key '%s', data may be empty." % series[0]['measurement'])
                logging.debug(e)

    def run_importing(self):
        self.write2influxdb()
