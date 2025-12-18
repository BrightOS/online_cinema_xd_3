.PHONY: up down restart logs ps

up:
	docker compose up -d

down:
	docker compose down

restart: down up

logs:
	docker compose logs -f

ps:
	docker compose ps

up-observability:
	docker compose up -d prometheus grafana jaeger

up-core:
	docker compose up -d postgres elasticsearch minio
