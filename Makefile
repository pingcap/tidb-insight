### Makefile for tidb-insight
.PHONY: collector tools

GOOS    := $(if $(GOOS),$(GOOS),linux)
GOARCH  := $(if $(GOARCH),$(GOARCH),amd64)
HOSTARCH:= $(if $(HOSTARCH),$(HOSTARCH),amd64)

default: collector

debug: collector tools

static: collector tools

all: default tools

collector:
	$(MAKE) -C collector ${MAKECMDGOALS}

tools:
	$(MAKE) -C tools ${MAKECMDGOALS}

package:
	GOOS=$(GOOS) GOARCH=$(GOARCH) HOSTARCH=$(HOSTARCH) ./package.sh

clean:
	rm -rf bin
	$(MAKE) -C tools/vmtouch $(MAKECMDGOALS)
