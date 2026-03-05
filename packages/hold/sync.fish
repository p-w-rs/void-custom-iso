#!/usr/bin/env fish

set PKG      rsync unison samba qrcp mup
set PACKAGES (string collect $PACKAGES $PKG)
