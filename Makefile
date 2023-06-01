up:
	docker-compose up -d --build --force-recreate

down:
	docker-compose down

log:
	docker-compose logs -f