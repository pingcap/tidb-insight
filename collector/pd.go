// tidb-insight project pd.go
package main

import (
	"bytes"
	"log"
	"os/exec"
	"strings"
)

// PDMeta is the metadata struct of a PD server
type PDMeta struct {
	ReleaseVer string `json:"release_version,omitempty"`
	GitCommit  string `json:"git_commit,omitempty"`
	GitBranch  string `json:"git_branch,omitempty"`
	BuildTime  string `json:"utc_build_time,omitempty"`
}

func getPDVersion() PDMeta {
	var pdVer PDMeta
	pdProc, err := getProcessesByName("pd-server")
	if err != nil {
		log.Fatal(err)
	}
	if pdProc == nil {
		return pdVer
	}
	file, err := pdProc.Exe()
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
		info := strings.Split(line, ":")
		if len(info) <= 1 {
			continue
		}
		switch info[0] {
		case "Release Version":
			pdVer.ReleaseVer = strings.TrimSpace(info[1])
		case "Git Commit Hash":
			pdVer.GitCommit = strings.TrimSpace(info[1])
		case "Git Branch":
			pdVer.GitBranch = strings.TrimSpace(info[1])
		case "UTC Build Time":
			pdVer.BuildTime = strings.TrimSpace(strings.Join(info[1:], ":"))
		default:
			continue
		}
	}

	return pdVer
}
