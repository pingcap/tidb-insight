// Copyright © 2018 PingCAP Inc.
//
// Use of this source code is governed by an MIT-style license that can be found in the LICENSE file.

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/AstroProfundis/sysinfo"
)

type Meta struct {
	Timestamp time.Time `json:"timestamp"`
	SiVer     string    `json:"sysinfo_ver"`
	TiDBVer   TiDBMeta  `json:"tidb"`
	TiKVVer   TiKVMeta  `json:"tikv"`
	PDVer     PDMeta    `json:"pd"`
}

type Metrics struct {
	Meta      Meta            `json:"meta"`
	SysInfo   sysinfo.SysInfo `json:"sysinfo"`
	ProcStats []ProcessStat   `json:"proc_stats"`
}

func main() {
	var metrics Metrics

	metrics.GetMeta()
	metrics.SysInfo.GetSysInfo()
	metrics.ProcStats = GetProcStats()

	data, err := json.MarshalIndent(&metrics, "", "  ")
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(string(data))
}

func (metrics *Metrics) GetMeta() {
	metrics.Meta.Timestamp = time.Now()
	metrics.Meta.SiVer = sysinfo.Version
	metrics.Meta.TiDBVer = getTiDBVersion()
	metrics.Meta.TiKVVer = getTiKVVersion()
	metrics.Meta.PDVer = getPDVersion()
}
