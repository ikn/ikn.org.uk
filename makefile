.PHONY: all push install clean

all:
	./build
	mkdir -p docker/site/
	cp -r *ikn.org.uk/ docker/site/
	mv docker/site/ikn.org.uk/download/ docker/download
	docker build docker --tag iknorguk/ikn:latest

push:
	docker push iknorguk/ikn:latest

deploy:
	scp ../remote.env ikn:remote.env
	rsync -av --delete --exclude site/ --exclude download/ docker/ ikn:docker/
	rsync -av --delete docker/download/ ikn:download/
	rsync -av --delete ../fileshare/ ikn:fileshare/
	ssh ikn ENV_FILE=remote.env PULL_POLICY=always docker/deploy.sh

deploy-local:
	ENV_FILE=../local.env PULL_POLICY=never ./docker/deploy.sh

clean:
	$(RM) -r ikn.org.uk/ docker/site/ docker/download/
	find lib/ -type d -name __pycache__ | xargs $(RM) -r
	docker image rm -f iknorguk/ikn:latest
