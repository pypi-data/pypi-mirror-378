#!/usr/bin/env bash

set -e
set -x

ruff check polymodel tests docs/src scripts --fix
ruff format polymodel tests docs/src scripts
