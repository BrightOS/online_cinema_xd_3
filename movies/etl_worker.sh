#!/bin/sh

pip install --no-cache-dir -r requirements.txt && \
python -m elastic.sync_worker