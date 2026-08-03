.PHONY: dev dev-up prod prod-up down logs build

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-up:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

prod:
	docker compose up -d --build

prod-up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

build:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml build