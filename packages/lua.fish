#!/usr/bin/env fish

set LUA      lua luarocks
set PACKAGES (string collect $PACKAGES $LUA)
