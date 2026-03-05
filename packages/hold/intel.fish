#!/usr/bin/env fish

set INTEL    intel-gmmlib intel-media-driver intel-ucode intel-video-accel mesa-intel-dri mesa-vulkan-intel
set PACKAGES (string collect $PACKAGES $INTEL)
