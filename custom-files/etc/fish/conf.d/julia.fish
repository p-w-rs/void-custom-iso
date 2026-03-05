#!/usr/bin/env fish

# Julia Configuration
# Performance and development settings
set -gx JULIA_NUM_THREADS auto                    # Use all available cores
set -gx JULIA_EDITOR "nvim"                       # Set your preferred editor
set -gx JULIA_PKG_PRESERVE_TIERED_INSTALLED true  # Prevent accidental downgrades
set -gx JULIA_PKG_USE_CLI_GIT true               # Use system git for packages
set -gx JULIA_REVISE_POLL 0.5                    # Faster code reload with Revise.jl
set -gx JULIA_ERROR_COLOR "\033[91m"             # Red error messages
set -gx JULIA_WARN_COLOR "\033[93m"              # Yellow warnings
set -gx JULIA_INFO_COLOR "\033[36m"              # Cyan info messages

# Julia project-local Python configuration
set -gx JULIA_PYTHONCALL_EXE "@PyCall"           # Use project-local Python
set -gx JULIA_CONDAPKG_BACKEND "Null"            # Prevent global conda usage
set -gx PYTHON ""                                # Force PyCall to use Julia's Python

# Julia helper functions
function jlp --description "Launch Julia with project in current directory"
    env -u LD_LIBRARY_PATH julia --project=. $argv
end

function julia --description "Launch Julia clearing library paths"
    command env -u LD_LIBRARY_PATH julia $argv
end
