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
	"runtime"
	"time"

	"github.com/AstroProfundis/sysinfo"
)

type Meta struct {
	Timestamp time.Time `json:"timestamp"`
	SiVer     string    `json:"sysinfo_ver"`
	GitBranch string    `json:"git_branch"`
	GitCommit string    `json:"git_commit"`
	BuildTime string    `json:"utc_build_time"`
	GoVersion string    `json:"go_version"`
	TiDBVer   TiDBMeta  `json:"tidb"`
	TiKVVer   TiKVMeta  `json:"tikv"`
	PDVer     PDMeta    `json:"pd"`
}

type Metrics struct {
	Meta       Meta            `json:"meta"`
	SysInfo    sysinfo.SysInfo `json:"sysinfo"`
	Partitions []BlockDev      `json:"partitions"`
	ProcStats  []ProcessStat   `json:"proc_stats"`
}

func main() {
	var metric Metrics
	metric.getMetrics()

	data, err := json.MarshalIndent(&metric, "", "  ")
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(string(data))
}

func (metric *Metrics) getMetrics() {
	metric.Meta.getMeta()
	metric.SysInfo.GetSysInfo()
	metric.Partitions = GetPartitionStats()
	metric.ProcStats = GetProcStats()
}

func (meta *Meta) getMeta() {
	meta.Timestamp = time.Now()
	meta.SiVer = sysinfo.Version
	meta.GitBranch = InsightGitBranch
	meta.GitCommit = InsightGitCommit
	meta.BuildTime = InsightBuildTime
	meta.GoVersion = fmt.Sprintf("%s %s/%s", runtime.Version(), runtime.GOOS, runtime.GOARCH)
	meta.TiDBVer = getTiDBVersion()
	meta.TiKVVer = getTiKVVersion()
	meta.PDVer = getPDVersion()
}
