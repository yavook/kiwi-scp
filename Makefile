##########
# COMMANDS

DOCKER:=docker
DOCKER_COMPOSE:=docker-compose
docker_bash=$(1)

# Check if needs root privileges?
PRIVGROUP:=docker
ifneq ($(findstring $(PRIVGROUP),$(shell groups)),$(PRIVGROUP))
DOCKER:=sudo $(DOCKER)
docker_bash=sudo bash -c '$(1)'
endif

#########
# CONFIGS

CONF_WILDC:=$(wildcard $(PWD)/*.conf)
# apply source to *all* configs!
CONF_SOURCE:=$(patsubst %,. %;,$(CONF_WILDC))

# extraction of env variables from *.conf files
confvalue=$(shell $(CONF_SOURCE) echo -n $${$(1)})

# docker network name
CONF_DOCKERNET:=$(call confvalue,DOCKERNET)
ifeq ($(CONF_DOCKERNET),)
$(error DOCKERNET not set in $(CONF_WILDC))
endif

# docker network CIDR 
CONF_DOCKERCIDR:=$(call confvalue,DOCKERCIDR)
ifeq ($(CONF_DOCKERNET),)
$(error DOCKERCIDR not set in $(CONF_WILDC))
endif

# persistent data directory
CONF_TARGETROOT:=$(call confvalue,TARGETROOT)
ifeq ($(CONF_TARGETROOT),)
$(error TARGETROOT not set in $(CONF_WILDC))
endif

# suffix for project directories
PROJ_SUFFX:=$(call confvalue,SUFFIX_PROJECT)
ifeq ($(PROJ_SUFFX),)
$(error SUFFIX_PROJECT not set in $(CONF_WILDC))
endif

# suffix for disabled project directories
DOWN_SUFFX:=$(call confvalue,SUFFIX_DOWN)
ifeq ($(DOWN_SUFFX),)
$(error SUFFIX_DOWN not set in $(CONF_WILDC))
endif

#########
# CONSTANTS

# file to store docker network cidr
FILE_DOCKERNET:=$(CONF_TARGETROOT)/up-$(CONF_DOCKERNET)

# remove any suffix $2 from $1
rmsuffix=$(patsubst %$2,%,$1)
# remove project suffix from $1
projname=$(call rmsuffix,$1,$(PROJ_SUFFX))

# project directory handling
PROJ_WILDC:=$(wildcard *$(PROJ_SUFFX))
PROJ_NAMES:=$(call projname,$(PROJ_WILDC))

#########
# FUNCTIONS

# run DOCKER_COMPOSE:
#  - in project directory
#  - with sourced *.conf files
#  - with COMPOSE_PROJECT_NAME, CONFDIR and TARGETDIR set
kiwicompose=$(call docker_bash,\
	cd "$<"; \
	$(CONF_SOURCE) \
	COMPOSE_PROJECT_NAME="$(call projname,$<)" \
	CONFDIR="$(CONF_TARGETROOT)/conf" \
	TARGETDIR="$(CONF_TARGETROOT)/$<" \
	$(DOCKER_COMPOSE) $(1))

#########
# TARGETS

# default target
.PHONY: all
all: purge-conf up

#########
# manage the docker network (container name local DNS)
$(FILE_DOCKERNET):
	-$(DOCKER) network create \
		--driver bridge \
		--internal \
		--subnet "$(CONF_DOCKERCIDR)" \
		"$(CONF_DOCKERNET)"
	@echo "Creating canary $(FILE_DOCKERNET) ..."
	@$(DOCKER) run --rm \
		-v "/:/mnt" -u root alpine:latest \
		ash -c '\
			mkdir -p "$(addprefix /mnt, $(CONF_TARGETROOT))"; \
			echo "$(CONF_DOCKERCIDR)" > "$(addprefix /mnt, $(FILE_DOCKERNET))"; \
		'

.PHONY: net-up
net-up: $(FILE_DOCKERNET)

.PHONY: net-down
net-down: down
	$(DOCKER) network rm "$(CONF_DOCKERNET)"
	@echo "Removing canary $(FILE_DOCKERNET) ..."
	@$(DOCKER) run --rm \
		-v "/:/mnt" -u root alpine:latest \
		ash -c '\
			rm -f "$(addprefix /mnt, $(FILE_DOCKERNET))"; \
		'

#########
# sync project config directory to variable folder

# Dockerfile for running rsync as root
define DOCKERFILE_RSYNC
FROM alpine:latest
RUN  apk --no-cache add rsync
endef

.PHONY: copy-conf
copy-conf:
ifneq ($(wildcard *${PROJ_SUFFX}/conf),)
	$(eval export DOCKERFILE_RSYNC)
	@echo "Building auxiliary image ldericher/kiwi-config:rsync ..."
	@echo -e "$${DOCKERFILE_RSYNC}" | \
		$(DOCKER) build -t ldericher/kiwi-config:rsync . -f- &> /dev/null

	$(eval sources:=$(wildcard *${PROJ_SUFFX}/conf))
	@echo "Syncing $(sources) to $(CONF_TARGETROOT) ..."

	$(eval sources:=$(realpath $(sources)))
	$(eval sources:=$(addprefix /mnt, $(sources)))
	$(eval sources:=$(patsubst %,'%',$(sources)))
	$(eval dest:='$(addprefix /mnt, $(CONF_TARGETROOT))')

	@$(DOCKER) run --rm \
		-v "/:/mnt" -u root ldericher/kiwi-config:rsync \
		ash -c '\
			rsync -r $(sources) $(dest); \
		'
endif

.PHONY: purge-conf
purge-conf:
	@echo "Emptying $(CONF_TARGETROOT)/conf ..."
	@$(DOCKER) run --rm \
		-v "/:/mnt" -u root alpine:latest \
		ash -c '\
			rm -rf "$(addprefix /mnt, $(CONF_TARGETROOT)/conf)"; \
		'

#########
# manage all projects
.PHONY: up down update
up: net-up copy-conf $(patsubst %,%-up,$(PROJ_NAMES))
down: $(patsubst %,%-down,$(PROJ_NAMES))
update: $(patsubst %,%-update,$(PROJ_NAMES))

#########
# manage single project
.PHONY: %-up
%-up: %$(PROJ_SUFFX) net-up
	$(call kiwicompose,up -d $(x))

.PHONY: %-down
ifeq ($(x),)
%-down: %$(PROJ_SUFFX)
	$(call kiwicompose,down)
else
%-down: %$(PROJ_SUFFX)
	$(call kiwicompose,stop $(x))
	$(call kiwicompose,rm -f $(x))
endif

.PHONY: %-pull
%-pull: %$(PROJ_SUFFX)
	$(call kiwicompose,pull --ignore-pull-failures $(x))

.PHONY: %-build
%-build: %$(PROJ_SUFFX)
	$(call kiwicompose,build --pull $(x))

.PHONY: %-logs
%-logs: %$(PROJ_SUFFX)
	$(call kiwicompose,logs -t $(x)) 2>/dev/null | less -R +G

.PHONY: %-logf
%-logf: %$(PROJ_SUFFX)
	$(call kiwicompose,logs -tf --tail=10 $(x)) ||:

ifneq ($(x),)
s?=bash
.PHONY: %-sh
%-sh: %$(PROJ_SUFFX)
	$(call kiwicompose,exec $(x) /bin/sh -c "[ -e /bin/$(s) ] && /bin/$(s) || /bin/sh")
endif

# enabling and disabling
.PHONY: %-enable %-disable
%-enable: %$(PROJ_SUFFX)$(DOWN_SUFFX)
	mv "$<" "$(call projname,$(call rmsuffix,$<,$(DOWN_SUFFX)))$(PROJ_SUFFX)"
%-disable: %$(PROJ_SUFFX)
	mv "$<" "$<$(DOWN_SUFFX)"

# Combinations
.PHONY: %-update
%-update: %$(PROJ_SUFFX) %-build %-pull copy-conf
	$(MAKE) $(call projname,$<)-down
	$(MAKE) $(call projname,$<)-up

# Arbitrary compose command
.PHONY: %-cmd
%-cmd: %$(PROJ_SUFFX)
	$(call kiwicompose,$(x))

#########
# project creation
.PHONY: %-new
%-new:
	$(eval proj_dir:=$(patsubst %-new,%$(PROJ_SUFFX)$(DOWN_SUFFX),$@))
	mkdir $(proj_dir)
	$(eval export COMPOSEFILE)
	echo -e "$${COMPOSEFILE}" > $(proj_dir)/docker-compose.yml

# default compose file
define COMPOSEFILE
version: "2"

networks:
  # reachable from outside
  default:
    driver: bridge
  # interconnects projects
  kiwihub:
    external:
      name: $$DOCKERNET

services:
  something:
    image: maintainer/repo:tag
    restart: unless-stopped
		networks:
		  - default
		  - kiwihub
    [...]
endef
