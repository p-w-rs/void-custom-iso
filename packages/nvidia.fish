#!/usr/bin/env fish

set NV       dkms libglvnd libglvnd-devel nvtop
set PACKAGES (string collect $PACKAGES $NV)
