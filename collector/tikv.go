// tidb-insight project tikv.go
package main

import (
	"bytes"
	"log"
	"os/exec"
	"strings"
)

// TiKVMeta is the metada struct of a TiKV server
type TiKVMeta struct {
	ReleaseVer  string `json:"release_version,omitempty"`
	GitCommit   string `json:"git_commit,omitempty"`
	GitBranch   string `json:"git_branch,omitempty"`
	BuildTime   string `json:"utc_build_time,omitempty"`
	RustVersion string `json:"rust_version,omitempty"`
}

func getTiKVVersion() TiKVMeta {
	var tikvVer TiKVMeta
	tikvProc, err := getProcessesByName("tikv-server")
	if err != nil {
		log.Fatal(err)
	}
	if tikvProc == nil {
		return tikvVer
	}
	file, err := tikvProc.Exe()
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
			tikvVer.ReleaseVer = strings.TrimSpace(info[1])
		case "Git Commit Hash":
			tikvVer.GitCommit = strings.TrimSpace(info[1])
		case "Git Commit Branch":
			tikvVer.GitBranch = strings.TrimSpace(info[1])
		case "UTC Build Time":
			tikvVer.BuildTime = strings.TrimSpace(strings.Join(info[1:], ":"))
		case "Rust Version":
			tikvVer.RustVersion = strings.TrimSpace(info[1])
		default:
			continue
		}
	}

	return tikvVer
}
