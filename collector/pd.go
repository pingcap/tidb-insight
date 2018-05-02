// tidb-insight project pd.go
package main

import (
	"bytes"
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
		printErr(err)
	}
	if pdProc == nil {
		return pdVer
	}
	file, err := pdProc.Exe()
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
			pdVer.ReleaseVer = strings.TrimSpace(tmp[1])
		case "Git Commit Hash":
			pdVer.GitCommit = strings.TrimSpace(tmp[1])
		case "Git Branch":
			pdVer.GitBranch = strings.TrimSpace(tmp[1])
		case "UTC Build Time":
			pdVer.BuildTime = strings.TrimSpace(strings.Join(tmp[1:], ":"))
		default:
			continue
		}
	}

	return pdVer
}
