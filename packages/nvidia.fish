#!/usr/bin/env fish

set NV       dkms libglvnd libglvnd-devel nvtop
set CMP      zstd
set PACKAGES (string collect $PACKAGES $NV $CMP)
