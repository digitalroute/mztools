#!/usr/bin/env bash

# This script is for manual testing of vcexport.
# Please set up AWS credentials before running

if [[ -z "$MZUSER" ]]||[[ -z "$MZPASSWD" ]]; then
  echo "please set MZUSER and MZPASSWD env vars"
  exit 1
fi

set -ex

EXPORTDIR=$(mktemp -d)
mztools vcexport -u $MZUSER/$MZPASSWD -e test -d $EXPORTDIR
ls -l $EXPORTDIR
rm -r $EXPORTDIR
EXPORTDIR=$(mktemp -d)
mztools vcexport -u $MZUSER/$MZPASSWD -e test -d $EXPORTDIR -es
ls -l $EXPORTDIR
rm -r $EXPORTDIR
EXPORTDIR=$(mktemp -d)
mztools vcexport -u $MZUSER/$MZPASSWD -e test -d $EXPORTDIR -f Examples Default
ls -l $EXPORTDIR
rm -r $EXPORTDIR
EXPORTDIR=$(mktemp -d)
mztools vcexport -u $MZUSER/$MZPASSWD -e test -d $EXPORTDIR -im
ls -l $EXPORTDIR
rm -r $EXPORTDIR
EXPORTDIR=$(mktemp -d)
mztools vcexport -u $MZUSER/$MZPASSWD -e test -d $EXPORTDIR -f Examples
ls -l $EXPORTDIR
mztools vcexport -u $MZUSER/$MZPASSWD -e test -d $EXPORTDIR -f Default -o
ls -l $EXPORTDIR
rm -r $EXPORTDIR

echo ALL DONE
