General
=======
* Add in doc that pip install should be done with --user

* Use python-anyconfig for Config validation and not configobj
* Use click-completion
* Move conf/compose.ini to .stakkr.yml
* Rename conf/ to etc/ and get more standard paths
* Rename logs/ to var/log/
* Move services to plugins/
* Convert old config to new config



* Ne pas lire plusieurs fois la config (stakkr / stakkr-compose)
* relire tout le code pour supprimer les doublons :)
* services outside, each will be a repo
* commande stakkr init créé un dossier stakkr/ (avec les conf des services) et un fichier stakkr.yml
* tester mailhog
* ajouter pg admin + phpredadmin
* gérer bash completion et zsh completion niveau systeme
* refaire le stakkr init
* ecrire la doc pour faire les tests unitaires


OK cli_test.py
OK command_test.py
OK configreader_test.py
OK docker_actions_test.py
OK files_utils_test.py
docker_clean_test.py
A FAIRE plugins_test.py
OK stakkr_compose_test.py
