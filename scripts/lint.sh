#!/usr/bin/env bash

set -e
set -x

flake8 src
black src --check --diff
isort src --check --diff
