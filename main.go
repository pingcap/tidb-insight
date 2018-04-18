// tidb-metrics-collector project main.go
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	//"github.com/AstroProfundis/sysinfo"
	"../../go/sysinfo"
)

type Meta struct {
	Timestamp time.Time `json:"timestamp"`
	SiVer     string    `json:"sysinfo_ver"`
}

type Metrics struct {
	Meta    Meta            `json:"meta"`
	SysInfo sysinfo.SysInfo `json:"sysinfo"`
}

func main() {
	var metrics Metrics

	metrics.GetMeta()
	metrics.SysInfo.GetSysInfo()

	data, err := json.MarshalIndent(&metrics, "", "  ")
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(string(data))
}

func (metrics *Metrics) GetMeta() {
	metrics.Meta.Timestamp = time.Now()
	metrics.Meta.SiVer = sysinfo.Version
}
