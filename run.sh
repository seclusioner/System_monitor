#!/bin/bash

cd "$(dirname "$0")"

source venv/bin/activate

mkdir -p logs

python3 app.py > logs/log.txt 2>&1 &
echo $! > logs/app.pid

