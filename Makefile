### Makefile for tidb-insight
.PHONY: collector tools

GOOS    := $(if $(GOOS),$(GOOS),"")
GOARCH  := $(if $(GOARCH),$(GOARCH),"")
HOSTARCH:= $(if $(HOSTARCH),$(HOSTARCH),amd64)

default: collector

static: collector

collector:
	$(MAKE) -C collector ${MAKECMDGOALS}

tools:
	$(MAKE) -C tools ${MAKECMDGOALS}

package:
	GOOS=$(GOOS) GOARCH=$(GOARCH) HOSTARCH=$(HOSTARCH) ./package.sh

clean:
	rm -rf bin
	$(MAKE) -C tools/vmtouch $(MAKECMDGOALS)
