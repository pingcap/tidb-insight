package main

import (
	"io/ioutil"
	"strconv"
	"strings"
)

// Version infomation
var (
	// InsightGitBranch is initialized during make
	InsightGitBranch = "Not Provided"

	// InsightGitCommit is initialized during make
	InsightGitCommit = "Not Provided"

	// InsightBuildDate is initialized during make
	InsightBuildTime = "Not Provided"
)

func GetSysUptime() (float64, float64, error) {
	contents, err := ioutil.ReadFile("/proc/uptime")
	if err != nil {
		return 0, 0, err
	}
	timeStrings := strings.Split(string(contents), "\n")
	timerCounts := strings.Split(string(timeStrings[0]), " ")
	uptime, err := strconv.ParseFloat(timerCounts[0], 64)
	if err != nil {
		return 0, 0, err
	}
	idleTime, err := strconv.ParseFloat(timerCounts[1], 64)
	if err != nil {
		return 0, 0, err
	}
	return uptime, idleTime, err
}
