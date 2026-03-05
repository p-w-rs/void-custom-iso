#!/usr/bin/env fish

set NV       nvidia dkms libglvnd libglvnd-devel nvtop
set CMP      zstd
set PACKAGES (string collect $PACKAGES $NV $CMP)
