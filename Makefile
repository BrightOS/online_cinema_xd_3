.PHONY: up down restart logs ps force-restart

up:
	[ -f videostream/.env ] || cp videostream/.env.example videostream/.env
	[ -f movies/.env ] || cp movies/.env.example movies/.env
	docker-compose up -d --build

down:
	docker-compose down

restart: down up

force-restart: down
	docker-compose up -d --build --force-recreate

logs:
	docker-compose logs -f

ps:
	docker-compose ps

up-observability:
	docker-compose up -d prometheus grafana jaeger

up-core:
	docker-compose up -d postgres elasticsearch minio
