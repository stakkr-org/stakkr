[main]
# Comma separated, valid values: adminer / apache / elasticsearch / elasticsearch-old / mailcatcher
#                                maildev / mongo / mysql / php / phpmyadmin / phyton / redis / xhgui
# by default: nothing
# services=apache,php,mysql

# Change Machines prefix
# project_name=stakkr

# Change your group id and user id only if needed (the defaults are the one from the current user)
# uid=1005
# gid=1005

# define the environement (if not dev, a few php modules will be deactivated)
# environment = dev

# Set your network
# subnet = 192.168.90.0/24

# Set your PHP version from 5.3 to 7.0 (5.6 by default)
# php.version=7.0
# php.ram=512M

# Set your Python version from https://hub.docker.com/_/python/
# python.ram=512M
# python.version=latest

# Set your Redis Version from https://hub.docker.com/_/redis/
# redis.ram=512M
# redis.version=latest

# Set the max upload size for PMA
# pma.upload_max_filesize=128M

# Set your apache version to 2.2
# apache.version=2.2
# apache.ram=512M

# Check https://hub.docker.com/_/mongo/ (latest by default)
# mongo.version=latest

# Check https://hub.docker.com/_/mysql/ (5.7 by default)
# mysql.version=5.7
# mysql.ram=1024M

# Password set on first start. Once the data exist won't be changed
# mysql.root_password=changeme


# Check https://hub.docker.com/_/elasticsearch/
# elasticsearch.version=2
# elasticsearch.ram=512M


# Conf for xhgui
# xhgui.ram=512M



# [network-block]
# php=25,465,587
