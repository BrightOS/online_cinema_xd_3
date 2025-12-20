#!/bin/bash

python3 worker.py &
python3 main.py &

wait -n
exit $?
