### Makefile for tidb-insight
.PHONY: collector

default: collector

debug: collector

all: default

collector:
	$(MAKE) -C collector $(MAKECMDGOALS)

package:
	./package.sh 2>package.err.log
