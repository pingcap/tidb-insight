### Makefile for tidb-insight
.PHONY: collector vmtouch

default: collector vmtouch

debug: collector vmtouch

all: default

collector:
	$(MAKE) -C collector $(MAKECMDGOALS)

vmtouch:
	$(MAKE) -C tools/vmtouch $(MAKECMDGOALS)

package:
	./package.sh 2>package.err.log
