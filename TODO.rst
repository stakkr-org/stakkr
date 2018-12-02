General
=======
* Use python-anyconfig for Config validation and not configobj
* Use click-completion
* Move conf/compose.ini to .stakkr.yml
* Rename conf/ to etc/ and get more standard paths
* Rename logs/ to var/log/
* Move services to plugins/
* Convert old config to new config



* Ne pas lire plusieurs fois la config (stakkr / stakkr-compose)
* relire tout le code pour supprimer les doublons :)
* name et url should come from config
* services outside, each will be a repo
* commande stakkr init créé un dossier stakkr/ et un fichier stakkr.yml
* faire un stakkr update pour mettre à jour les plugins / services
* retirer les post scripts ou le faire autrement (mysql ...) (fait)
* tester mailhog
* faire la doc et des github dédiés pour les packages
* ajouter pg admin + phpredadmin
* gérer bash completion et zsh completion niveau systeme