#!/usr/bin/env fish

set LLVM     llvm clang lldb
set LIBS     libstdc++ libstdc++-devel llvm21-devel
set BUILD    git make
set PACKAGES (string collect $PACKAGES $LLVM $LIBS $BUILD)
