### Makefile for collector

ifeq "$(GOBIN)" ""
    GO    := go
else
    GO    := $(GOBIN)
endif
GOOS    := $(if $(GOOS),$(GOOS),linux)
GOARCH  := $(if $(GOARCH),$(GOARCH),amd64)
GOENV   := GO111MODULE=on CGO_ENABLED=0 GOOS=$(GOOS) GOARCH=$(GOARCH)
GOBUILD   := $(GOENV) $(GO) build $(BUILD_FLAGS)

COMMIT    := $(shell git rev-parse HEAD)
BRANCH    := $(shell git rev-parse --abbrev-ref HEAD)
BUILDTIME := $(shell date -u '+%Y-%m-%d %I:%M:%S')

LDFLAGS   += -X "main.InsightGitBranch=$(BRANCH)"
LDFLAGS   += -X "main.InsightGitCommit=$(COMMIT)"

default: release

all: default

debug:
	$(GOBUILD) -ldflags '$(LDFLAGS)' \
		-o ../bin/collector

release:
	$(GOBUILD) -ldflags '-s -w $(LDFLAGS)' \
		-o ../bin/collector

static:
	$(GOBUILD) -ldflags '-s -w -extldflags "-static" $(LDFLAGS)' \
		-o ../bin/collector

