### Makefile for tools

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

default: release

all: default

debug:
	$(GOBUILD) -ldflags '$(LDFLAGS)' \
		-o ../bin/prom2influx \
		-i prom2influx.go

release:
	$(GOBUILD) -ldflags '-s -w $(LDFLAGS)' \
		-o ../bin/prom2influx \
		-i prom2influx.go

static:
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
	$(GOBUILD) -ldflags '-s -w -extldflags "-static" $(LDFLAGS)' \
		-o ../bin/prom2influx \
		-i prom2influx.go
