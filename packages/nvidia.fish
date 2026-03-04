#!/usr/bin/env fish

set NV       dkms libglvnd libglvnd-devel
set PACKAGES (string collect $PACKAGES $NV)
