#!/usr/bin/env fish

set DOCKER   docker docker-cli
set EXTRA    nvidia-docker
set PACKAGES (string collect $PACKAGES $DOCKER $EXTRA)
