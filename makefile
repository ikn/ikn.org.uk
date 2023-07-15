.PHONY: all push install clean

all:
	./build
	mkdir -p docker/site/
	cp -r *ikn.org.uk/ docker/site/
	cp -r ../fileshare/ docker/site/stuff.ikn.org.uk/
	docker build docker --tag ikn5812/ikn:latest

push:
	docker push ikn5812/ikn:latest

deploy:
	scp docker/deploy.sh docker/docker-compose.yaml ikn:docker/
	ssh ikn docker/deploy.sh

deploy-local:
	./docker/deploy.sh

clean:
	$(RM) -r ikn.org.uk/ docker/site/
	find lib/ -type d -name __pycache__ | xargs $(RM) -r
	docker image rm -f ikn5812/ikn:latest
	docker image prune -f
