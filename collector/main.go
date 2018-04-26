// Copyright 2018 PingCAP, Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// See the License for the specific language governing permissions and
// limitations under the License.

package main

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/AstroProfundis/sysinfo"
)

type meta struct {
	Timestamp time.Time `json:"timestamp"`
	SiVer     string    `json:"sysinfo_ver"`
	TiDBVer   TiDBMeta  `json:"tidb"`
	TiKVVer   TiKVMeta  `json:"tikv"`
	PDVer     PDMeta    `json:"pd"`
}

type metrics struct {
	meta       meta            `json:"meta"`
	SysInfo    sysinfo.SysInfo `json:"sysinfo"`
	Partitions []BlockDev      `json:"partitions"`
	ProcStats  []ProcessStat   `json:"proc_stats"`
}

func main() {
	var metric metrics

	metric.getMeta()
	metric.SysInfo.GetSysInfo()
	metric.Partitions = GetPartitionStats()
	metric.ProcStats = GetProcStats()

	data, err := json.MarshalIndent(&metric, "", "  ")
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(string(data))
}

func (metric *metrics) getMeta() {
	metric.meta.Timestamp = time.Now()
	metric.meta.SiVer = sysinfo.Version
	metric.meta.TiDBVer = getTiDBVersion()
	metric.meta.TiKVVer = getTiKVVersion()
	metric.meta.PDVer = getPDVersion()
}
