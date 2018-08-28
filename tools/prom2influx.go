// This tool receives JSON metrics of Prometheus from stdin and writes them
// to a influxdb server

package main

import (
	"encoding/json"
	"flag"

	"fmt"
	"io/ioutil"
	"log"
	"os"
	"time"

	influx "github.com/influxdata/influxdb/client/v2"
)

type options struct {
	Host   string
	Port   string
	User   string
	Passwd string
	DBName string
}

func parseOpts() options {
	influxHost := flag.String("host", "localhost", "The host of influxdb.")
	influxPort := flag.String("port", "8086", "The port of influxdb.")
	influxUser := flag.String("user", "", "The username of influxdb.")
	influxPass := flag.String("passwd", "", "The password of user.")
	influxDB := flag.String("db", "tidb-insight", "The database name of imported metrics.")
	flag.Parse()

	var opts options
	opts.Host = *influxHost
	opts.Port = *influxPort
	opts.User = *influxUser
	opts.Passwd = *influxPass
	opts.DBName = *influxDB
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

func buildPoints(data []map[string]interface{}, client influx.Client,
	opts options) (bp influx.BatchPoints, err error) {
	if bp, err := influx.NewBatchPoints(influx.BatchPointsConfig{
		Database:  opts.DBName,
		Precision: "s",
	}); err != nil {
		return nil, err
	}

	for _, series := range data {
		raw_tags := series["metric"].(map[string]interface{})
		tags := make(map[string]string)
		for k, v := range raw_tags {
			tags[k] = v.(string)
		}
		tags["cluster"] = opts.DBName
		tags["monitor"] = "prometheus"
		measurement := series["metric"].(map[string]interface{})["__name__"]
		for _, point := range series["values"].([]interface{}) {
			timestamp := point.([]interface{})[0].(float64)
			timepoint := time.Unix(int64(timestamp), 0)
			fields := map[string]interface{}{
				"value": point.([]interface{})[1].(string),
			}
			if pt, err := influx.NewPoint(measurement.(string), tags, fields,
				timepoint); err == nil {
				bp.AddPoint(pt)
				continue
			}
			return bp, err
		}
	}
	return bp, nil
}

func main() {
	opts := parseOpts()

	// connect to influxdb
	client, err := influx.NewHTTPClient(influx.HTTPConfig{
		Addr:     "http://" + opts.Host + ":" + opts.Port,
		Username: opts.User,
		Password: opts.Passwd,
	})
	if err != nil {
		log.Fatal(err)
	}
	defer client.Close()

	// read JSON data from stdin
	input, err := ioutil.ReadAll(os.Stdin)
	if err != nil {
		log.Fatal(err)
	}

	// decode JSON
	var data []map[string]interface{}
	if err = json.Unmarshal(input, &data); err != nil {
		log.Fatal(err)
	}

	bp, err := buildPoints(data, client, opts)
	if err != nil {
		log.Fatal(err)
	}

	// create database has no side effect if database already exist
	_, err = queryDB(client, opts.DBName, fmt.Sprintf("CREATE DATABASE %s", opts.DBName))
	if err != nil {
		log.Fatal(err)
	}

	// write batch points to influxdb
	if err := client.Write(bp); err != nil {
		log.Fatal(err)
	}
	fmt.Println(bp)
}
