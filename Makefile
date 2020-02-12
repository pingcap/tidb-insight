### Makefile for tidb-insight
.PHONY: collector tools

GOOS    := $(if $(GOOS),$(GOOS),linux)
GOARCH  := $(if $(GOARCH),$(GOARCH),amd64)
HOSTARCH:= $(if $(HOSTARCH),$(HOSTARCH),amd64)

default: collector tools

debug: collector tools

all: default

collector:
	GOOS=$(GOOS) GOARCH=$(GOARCH) HOSTARCH=$(HOSTARCH) $(MAKE) -C collector $(MAKECMDGOALS)

tools:
	GOOS=$(GOOS) GOARCH=$(GOARCH) HOSTARCH=$(HOSTARCH) $(MAKE) -C tools $(MAKECMDGOALS)
	$(MAKE) -C tools/vmtouch $(MAKECMDGOALS)
	install -Dm755 tools/vmtouch/vmtouch bin/

package:
	GOOS=$(GOOS) GOARCH=$(GOARCH) HOSTARCH=$(HOSTARCH) ./package.sh

clean:
	rm -rf bin
	$(MAKE) -C tools/vmtouch $(MAKECMDGOALS)
