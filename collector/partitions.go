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

type BlockDev struct {
	// similiar to blkdev_cxt in lsblk (from util-linux)
	Name      string     `json:"name,omitempty"`
	Partition bool       `json:"partition,omitempty"`
	Mount     MountInfo  `json:"mount,omitempty"`
	UUID      string     `json:"uuid,omitempty"`
	Size      uint64     `json:"size,omitempty"`
	SubDev    []BlockDev `json:"subdev,omitempty"`
	Holder    []string   `json:"holder_of,omitempty"`
	Slave     []string   `json:"slave_of,omitempty"`
}

type MountInfo struct {
	MountPoint string `json:"mount_point,omitempty"`
	FSType     string `json:"filesystem,omitempty"`
	Options    string `json:"mount_options,omitempty"`
}

const sysClassBlock = "/sys/block"

func GetPartitionStats() []BlockDev {
	part_stats := make([]BlockDev, 0)
	if dir_sys_blk, err := os.Lstat(sysClassBlock); err == nil &&
		dir_sys_blk.IsDir() {
		fi, _ := os.Open(sysClassBlock)
		block_devs, _ := fi.Readdir(0)
		for _, blk := range block_devs {
			var blkdev BlockDev
			if blkdev.getBlockDevice(blk, nil) {
				part_stats = append(part_stats, blkdev)
			}
		}
		matchUUIDs(part_stats, checkUUIDs())
		matchMounts(part_stats, checkMounts())
	}
	return part_stats
}

func (blkdev *BlockDev) getBlockDevice(blk os.FileInfo, parent os.FileInfo) bool {
	var fullpath string
	var dev string
	if parent != nil {
		fullpath = path.Join(sysClassBlock, parent.Name(), blk.Name())
		dev = fullpath
	} else {
		fullpath = path.Join(sysClassBlock, blk.Name())
		dev, _ = os.Readlink(fullpath)
	}

	if strings.HasPrefix(dev, "../devices/virtual/") &&
		(strings.Contains(dev, "ram") ||
			strings.Contains(dev, "loop")) {
		return false
	}

	// open the dir
	var fi *os.File
	if parent != nil {
		fi, _ = os.Open(dev)
	} else {
		fi, _ = os.Open(path.Join(sysClassBlock, dev))
	}
	subfiles, err := fi.Readdir(0)
	if err != nil {
		return false
	}

	// check for sub devices
	for _, subfile := range subfiles {
		// check if this is a partition
		if subfile.Name() == "partition" {
			blkdev.Partition = true
		}

		// populate subdev
		if strings.HasPrefix(subfile.Name(), blk.Name()) {
			var subblk BlockDev
			subblk.getBlockDevice(subfile, blk)
			blkdev.SubDev = append(blkdev.SubDev, subblk)
		}
	}

	blkdev.Name = blk.Name()
	blksize, err := strconv.Atoi(si.SlurpFile(path.Join(fullpath, "size")))
	if err == nil {
		blkdev.Size = uint64(blksize)
	}

	slaves, holders := listDeps(blk.Name())
	if len(slaves) > 0 {
		for _, slave := range slaves {
			blkdev.Slave = append(blkdev.Slave, slave.Name())
		}
	}
	if len(holders) > 0 {
		for _, holder := range holders {
			blkdev.Holder = append(blkdev.Holder, holder.Name())
		}
	}

	return true
}

func listDeps(blk string) ([]os.FileInfo, []os.FileInfo) {
	fi_slaves, _ := os.Open(path.Join(sysClassBlock, blk, "slaves"))
	fi_holders, _ := os.Open(path.Join(sysClassBlock, blk, "holders"))
	slaves, _ := fi_slaves.Readdir(0)
	holders, _ := fi_holders.Readdir(0)
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
	disk_by_uuid := make(map[string]string)
	for _, link := range links {
		if link.IsDir() {
			continue
		}
		blk, err := os.Readlink(path.Join(sysDiskUUID, link.Name()))
		if err != nil {
			continue
		}
		blkname := strings.TrimPrefix(blk, "../../")
		disk_by_uuid[blkname] = link.Name()
	}
	return disk_by_uuid
}

func matchUUIDs(devs []BlockDev, disk_by_uuid map[string]string) {
	if len(devs) < 1 || disk_by_uuid == nil {
		return
	}

	// match devs to their UUIDs
	for i := 0; i < len(devs); i++ {
		devs[i].UUID = disk_by_uuid[devs[i].Name]

		// sub devices
		if len(devs[i].SubDev) < 1 {
			continue
		}
		matchUUIDs(devs[i].SubDev, disk_by_uuid)
	}
}

func checkMounts() map[string]MountInfo {
	raw, err := ioutil.ReadFile("/proc/mounts")
	if err != nil {
		return nil
	}
	raw_lines := strings.Split(string(raw), "\n")
	mount_points := make(map[string]MountInfo)

	for _, line := range raw_lines {
		_tmp := strings.Split(line, " ")
		if len(_tmp) < 6 {
			continue
		}
		var mp MountInfo
		mp.MountPoint = _tmp[1]
		mp.FSType = _tmp[2]
		mp.Options = _tmp[3]
		_devpath := strings.Split(_tmp[0], "/")
		if len(_devpath) < 1 {
			continue
		}
		_devname := _devpath[len(_devpath)-1:][0]
		mount_points[_devname] = mp
	}

	// check for swap partitions
	// note: swap file is not supported yet, as virtual block devices
	// are excluded from final result
	if swaps, err := ioutil.ReadFile("/proc/swaps"); err == nil {
		swap_lines := strings.Split(string(swaps), "\n")
		for i, line := range swap_lines {
			// skip table headers and empty line
			if i == 0 ||
				line == "" {
				continue
			}
			_tmp := strings.Fields(line)
			_devpath := strings.Split(_tmp[0], "/")
			if len(_devpath) < 1 {
				continue
			}
			var mp MountInfo
			mp.MountPoint = "[SWAP]"
			mp.FSType = "swap"
			_devname := _devpath[len(_devpath)-1:][0]
			mount_points[_devname] = mp
		}
	}

	return mount_points
}

func matchMounts(devs []BlockDev, mount_points map[string]MountInfo) {
	if len(devs) < 1 || mount_points == nil {
		return
	}

	for i := 0; i < len(devs); i++ {
		devs[i].Mount = mount_points[devs[i].Name]

		// sub devices
		if len(devs[i].SubDev) < 1 {
			continue
		}
		matchMounts(devs[i].SubDev, mount_points)
	}
}
