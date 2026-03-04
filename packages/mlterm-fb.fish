#!/usr/bin/env fish

set GCC      gcc gdb glibc
set LIBS     libtool freetype freetype-devel fontconfig fontconfig-devel cairo cairo-devel libpng libpng-devel kbd
set BUILD    git make autoconf automake pkg-config
set PACKAGES (string collect $PACKAGES $GCC $LIBS $BUILD)
