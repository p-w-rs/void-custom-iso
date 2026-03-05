#!/usr/bin/env fish

set CERT     ca-certificates acmetool certbot
set PACKAGES (string collect $PACKAGES $CERT)
