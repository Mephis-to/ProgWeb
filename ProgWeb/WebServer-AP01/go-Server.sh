#!/bin/bash

cd "$(dirname "$0")" || exit 1

source environment.sh

export FLASK_APP=Server.py

FLASK_BIN=${Directory_PythonEnv}/bin/flask

${FLASK_BIN} run --port ${Port} --host=0.0.0.0
