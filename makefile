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
	ssh ikn rm -rf docker
	rsync -av --exclude site/ docker/ ikn:docker/
	ssh ikn ENV_FILE=docker/tls.env PULL_POLICY=always docker/deploy.sh

deploy-local:
	ENV_FILE=docker/no-tls.env PULL_POLICY=never ./docker/deploy.sh

clean:
	$(RM) -r ikn.org.uk/ docker/site/
	find lib/ -type d -name __pycache__ | xargs $(RM) -r
	docker image rm -f ikn5812/ikn:latest
