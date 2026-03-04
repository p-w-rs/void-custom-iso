#!/usr/bin/env fish

set FF       ffmpeg ffplay
set AV       libavcodec libavdevice libavfilter libavformat libavresample libavutil
set PX       libvpx libvpx-devel libvpx-tools
set AO       libaom libaom-devel libaom-tools
set RV       rav1e rav1e-devel
set OP       opus opus-devel opus-tools
set OTHER    alsa-plugins-ffmpeg nv-codec-headers libswscale  libpostproc
set PACKAGES (string collect $PACKAGES $FF $AV $PX $AO $RV $OP $OTHER)
