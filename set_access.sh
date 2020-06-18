#!/bin/bash
#
# File   : set_access.sh
# Author : Hang Gao
# Email  : hangg.sv7@gmail.com
# Date   : 06/14/2020
#
# Distributed under terms of the MIT license.

set -e -x

# public resources
chmod -R 755 css fonts js assets
chmod 744 index.html

# private but accessable at the end node
chmod -R 755 projects
chmod 701 projects

chmod -R 755 misc
chmod 701 misc
chmod og-x misc/toeva/rose.js misc/toeva/style.css
