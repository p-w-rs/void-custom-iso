#!/usr/bin/env fish

# Python Configuration
# Disable cache and bytecode generation for cleaner development
set -gx PYTHONDONTWRITEBYTECODE 1       # Prevents .pyc files
set -gx PYTHONUNBUFFERED        1       # Ensures output is displayed immediately
set -gx PYTHONNODEBUGRANGES     1       # Reduces memory usage in 3.11+
set -gx PYTHONPYCACHEPREFIX     /tmp    # Redirects __pycache__ to /tmp (auto-cleaned)

# UV Configuration
if type -q uv
    set -gx UV_LINK_MODE    copy
    set -gx UV_NO_CACHE     0  # Set to 1 if you want to disable UV caching
end
