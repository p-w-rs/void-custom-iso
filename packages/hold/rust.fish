#!/usr/bin/env fish

set RUST     rust cargo
set PACKAGES (string collect $PACKAGES $RUST)
