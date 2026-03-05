#!/usr/bin/env fish

set MESA     glu mesa mesa-dri mesa-intel-dri mesa-opencl mesa-vdpau mesa-vaapi mesa-vulkan-intel
set PACKAGES (string collect $PACKAGES $MESA)
