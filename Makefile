### Makefile for tidb-insight
.PHONY: collector tools

default: collector tools

debug: collector tools

all: default

collector:
	$(MAKE) -C collector $(MAKECMDGOALS)

tools:
	$(MAKE) -C tools $(MAKECMDGOALS)
	$(MAKE) -C tools/vmtouch $(MAKECMDGOALS)
	install -Dm755 tools/vmtouch/vmtouch bin/

package:
	./package.sh

clean:
	rm -rf bin
	$(MAKE) -C tools/vmtouch $(MAKECMDGOALS)
