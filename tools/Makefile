### Makefile for tools

ifeq "$(GOBIN)" ""
    GO  := go
else
    GO  := $(GOBIN)
endif
GOOS    := $(if $(GOOS),$(GOOS),linux)
GOARCH  := $(if $(GOARCH),$(GOARCH),amd64)
GOENV   := GO111MODULE=on CGO_ENABLED=0 GOOS=$(GOOS) GOARCH=$(GOARCH)
GOBUILD := $(GOENV) $(GO) build $(BUILD_FLAGS)
LDFLAGS += $(EXTRA_LDFLAGS)

default: release vmtouch

tools: default

debug:
	$(GOBUILD) -ldflags '$(LDFLAGS)' \
		-o ../bin/prom2influx \
		prom2influx.go

release:
	$(GOBUILD) -ldflags '-s -w $(LDFLAGS)' \
		-o ../bin/prom2influx \
		prom2influx.go

static:
	$(GOBUILD) -ldflags '-s -w -extldflags "-static" $(LDFLAGS)' \
		-o ../bin/prom2influx \
		prom2influx.go

.PHONY: vmtouch

vmtouch:
	$(MAKE) -C vmtouch vmtouch
	install -Dm755 vmtouch/vmtouch ../bin/vmtouch
