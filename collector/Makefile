### Makefile for collector

# Ensure GOPATH is set before running build process.
ifeq "$(GOPATH)" ""
    $(error Please set the environment variable GOPATH before running `make`)
endif

ifeq "$(GOBIN)" ""
    GO    := GOPATH=$(GOPATH) go
else
    GO    := GOPATH=$(GOPATH) $(GOBIN)
endif
GOBUILD   := $(GO) build

COMMIT    := $(shell git rev-parse HEAD)
BRANCH    := $(shell git rev-parse --abbrev-ref HEAD)
BUILDTIME := $(shell date -u '+%Y-%m-%d %I:%M:%S')

LDFLAGS   += -X "main.InsightGitBranch=$(BRANCH)"
LDFLAGS   += -X "main.InsightGitCommit=$(COMMIT)"
LDFLAGS   += -X "main.InsightBuildTime=$(BUILDTIME)"

default: release

all: default

debug:
	$(GOBUILD) -ldflags '$(LDFLAGS)' \
		-o ../bin/collector \
		-i *.go

release:
	$(GOBUILD) -ldflags '-w $(LDFLAGS)' \
		-o ../bin/collector \
		-i *.go

deps:
	$(GO) get ./...

static:
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
	$(GOBUILD) -ldflags '-s -w -extldflags "-static" $(LDFLAGS)' \
		-o ../bin/collector \
		-i *.go
