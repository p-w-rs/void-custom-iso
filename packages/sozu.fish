#!/usr/bin/env fish

set RUST     rust cargo
set LIBS     pkg-config protobuf libprotobuf openssl openssl-devel
set BUILD    git
set PACKAGES (string collect $PACKAGES $RUST $LIBS $BUILD)
