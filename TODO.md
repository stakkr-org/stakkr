General
=======
* Add unit tests for `stakkr services`, `stakkr services-add xyz` and `stakkr services-update`
* Use click-completion for bash and zsh completion
* Rename logs/ to var/log/ or implement a log centralization service :) (https://hub.docker.com/r/graylog/graylog/ or https://hub.docker.com/r/prom/prometheus/ ?)
* Move `stakkr mysql` to plugins/
* improve error message when config invalid (no need to display standard config_default.yml)
* check git is installed with packages-add
* make sure at least one service is `enabled: true`
* Convert old config to new config (doc or command)
* Re-implement plugins
* [VERBOSE] of stakkr-compose is not green :)
* Add option `-r` to remove containers on stop (`stakkr stop -r -> stakkr-compose down`)
* Rewrite a part of doc to install venv for development 
* find a solution to generate a stakkr.yml template automatically
* Make sure config is read once only
* Test mailhog deeply
* Prepare recipes as wordpress, drupal, etc...
* Add pgadmin + phpredadmin in databases
* ~~Redo stakkr-init~~
* ~~Services outside, each will be a repo~~
* ~~Move conf/compose.ini to stakkr.yml~~
* ~~Use python-anyconfig for Config validation and not configobj~~


# Development :
```bash
$ docker run --privileged --name stakkr-test -v $(pwd):/stakkr-core --rm -d docker:stable-dind
$ docker exec -ti stakkr-test /bin/sh

$ apk add python3 git vim
$ python3 -m pip install -e /stakkr-core
# Or from the latest dev version :
# $ python3 -m pip install https://github.com/stakkr-org/stakkr/archive/v4.0-dev.zip
# Or with a specific user : 
# $ python3 -m pip install -e /stakkr-core --user

$ mkdir /stakkr-dev
$ cd /stakkr-dev
$ stakkr-init
```
