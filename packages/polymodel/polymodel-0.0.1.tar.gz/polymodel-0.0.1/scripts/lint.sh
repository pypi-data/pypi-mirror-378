#!/usr/bin/env bash

set -e
set -x

mypy polymodel
ruff check polymodel tests docs/src scripts
ruff format polymodel tests docs/src scripts --check
