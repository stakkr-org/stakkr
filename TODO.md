General
=======
* Add unit tests for `stakkr services`, `stakkr services-add xyz` and `stakkr services-update`
* Use click-completion for bash and zsh completion
* make sure at least one service is `enabled: true`
* Convert old config to new config (doc or command)
* [VERBOSE] of stakkr-compose is not green :)
* Add option `-r` to remove containers on stop (`stakkr stop -r -> stakkr-compose down`)
* Test mailhog deeply
* Add pgadmin + phpredadmin in databases
* Need to fix commands list when doing "stakkr -c tests/static/config_aliases.yml"

* ~~Redo stakkr-init~~
* ~~Services outside, each will be a repo~~
* ~~Move conf/compose.ini to stakkr.yml~~
* ~~Use python-anyconfig for Config validation and not configobj~~
* ~~Rewrite a part of doc to install venv for development~~ 
* ~~Find a solution to generate a stakkr.yml template automatically~~ : recipe
* ~~Prepare recipes as wordpress, drupal, etc...~~
* ~~Re-implement plugins~~ Will try via command aliases
* ~~Check git is installed with packages-add~~
* ~~Improve error message when config invalid (no need to display standard config_default.yml)~~
