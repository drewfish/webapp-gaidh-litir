#!/bin/bash
set -ex
cd /opt/gaidh-litir
if [[ -f payload.tgz ]]; then
  tar tfvz payload.tgz
  tar xfvz payload.tgz
  rm payload.tgz
fi

