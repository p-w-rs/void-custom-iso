#!/usr/bin/env fish

# CUDA Environment Variables
# Configure CUDA paths and libraries
if test -d /usr/local/cuda
    set -gx CUDA_HOME       /usr/local/cuda
    set -gx PATH            /usr/local/cuda/bin $PATH
    set -gx LD_LIBRARY_PATH /usr/local/cuda/lib64 $LD_LIBRARY_PATH
    set -gx CUDNN_PATH      $CUDA_HOME
end
