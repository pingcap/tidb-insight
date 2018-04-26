.PHONY: collector
### Makefile for tidb-insight

# Ensure GOPATH is set before running build process.
ifeq "$(GOPATH)" ""
    $(error Please set the environment variable GOPATH before running `make`)
endif

CURDIR := $(shell pwd)

GO        := go
GOBUILD   := GOPATH=$(GOPATH) $(GO) build

COMMIT=$(shell git rev-parse HEAD)
BRANCH=$(shell git rev-parse --abbrev-ref HEAD)

default: collector

all: default

collector:
	$(GOBUILD) -o bin/collector -i collector/*.go
