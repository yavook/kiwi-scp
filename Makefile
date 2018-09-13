# *.conf file handling
CONF_WILDC:=$(wildcard $(PWD)/*.conf)
CONF_SOURCE:=$(patsubst %,. %;,$(CONF_WILDC))

# extraction of env variables from *.conf files
confvalue=$(shell $(CONF_SOURCE) echo -n $${$(1)})

# docker network name
CONF_DOCKERNET:=$(call confvalue,DOCKERNET)
ifeq ($(CONF_DOCKERNET),)
$(error DOCKERNET not set in $(CONF_WILDC))
endif

# persistent data directory
CONF_TARGETROOT:=$(call confvalue,TARGETROOT)
ifeq ($(CONF_TARGETROOT),)
$(error TARGETROOT not set in $(CONF_WILDC))
endif

# file to store docker network cidr
FILE_DOCKERNET:=$(CONF_TARGETROOT)/up-$(CONF_DOCKERNET)

# project directory handling
PROJ_WILDC:=$(wildcard *.docker)
PROJ_NAMES:=$(basename $(PROJ_WILDC))

# different complexities of commands with root privileges
# - in project directory
projsudo=cd "$<"; sudo bash -c "$(1)"
# - additionally with sourced *.conf files
confprojsudo=$(call projsudo,$(CONF_SOURCE) $(1))
# - only for compose: additionally with COMPOSE_PROJECT_NAME, CONFDIR and TARGETDIR set
sudocompose=$(call confprojsudo,COMPOSE_PROJECT_NAME="$(basename $<)" CONFDIR="$(CONF_TARGETROOT)/conf" TARGETDIR="$(CONF_TARGETROOT)/$<" docker-compose $(1))

#########
# TARGETS

# default target
.PHONY: all
all: purge-conf up

#########
# manage the docker network (container name local DNS)
$(FILE_DOCKERNET):
	sudo docker network create "$(CONF_DOCKERNET)" ||:
	sudo mkdir -p "$(CONF_TARGETROOT)"
	sudo chmod 700 "$(CONF_TARGETROOT)"
	sudo docker network inspect -f '{{(index .IPAM.Config 0).Subnet}}' "$(CONF_DOCKERNET)" | sudo tee "$@"

.PHONY: net-up
net-up: $(FILE_DOCKERNET)

.PHONY: net-down
net-down: down
	sudo docker network rm $(CONF_DOCKERNET)
	sudo rm $(FILE_DOCKERNET)

#########
# sync project config directory to variable folder
.PHONY: %-copyconf
%-copyconf: %.docker
	@if [ -d "$</conf" ]; then \
	  sudo rsync -r "$</conf" "$(CONF_TARGETROOT)"; \
	  echo "Synced '$</conf' to '$(CONF_TARGETROOT)'"; \
	fi

.PHONY: purge-conf
purge-conf:
	sudo rm -rf "$(CONF_TARGETROOT)/conf"

#########
# manage all projects
.PHONY: up down update
up: net-up $(patsubst %,%-up,$(PROJ_NAMES))
down: $(patsubst %,%-down,$(PROJ_NAMES))
update: $(patsubst %,%-update,$(PROJ_NAMES))

#########
# manage single project
.PHONY: %-up
%-up: %.docker %-copyconf
	$(call sudocompose,up -d $(x))

.PHONY: %-down
ifeq ($(x),)
%-down: %.docker
	$(call sudocompose,down)
else
%-down: %.docker
	$(call sudocompose,stop $(x))
	$(call sudocompose,rm -f $(x))
endif

.PHONY: %-pull
%-pull: %.docker
	$(call sudocompose,pull $(x))

.PHONY: %-build
%-build: %.docker
	$(call sudocompose,build --pull $(x))

.PHONY: %-logs
%-logs: %.docker
	$(call sudocompose,logs -t $(x)) 2>/dev/null | less -R +G

.PHONY: %-logf
%-logf: %.docker
	$(call sudocompose,logs -tf --tail=10 $(x)) ||:

s?=bash
.PHONY: %-sh
%-sh: %.docker
	$(call sudocompose,exec $(x) $(s)) ||:

# enabling and disabling
.PHONY: %-enable %-disable
%-enable: %.docker.down
	mv "$<" "$(basename $<)"
%-disable: %.docker
	mv "$<" "$<.down"

# Combinations
.PHONY: %-update
%-update: %.docker %-build %-pull
	$(MAKE) $(basename $<)-up

# Arbitrary compose command
.PHONY: %-cmd
%-cmd: %.docker
	$(call sudocompose,$(x))

