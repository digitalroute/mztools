#!/bin/bash

# This is a wrapper script for the mztools docker container
if [ "$1" == "update" ]; then
  docker pull mztools:latest
else
  docker run -i -e AWS_DEFAULT_REGION \
             -e AWS_SECURITY_TOKEN \
             -e AWS_ACCESS_KEY_ID \
             -e AWS_SECRET_ACCESS_KEY \
             -e AWS_SESSION_TOKEN \
             -v "$(pwd)":/data \
             --rm mztools:latest \
             "$@"
fi
