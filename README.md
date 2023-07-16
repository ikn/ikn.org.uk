Source code for <http://ikn.org.uk>.

# License

Distributed under the terms of the
[BSD 3-Clause license](https://opensource.org/licenses/BSD-3-Clause).

# Build

Adjust paths in config files in the `data` directory, then run `make`.  This
builds a static site in the `dist` directory, and a Docker image called `ikn`.

`make push` pushes the Docker image to Docker Hub.

`make deploy` deploys the pushed Docker image to the web server.

`make deploy-local` deploys the built Docker image on this machine.

# Dependencies

- [Python 3](http://www.python.org) (>= 3.7)
- [Jinja 2](https://jinja.palletsprojects.com/en/2.11.x/)
- [Pillow](https://python-pillow.org/)
- [gw2buildutil](http://ikn.org.uk/lib/gw2buildutil) (0.2)
- [Docker](https://www.docker.com/)
- [rsync](https://rsync.samba.org/)

# Web server setup

* install Docker and Docker Compose
* install rsync
* enable and start cronie
* cron job: `0 4 * * * ~/docker/reload-apache.sh`
* create remote user and add to the `docker` group
* configure SSH locally for passwordless access with hostname `ikn`
