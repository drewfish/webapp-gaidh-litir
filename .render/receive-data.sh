#!/bin/bash
set -ex
cd /opt/gaidh-litir
if [[ -f payload.tgz ]]; then
  tar xfz payload.tgz
  rm payload.tgz
fi

