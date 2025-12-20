#!/bin/sh

python -m scripts.init_db && \
python -m init_db && \
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
