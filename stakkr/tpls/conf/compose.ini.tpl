[main]
# Comma separated, valid values: adminer / apache / elasticsearch / elasticsearch-old / mailcatcher
#                                maildev / mongo / mysql / php / phpmyadmin / phyton / redis / xhgui
# by default: nothing
# services=apache,php,mysql

# Change Machines prefix (A SINGLE WORD to avoid strange behaviors)
# project_name=stakkr

# Change your group id and user id only if needed (the defaults are the one from the current user)
# uid=1005
# gid=1005

# define the environement (if not dev, a few php modules will be deactivated)
# environment = dev

# Set your network
# subnet = 192.168.90.0/24


# Which port should we expose ?
# adminer.expose = 8081


# Set your apache version (2.2 / 2.4 / 2.4-slim)
# apache.version=2.2
# apache.ram=512M
# Which port should we expose for apache ?
# apache.expose = 8080


# Check https://www.docker.elastic.co
# elasticsearch.version=6.2.3
# elasticsearch.ram=2048M


# Which port should we expose for mailcatcher ?
# mailcatcher.expose = 8082


# Which port should we expose for maildev ?
# maildev.expose = 8083


# Check https://hub.docker.com/_/mongo/ (latest by default)
# mongo.version=latest


# Check https://hub.docker.com/_/mysql/ (5.7 by default)
# mysql.ram=1024M
# mysql.version=5.7
# Password set on first start. Once the data exist won't be changed
# mysql.root_password=changeme


# Set your PHP version from 5.3 to 7.2 (5.6 by default)
# php.version=7.0
# php.ram=512M


# Set the max upload size for phpMyAdmin
# pma.upload_max_filesize=128M
# Which port should we expose for PMA ?
# pma.expose = 8084


# Which port should we expose for portainer ?
# portainer.expose = 8085


# Set your postgresql version + password (default superuser is "postgres")
# postgres.ram = 1024M
# postgres.password = postgres
# postgres.version = 9-alpine


# Set your Python version from https://hub.docker.com/_/python/
# python.ram=512M
# python.version=latest


# Set your Redis Version from https://hub.docker.com/_/redis/
# redis.ram=512M
# redis.version=latest


# xhgui max RAM
# xhgui.ram=512M
# Which port should we expose for xhgui ?
# xhgui.expose = 8085


# [network-block]
# php=25,465,587
