// tidb-insight project tidb.go
package main

import (
	"bytes"
	"os/exec"
	"strings"
)

// TiDBMeta is the metadata struct of a TiDB server
type TiDBMeta struct {
	ReleaseVer string `json:"release_version,omitempty"`
	GitCommit  string `json:"git_commit,omitempty"`
	GitBranch  string `json:"git_branch,omitempty"`
	BuildTime  string `json:"utc_build_time,omitempty"`
	GoVersion  string `json:"go_version,omitempty"`
}

func getTiDBVersion() TiDBMeta {
	var tidbVer TiDBMeta
	tidbProc, err := getProcessesByName("tidb-server")
	if err != nil {
		printErr(err)
	}
	if tidbProc == nil {
		return tidbVer
	}
	file, err := tidbProc.Exe()
	if err != nil {
		printErr(err)
	}

	cmd := exec.Command(file, "-V")
	var out bytes.Buffer
	cmd.Stdout = &out
	err = cmd.Run()
	if err != nil {
		printErr(err)
	}

	output := strings.Split(out.String(), "\n")
	for _, line := range output {
		tmp := strings.Split(line, ":")
		if len(tmp) <= 1 {
			continue
		}
		switch tmp[0] {
		case "Release Version":
			tidbVer.ReleaseVer = strings.TrimSpace(tmp[1])
		case "Git Commit Hash":
			tidbVer.GitCommit = strings.TrimSpace(tmp[1])
		case "Git Commit Branch":
			tidbVer.GitBranch = strings.TrimSpace(tmp[1])
		case "UTC Build Time":
			tidbVer.BuildTime = strings.TrimSpace(strings.Join(tmp[1:], ":"))
		case "GoVersion":
			tmpTrimed := strings.TrimSpace(tmp[1])
			tidbVer.GoVersion = strings.TrimPrefix(tmpTrimed, "go version ")
		default:
			continue
		}
	}

	return tidbVer
}
