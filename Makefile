### Makefile for tidb-insight
.PHONY: collector

default: collector

debug: collector

all: default

collector:
	$(MAKE) -C collector $(MAKECMDGOALS)
