### Makefile for collector
GOPKG=github.com/pingcap/tidb-insight/collector
ifeq "$(GOBIN)" ""
    GO    := go
else
    GO    := $(GOBIN)
endif
GOOS    := $(if $(GOOS),$(GOOS),linux)
GOARCH  := $(if $(GOARCH),$(GOARCH),amd64)
GOENV   := GO111MODULE=on CGO_ENABLED=1 GOOS=$(GOOS) GOARCH=$(GOARCH)
GOBUILD   := $(GOENV) $(GO) build $(BUILD_FLAGS)

COMMIT    := $(shell git describe --no-match --always --dirty)
BRANCH    := $(shell git rev-parse --abbrev-ref HEAD)

LDFLAGS   += -X "$(GOPKG)/insight.GitBranch=$(BRANCH)"
LDFLAGS   += -X "$(GOPKG)/insight.GitCommit=$(COMMIT)"

default: release

all: default

debug:
	$(GOBUILD) -ldflags '$(LDFLAGS)' \
		-o ../bin/collector \
		collector.go

release:
	$(GOBUILD) -ldflags '-s -w $(LDFLAGS)' \
		-o ../bin/collector \
		collector.go

static:
	$(GOBUILD) -ldflags '-s -w -extldflags "-static" $(LDFLAGS)' \
		-o ../bin/collector \
		collector.go

