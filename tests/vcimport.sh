#!/usr/bin/env bash

# This script is for manual testing of vcimport.
# Please set up AWS credentials before running

if [[ -z "$MZUSER" ]]||[[ -z "$MZPASSWD" ]]; then
  echo "please set MZUSER and MZPASSWD env vars"
  exit 1
fi

set -xe

EXPORTDIR=$(mktemp -d)
mztools vcexport -u $MZUSER/$MZPASSWD -e dev -d $EXPORTDIR -f Examples

# The output from these commands should be the same
mztools vcimport -u $MZUSER/$MZPASSWD -e dev -d $EXPORTDIR -f Examples
mztools vcimport -u $MZUSER/$MZPASSWD -e dev -d $EXPORTDIR -y --message "Test in vcimport.sh"
mztools vcimport -u $MZUSER/$MZPASSWD -e dev -d $EXPORTDIR

rm -r $EXPORTDIR
