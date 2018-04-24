// tidb-insight project pd.go
package main

import (
	"bytes"
	"log"
	"os/exec"
	"strings"
)

type PDMeta struct {
	ReleaseVer string `json:"release_version,omitempty"`
	GitCommit  string `json:"git_commit,omitempty"`
	GitBranch  string `json:"git_branch,omitempty"`
	BuildTime  string `json:"utc_build_time,omitempty"`
}

func getPDVersion() PDMeta {
	var pd_ver PDMeta
	pd_proc, err := getProcessesByName("pd-server")
	if err != nil {
		log.Fatal(err)
	}
	if pd_proc == nil {
		return pd_ver
	}
	file, err := pd_proc.Exe()
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
			pd_ver.ReleaseVer = strings.TrimSpace(_tmp[1])
		case "Git Commit Hash":
			pd_ver.GitCommit = strings.TrimSpace(_tmp[1])
		case "Git Branch":
			pd_ver.GitBranch = strings.TrimSpace(_tmp[1])
		case "UTC Build Time":
			pd_ver.BuildTime = strings.TrimSpace(strings.Join(_tmp[1:], ":"))
		default:
			continue
		}
	}

	return pd_ver
}
