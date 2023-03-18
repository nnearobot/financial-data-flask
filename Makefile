build:
	docker-compose up -d --build --remove-orphans

start:
	docker-compose start

stop:
	docker-compose stop
	$(info application has been stopped.)
