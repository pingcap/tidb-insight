// tidb-insight project tikv.go
package main

import (
	"bytes"
	"log"
	"os/exec"
	"strings"
)

type TiKVMeta struct {
	ReleaseVer  string `json:"release_version"`
	GitCommit   string `json:"git_commit"`
	GitBranch   string `json:"git_branch"`
	BuildTime   string `json:"utc_build_time"`
	RustVersion string `json:"rust_version"`
}

func getTiKVVersion() TiKVMeta {
	var tikv_ver TiKVMeta
	tikv_proc, err := getProcessesByName("tikv-server")
	if err != nil {
		log.Fatal(err)
	}
	file, err := tikv_proc.Exe()
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
			tikv_ver.ReleaseVer = strings.TrimSpace(_tmp[1])
		case "Git Commit Hash":
			tikv_ver.GitCommit = strings.TrimSpace(_tmp[1])
		case "Git Commit Branch":
			tikv_ver.GitBranch = strings.TrimSpace(_tmp[1])
		case "UTC Build Time":
			tikv_ver.BuildTime = strings.TrimSpace(strings.Join(_tmp[1:], ":"))
		case "Rust Version":
			tikv_ver.RustVersion = strings.TrimSpace(_tmp[1])
		default:
			continue
		}
	}

	return tikv_ver
}
