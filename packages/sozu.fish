#!/usr/bin/env fish

set RUST     rust cargo
set LIBS     protobuf libprotobuf openssl openssl-devel
set BUILD    git pkg-config
set PACKAGES (string collect $PACKAGES $RUST $LIBS $BUILD)
