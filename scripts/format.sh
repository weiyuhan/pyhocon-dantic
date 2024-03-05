#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place pyhocon_dantic
black pyhocon_dantic
isort pyhocon_dantic