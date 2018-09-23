[main]
# Comma separated, valid values are available via the command `stakkr services`
# by default: nothing
# services=apache,php,mysql

# Change Machines prefix (A SINGLE WORD to avoid strange behaviors)
# project_name=stakkr

# Change your group id and user id only if needed (the defaults are the one from the current user)
# uid=1005
# gid=1005

# define the environement (if not dev, a few php modules will be deactivated)
# environment = dev

# Set your network (optional, if empty, it'll be automatically set)
# subnet = 192.168.90.0/24


# Adminer, a micro phpmyadmin that supports more dbs
# see : https://hub.docker.com/r/edyan/adminer/
# adminer.ram = 256M
# adminer.version = latest


# Set your apache version (2.2 / 2.4 / 2.4-slim)
# see : https://hub.docker.com/r/edyan/apache/
# apache.ram = 512M
# apache.version = 2.2


# Check https://www.docker.elastic.co
# elasticsearch.ram = 2048M
# elasticsearch.version = 6.2.3

# Check https://www.docker.elastic.co for kibana
# kibana.ram=2048M
# kibana.version=6.3.0

# Check https://www.docker.elastic.co for logstash
# logstash.ram=2048M
# logstash.version=6.3.0


# Mailcatcher, a fake smtp
# see : https://hub.docker.com/r/tophfr/mailcatcher/
# mailcatcher.ram = 256M
# mailcatcher.version = latest


# Maildev, another fake smtp
# see : https://hub.docker.com/r/djfarrelly/maildev/
# mailcatcher.ram = 256M
# mailcatcher.version = latest


# Check https://hub.docker.com/_/mongo/ (latest by default)
# mongo.ram = 1024M
# mongo.version = latest


# Check https://hub.docker.com/_/mysql/ (5.7 by default)
# mysql.ram = 1024M
# mysql.version = 5.7
# Password set on first start. Once the data exist won't be changed
# mysql.root_password = changeme


# How much RAM for Nginx ?
# see : https://hub.docker.com/r/edyan/nginx/
# nginx.ram = 512M
# nginx.version = latest


# Set your PHP version from 5.3 to 7.2 (5.6 by default)
# see : https://hub.docker.com/r/edyan/php/
# php.ram = 512M
# php.version = 7.0


# PhpMyadmin to administrate mysql DBs
# Set the max upload size for phpMyAdmin
# pma.ram = 512M
# pma.version = latest
# pma.upload_max_filesize = 128M


# Portainer, a docker GUI
# see : https://hub.docker.com/r/portainer/portainer/
# portainer.ram = 512M
# portainer.version = latest


# Set your postgresql version + password (default superuser is "postgres")
# see : https://hub.docker.com/_/postgres/
# postgres.ram = 512M
# postgres.password = postgres
# postgres.version = 9-alpine


# Set your sqlserver version + password (default superuser is "sa")
# Be careful that does not work for MacOS (no data persistence)
# see : https://hub.docker.com/r/microsoft/mssql-server-linux/
# sqlserver.ram = 1024M
# sqlserver.password = Sa2017Sqlserver
# sqlserver.version = 2017-latest


# Set your Redis Version from https://hub.docker.com/_/redis/
# redis.ram=512M
# redis.version=latest


# Profiler for PHP
# see : https://hub.docker.com/r/edyan/xhgui/
# xhgui max RAM
# xhgui.ram=512M
# Versions available : php5.6 and php7.2 (latest). Use the right version for your main PHP container
# xhgui.version=latest



[proxy]
# Enable Proxy with traefik to have nice hostnames
# enabled = 1
# domain = localhost # you can also use stakkr.org but you need internet for the DNS resolution
# port = 80



[network-block]
# php=25,465,587
