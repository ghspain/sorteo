.PHONY: build run clean help

IMAGE_NAME = ghspain-sorteo
CONTAINER_NAME = ghspain-sorteo-app

build:
	docker build -t $(IMAGE_NAME) .

run: build stop
	docker run -d --name $(CONTAINER_NAME) -p 8501:8501 $(IMAGE_NAME)

clean:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true
	docker rmi $(IMAGE_NAME) || true

stop:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

help:
	@echo "Available commands:"
	@echo "make build    - Build Docker image"
	@echo "make run     - Run application in Docker container"
	@echo "make clean   - Stop and remove container, remove image"