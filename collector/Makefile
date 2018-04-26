### Makefile for collector

# Ensure GOPATH is set before running build process.
ifeq "$(GOPATH)" ""
    $(error Please set the environment variable GOPATH before running `make`)
endif

GO        := go
GOBUILD   := GOPATH=$(GOPATH) $(GO) build
GOVER     := $(shell $(GO) version)

COMMIT    := $(shell git rev-parse HEAD)
BRANCH    := $(shell git rev-parse --abbrev-ref HEAD)
BUILDTIME := $(shell date -u '+%Y-%m-%d %I:%M:%S')

LDFLAGS   += -X "main.InsightGitBranch=$(BRANCH)"
LDFLAGS   += -X "main.InsightGitCommit=$(COMMIT)"
LDFLAGS   += -X "main.InsightBuildTime=$(BUILDTIME)"
LDFLAGS   += -X "main.InsightGoVersion=$(GOVER)"

default: release

all: default

debug:
	$(GOBUILD) -ldflags '$(LDFLAGS)' \
		-o ../bin/collector \
		-i *.go

release:
	$(GOBUILD) -ldflags '-s -w -extldflags "-static" $(LDFLAGS)' \
		-o ../bin/collector \
		-i *.go
