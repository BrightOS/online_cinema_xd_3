# HOWTO: запустить сервис

### 1. Зависимости

```
pip install -r requirements.txt
```

### 2. Redis / MinIO

ну тут как-бы сами

### 3. енвы

Нужен .env файл. Для теста можно юзать эти енвы:

```
LOG_LEVEL=10 

S3_BUCKET=bucket
S3_ENDPOINT_URL=http://localhost:9000
aws_access_key_id=minioadmin
aws_secret_access_key=minioadmin
REDIS_URL=redis://localhost:6379/0
```

Если заколебут логи, LOG_LEVEL=30

### 4. Воркер

```
python worker.py
```

### 5. АПИ

```
python main.py
```

### 6. эээ Profit?!

Апи по адресу http://127.0.0.1:8002/docs#/

Можно юзать dummy.html для просмотра видео (только для тестов, там GUI шляпа)
