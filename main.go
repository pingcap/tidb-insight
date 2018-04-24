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
