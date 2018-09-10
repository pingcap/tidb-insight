// This tool receives JSON metrics of Prometheus from stdin and writes them
// to a influxdb server

package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"

	influx "github.com/influxdata/influxdb/client/v2"
	"github.com/prometheus/common/model"
)

type options struct {
	Host   string
	Port   string
	User   string
	Passwd string
	DBName string
	File   string
	Chunk  int
}

type promResult struct {
	ResultType string
	Result     model.Matrix
}

type promDump struct {
	Status string
	Data   promResult
}

func parseOpts() options {
	influxHost := flag.String("host", "localhost", "The host of influxdb.")
	influxPort := flag.String("port", "8086", "The port of influxdb.")
	influxUser := flag.String("user", "", "The username of influxdb.")
	influxPass := flag.String("passwd", "", "The password of user.")
	influxDB := flag.String("db", "tidb-insight", "The database name of imported metrics.")
	influxFile := flag.String("file", "", "The dumped metric JSON file to load.")
	influxChunk := flag.Int("chunk", 2000, "The chunk size of writing.")
	flag.Parse()

	var opts options
	opts.Host = *influxHost
	opts.Port = *influxPort
	opts.User = *influxUser
	opts.Passwd = *influxPass
	opts.DBName = *influxDB
	opts.File = *influxFile
	opts.Chunk = *influxChunk
	return opts
}

// queryDB convenience function to query the database
func queryDB(clnt influx.Client, db_name string, cmd string) (res []influx.Result, err error) {
	q := influx.Query{
		Command:  cmd,
		Database: db_name,
	}
	if response, err := clnt.Query(q); err == nil {
		if response.Error() != nil {
			return res, response.Error()
		}
		res = response.Results
	} else {
		return res, err
	}
	return res, nil
}

func slicePoints(data []*influx.Point, chunkSize int) [][]*influx.Point {
	var result [][]*influx.Point
	for i := 0; i < len(data); i += chunkSize {
		endPos := i + chunkSize
		if endPos > len(data) {
			endPos = len(data)
		}
		result = append(result, data[i:endPos])
	}
	return result
}

func newClient(opts options) influx.Client {
	// connect to influxdb
	client, err := influx.NewHTTPClient(influx.HTTPConfig{
		Addr:     "http://" + opts.Host + ":" + opts.Port,
		Username: opts.User,
		Password: opts.Passwd,
	})
	if err != nil {
		log.Fatal(err)
	}
	return client
}

func buildPoints(series *model.SampleStream, client influx.Client,
	opts options) []*influx.Point {
	var ptList []*influx.Point
	raw_tags := series.Metric
	tags := make(map[string]string)
	for k, v := range raw_tags {
		tags[string(k)] = string(v)
	}
	tags["cluster"] = opts.DBName
	tags["monitor"] = "prometheus"
	measurement := tags["__name__"]
	for _, point := range series.Values {
		timestamp := point.Timestamp.Time()
		fields := map[string]interface{}{
			// model.SampleValue is alias of float64
			"value": float64(point.Value),
		}
		if pt, err := influx.NewPoint(measurement, tags, fields,
			timestamp); err == nil {
			ptList = append(ptList, pt)
		} // errored points are ignored
	}
	return ptList
}

func writeBatchPoints(data promDump, opts options) error {
	for _, series := range data.Data.Result {
		client := newClient(opts)
		ptList := buildPoints(series, client, opts)

		for _, chunk := range slicePoints(ptList, opts.Chunk) {
			// create influx.Client and close it every time we write a BatchPoints
			// series to reduce memory usage on large dataset
			bp, err := influx.NewBatchPoints(influx.BatchPointsConfig{
				Database:  opts.DBName,
				Precision: "s",
			})
			if err != nil {
				return err
			}
			bp.AddPoints(chunk)
			// write batch points to influxdb
			if err := client.Write(bp); err != nil {
				return err
			}
		}
		client.Close()
	}
	return nil
}

func main() {
	opts := parseOpts()

	// read JSON data from file
	input, err := ioutil.ReadFile(opts.File)
	if err != nil {
		log.Fatal(err)
	}

	// decode JSON
	var data promDump
	if err = json.Unmarshal(input, &data); err != nil {
		log.Fatal(err)
	}

	// connect to influxdb
	client := newClient(opts)
	// create database has no side effect if database already exist
	_, err = queryDB(client, opts.DBName, fmt.Sprintf("CREATE DATABASE %s", opts.DBName))
	if err != nil {
		log.Fatal(err)
	}
	client.Close()

	if err := writeBatchPoints(data, opts); err != nil {
		log.Fatal(err)
	}
}
