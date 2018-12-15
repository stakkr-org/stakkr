General
=======
* Add unit tests for `stakkr services`, `stakkr services-add xyz` and `stakkr services-update`
* ~Use python-anyconfig for Config validation and not configobj~
* Use click-completion
* ~Move conf/compose.ini to stakkr.yml~
* Rename conf/ to etc/ and get more standard paths
* Rename logs/ to var/log/ or implement a log centralization service :)
* Move `stakkr mysql` to plugins/
* Convert old config to new config (document or command)
* Reimplement plugins
* ~Services outside, each will be a repo~
* ~Redo stakkr-init~
* Rewrite a part of doc to install venv for development and install as user (`python3 -m pip install stakkr --user`)

* Ne pas lire plusieurs fois la config (stakkr / stakkr-compose)
* relire tout le code pour supprimer les doublons :)
* commande stakkr init créé un dossier stakkr/ (avec les conf des services) et un fichier stakkr.yml
* tester mailhog
* ajouter pg admin + phpredadmin
* gérer bash completion et zsh completion niveau systeme
* ecrire la doc pour faire les tests unitaires

