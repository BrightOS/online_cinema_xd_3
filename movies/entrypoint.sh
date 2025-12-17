#!/bin/sh

# Инициализация базы, если таблиц нет
python -m scripts.init_db

# Запуск приложения
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
