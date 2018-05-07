// get partitions info of the system

package main

import (
	"io/ioutil"
	"os"
	"path"
	"strconv"
	"strings"

	si "github.com/AstroProfundis/sysinfo"
)

// BlockDev is similar to blkDev_cxt in lsblk (from util-linux)
// contains metadata of a block device
type BlockDev struct {
	Name      string     `json:"name,omitempty"`
	Partition bool       `json:"partition,omitempty"`
	Mount     MountInfo  `json:"mount,omitempty"`
	UUID      string     `json:"uuid,omitempty"`
	Size      uint64     `json:"size,omitempty"`
	SubDev    []BlockDev `json:"subdev,omitempty"`
	Holder    []string   `json:"holder_of,omitempty"`
	Slave     []string   `json:"slave_of,omitempty"`
}

// MountInfo is the metadata of a mounted device
type MountInfo struct {
	MountPoint string `json:"mount_point,omitempty"`
	FSType     string `json:"filesystem,omitempty"`
	Options    string `json:"mount_options,omitempty"`
}

const sysClassBlock = "/sys/block"

func GetPartitionStats() []BlockDev {
	partStats := make([]BlockDev, 0)
	if dirSysBlk, err := os.Lstat(sysClassBlock); err == nil &&
		dirSysBlk.IsDir() {
		fi, err := os.Open(sysClassBlock)
		if err != nil {
			printErr(err)
		}
		blockDevs, err := fi.Readdir(0)
		if err != nil {
			printErr(err)
		}
		for _, blk := range blockDevs {
			var blkDev BlockDev
			if blkDev.getBlockDevice(blk, nil) {
				partStats = append(partStats, blkDev)
			}
		}
		matchUUIDs(partStats, checkUUIDs())
		matchMounts(partStats, checkMounts())
	}
	return partStats
}

func (blkDev *BlockDev) getBlockDevice(blk os.FileInfo, parent os.FileInfo) bool {
	var fullpath string
	var dev string
	var err error
	if parent != nil {
		fullpath = path.Join(sysClassBlock, parent.Name(), blk.Name())
		dev = fullpath
	} else {
		fullpath = path.Join(sysClassBlock, blk.Name())
		dev, err = os.Readlink(fullpath)
		if err != nil {
			printErr(err)
		}
	}

	if strings.HasPrefix(dev, "../devices/virtual/") &&
		(strings.Contains(dev, "ram") ||
			strings.Contains(dev, "loop")) {
		return false
	}

	// open the dir
	var fi *os.File
	if parent != nil {
		fi, err = os.Open(dev)
		if err != nil {
			printErr(err)
		}
	} else {
		fi, err = os.Open(path.Join(sysClassBlock, dev))
		if err != nil {
			printErr(err)
		}
	}

	subfiles, err := fi.Readdir(0)
	if err != nil {
		printErr(err)
		return false
	}

	// check for sub devices
	for _, subfile := range subfiles {
		// check if this is a partition
		if subfile.Name() == "partition" {
			blkDev.Partition = true
		}

		// populate subdev
		if strings.HasPrefix(subfile.Name(), blk.Name()) {
			var subblk BlockDev
			subblk.getBlockDevice(subfile, blk)
			blkDev.SubDev = append(blkDev.SubDev, subblk)
		}
	}

	blkDev.Name = blk.Name()
	blkSize, err := strconv.Atoi(si.SlurpFile(path.Join(fullpath, "size")))
	if err == nil {
		blkDev.Size = uint64(blkSize)
	}

	slaves, holders := listDeps(blk.Name())
	if len(slaves) > 0 {
		for _, slave := range slaves {
			blkDev.Slave = append(blkDev.Slave, slave.Name())
		}
	}
	if len(holders) > 0 {
		for _, holder := range holders {
			blkDev.Holder = append(blkDev.Holder, holder.Name())
		}
	}

	return true
}

func listDeps(blk string) ([]os.FileInfo, []os.FileInfo) {
	fiSlaves, err := os.Open(path.Join(sysClassBlock, blk, "slaves"))
	if err != nil {
		printErr(err)
	}
	fiHolders, err := os.Open(path.Join(sysClassBlock, blk, "holders"))
	if err != nil {
		printErr(err)
	}
	slaves, err := fiSlaves.Readdir(0)
	if err != nil {
		printErr(err)
	}
	holders, err := fiHolders.Readdir(0)
	if err != nil {
		printErr(err)
	}
	return slaves, holders
}

func checkUUIDs() map[string]string {
	sysDiskUUID := "/dev/disk/by-uuid"
	fi, err := os.Open(sysDiskUUID)
	if err != nil {
		return nil
	}
	links, err := fi.Readdir(0)
	if err != nil {
		return nil
	}
	diskByUUID := make(map[string]string)
	for _, link := range links {
		if link.IsDir() {
			continue
		}
		blk, err := os.Readlink(path.Join(sysDiskUUID, link.Name()))
		if err != nil {
			continue
		}
		blkName := strings.TrimPrefix(blk, "../../")
		diskByUUID[blkName] = link.Name()
	}
	return diskByUUID
}

func matchUUIDs(devs []BlockDev, diskByUUID map[string]string) {
	if len(devs) < 1 || diskByUUID == nil {
		return
	}

	// match devs to their UUIDs
	for i := 0; i < len(devs); i++ {
		devs[i].UUID = diskByUUID[devs[i].Name]

		// sub devices
		if len(devs[i].SubDev) < 1 {
			continue
		}
		matchUUIDs(devs[i].SubDev, diskByUUID)
	}
}

func checkMounts() map[string]MountInfo {
	raw, err := ioutil.ReadFile("/proc/mounts")
	if err != nil {
		return nil
	}
	rawLines := strings.Split(string(raw), "\n")
	mountPoints := make(map[string]MountInfo)

	for _, line := range rawLines {
		tmp := strings.Split(line, " ")
		if len(tmp) < 6 {
			continue
		}
		var mp MountInfo
		mp.MountPoint = tmp[1]
		mp.FSType = tmp[2]
		mp.Options = tmp[3]
		devPath := strings.Split(tmp[0], "/")
		if len(devPath) < 1 {
			continue
		}
		devName := devPath[len(devPath)-1:][0]
		mountPoints[devName] = mp
	}

	// check for swap partitions
	// note: swap file is not supported yet, as virtual block devices
	// are excluded from final result
	if swaps, err := ioutil.ReadFile("/proc/swaps"); err == nil {
		swapLines := strings.Split(string(swaps), "\n")
		for i, line := range swapLines {
			// skip table headers and empty line
			if i == 0 ||
				line == "" {
				continue
			}
			devPath := strings.Split(strings.Fields(line)[0], "/")
			if len(devPath) < 1 {
				continue
			}
			var mp MountInfo
			mp.MountPoint = "[SWAP]"
			mp.FSType = "swap"
			devName := devPath[len(devPath)-1:][0]
			mountPoints[devName] = mp
		}
	}

	return mountPoints
}

func matchMounts(devs []BlockDev, mountPoints map[string]MountInfo) {
	if len(devs) < 1 || mountPoints == nil {
		return
	}

	for i := 0; i < len(devs); i++ {
		devs[i].Mount = mountPoints[devs[i].Name]

		// sub devices
		if len(devs[i].SubDev) < 1 {
			continue
		}
		matchMounts(devs[i].SubDev, mountPoints)
	}
}
