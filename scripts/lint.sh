#!/usr/bin/env bash

set -x

mypy pyhocon_dantic --explicit-package-bases --ignore-missing-imports
black pyhocon_dantic --check
isort --check-only pyhocon_dantic
flake8 pyhocon_dantic --max-line-length=127