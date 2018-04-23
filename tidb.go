// tidb-insight project tidb.go
package main

import (
	"bytes"
	"log"
	"os/exec"
	"strings"
)

type TiDBMeta struct {
	ReleaseVer string `json:"release_version"`
	GitCommit  string `json:"git_commit"`
	GitBranch  string `json:"git_branch"`
	BuildTime  string `json:"utc_build_time"`
	GoVersion  string `json:"go_version"`
}

func getTiDBVersion() TiDBMeta {
	var tidb_ver TiDBMeta
	tidb_proc, err := getProcessesByName("tidb-server")
	if err != nil {
		log.Fatal(err)
	}
	if tidb_proc == nil {
		return tidb_ver
	}
	file, err := tidb_proc.Exe()
	if err != nil {
		log.Fatal(err)
	}

	cmd := exec.Command(file, "-V")
	var out bytes.Buffer
	cmd.Stdout = &out
	err = cmd.Run()
	if err != nil {
		log.Fatal(err)
	}

	output := strings.Split(out.String(), "\n")
	for _, line := range output {
		_tmp := strings.Split(line, ":")
		if len(_tmp) <= 1 {
			continue
		}
		switch _tmp[0] {
		case "Release Version":
			tidb_ver.ReleaseVer = strings.TrimSpace(_tmp[1])
		case "Git Commit Hash":
			tidb_ver.GitCommit = strings.TrimSpace(_tmp[1])
		case "Git Commit Branch":
			tidb_ver.GitBranch = strings.TrimSpace(_tmp[1])
		case "UTC Build Time":
			tidb_ver.BuildTime = strings.TrimSpace(strings.Join(_tmp[1:], ":"))
		case "GoVersion":
			_tmp_trimmed := strings.TrimSpace(_tmp[1])
			tidb_ver.GoVersion = strings.TrimPrefix(_tmp_trimmed, "go version ")
		default:
			continue
		}
	}

	return tidb_ver
}
