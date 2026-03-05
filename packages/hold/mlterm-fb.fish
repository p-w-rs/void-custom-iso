#!/usr/bin/env fish

# Build dependencies for mlterm-fb (framebuffer terminal with sixel support).
# mlterm itself is compiled from source (custom-files/opt/mlterm submodule)
# so we only need the libraries and tools it links against.

set GCC      gcc gdb glibc
set BUILD    make autoconf automake pkg-config libtool

# Freetype + fontconfig — anti-aliased font rendering on the framebuffer
set FONTS    freetype freetype-devel fontconfig fontconfig-devel

# Image / sixel support — libsixel provides img2sixel for producing sixel output
# chafa renders images/video to sixel/block art in the terminal
set SIXEL    libsixel libsixel-devel chafa

# PCF/bitmap font fallback (unifont covers the full BMP)
set PCFFONT  font-unifont-bdf

set PACKAGES (string collect $PACKAGES $GCC $BUILD $FONTS $SIXEL $PCFFONT)
