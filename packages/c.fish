#!/usr/bin/env fish

set GCC      gcc gdb glibc
set LLVM     llvm clang clang-analyzer clang-tools-extra lldb
set LIBS     libstdc++ libstdc++-devel libdrm libdrm-devel libinput libinput-devel libxkbcommon libxkbcommon-devel libtool
set LIBS2    libevdev libevdev-devel libuvdev libuvdev-devel glib glib-devel libconfig libconfig-devel libconfig++ libconfig++-devel
set BUILD    make cmake automake pkg-config autoconf binutils patch ninja meson diffutils binutils
set PACKAGES (string collect $PACKAGES $GCC $LLVM $LIBS $LIBS2 $BUILD)
