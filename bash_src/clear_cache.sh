#!/bin/bash

# removing only all executables from codes.
file -F: codes/* | grep "executable" | cut -d: -f1 | xargs rm

# clearing response files and logs
#truncate -s 0 bardcoder.log
truncate -s 0 response/content.md
truncate -s 0 response/response.json
