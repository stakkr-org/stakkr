General
=======
* Add unit tests for `stakkr services`, `stakkr services-add xyz` and `stakkr services-update`
* ~~Use python-anyconfig for Config validation and not configobj~~
* Use click-completion
* ~~Move conf/compose.ini to stakkr.yml~~
* Rename conf/ to etc/ and get more standard paths
* Rename logs/ to var/log/ or implement a log centralization service :) (https://hub.docker.com/r/graylog/graylog/ or https://hub.docker.com/r/prom/prometheus/ ?)
* Move `stakkr mysql` to plugins/
* improve error message when config invalid (no need to display standard config_default.yml)
* check git is installed with packages-add
* make sure at least one service is `enabled: true`
* Convert old config to new config (document or command)
* Reimplement plugins
* [VERBOSE] of stakkr-compose is not green :)
* Add option `-r` to remove containers on stop (`stakkr-compose down`)
* ~~Services outside, each will be a repo~~
* ~~Redo stakkr-init~~
* Rewrite a part of doc to install venv for development and install as user (`python3 -m pip install stakkr --user`)
* find a solution to generate a stakkr.yml template automatically
* Ne pas lire plusieurs fois la config (stakkr / stakkr-compose)
* relire tout le code pour supprimer les doublons :)
* commande stakkr init créé un dossier stakkr/ (avec les conf des services) et un fichier stakkr.yml
* tester mailhog
* ajouter pg admin + phpredadmin
* gérer bash completion et zsh completion niveau systeme
* ecrire la doc pour faire les tests unitaires


# Development :
```bash
$ docker run --privileged --name stakkr-test -v $(pwd):/stakkr-core --rm -d docker:stable-dind
$ docker exec -ti stakkr-test /bin/sh

$ apk add python3 git vim
$ python3 -m pip install -e /stakkr-core
# Or from the latest dev version :
# $ python3 -m pip install https://github.com/stakkr-org/stakkr/archive/v4.0-dev.zip

$ mkdir /stakkr-dev
$ cd /stakkr-dev
$ stakkr-init
```