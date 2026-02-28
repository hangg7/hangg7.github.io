#!/bin/bash
#
# File   : set_access.sh
# Author : Hang Gao
# Email  : hangg.sv7@gmail.com
# Date   : 06/14/2020
#
# Distributed under terms of the MIT license.

set -e -x

# Public resources
chmod -R 755 assets
chmod 744 index.html

# Private but accessable at the end node
chmod -R 755 deformable-kernels dycheck eva
chmod 701 deformable-kernels dycheck eva

chmod -R 755 private
chmod 701 private

chmod og-x eva/rose.js eva/styles.css
