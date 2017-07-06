[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/inetprocess/marina/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/inetprocess/marina/?branch=master)
[![Build Status](https://scrutinizer-ci.com/g/inetprocess/marina/badges/build.png?b=master)](https://scrutinizer-ci.com/g/inetprocess/marina/build-status/master)

# Marina
A recompose tool that uses docker compose to easily create / maintain a stack of services, for example for web development. Via a configuration file you can setup the required services and let marina link and start everything for you.

- [Docker installation](#docker-installation)
- [Clone the repository](#clone-the-repository)
- [Configuration](#configuration)
	- [Config Parameters](#config-parameters)
- [Files location](#files-location)
	- [Add binaries](#add-binaries)
- [Before running any command](#before-running-any-command)
- [Usage](#usage)
	- [Get Help](#get-help)
	- [Start the servers](#start-the-servers)
	- [Stop the servers](#stop-the-servers)
	- [Restart the servers](#restart-the-servers)
	- [Status](#status)
	- [Enter a VM](#enter-a-vm)
	- [PHP usage](#php-usage)
	- [MySQL usage](#mysql-usage)
    	- [DNS](#dns)
- [Plugins](#plugins)
	- [Writing a plugin](#writing-a-plugin)
	- [Install a plugin](#installing-a-plugin)
   	- [Define services in your plugins](#define-services-in-your-plugins)
	- [List of existing plugins](#list-of-existing-plugins)


# Docker installation (example for Ubuntu)
Read https://docs.docker.com/engine/installation/ubuntulinux/ for Ubuntu.


# Clone the repository
You can clone the repository as many times as you want as you can have multiple instances at the same time. A good practice is too have one clone for one project or one clone for projects with the same versions of PHP / MySQL / Elasticsearch, etc ...
```bash
$ git clone https://github.com/inetprocess/marina
```

## Prerequisites
### Automatic Installation
Once cloned, you can run the `install.sh` script made for Ubuntu (tested on 16.04) that will install the dependencies:
```bash
$ cd marina
$ ./install.sh
```

### Manual Installation
Else:
* Install the OS packages for Python3: `pip`, `setuptools` and `virtualenv`

* Install `autoenv` (Read https://github.com/kennethreitz/autoenv). Example:
```bash
$ pip3 install autoenv
```

* Create the virtualenv and activate it:
```bash
$ virtualenv -p /usr/bin/python3 ${PWD##*/}_lamp
$ source ${PWD##*/}_lamp/bin/activate
$ pip3 install click clint # because it could be needed at that stage
$ pip3 install -e .
```


# Configuration
Copy the file `conf/compose.ini.tpl` to `conf/compose.ini` and set the right Configuration parameters.


## Config Parameters
Everything should be defined in the `[main]` section. **Don't use double quotes to protect your values.**. All values are defined in the compose.ini.tpl.

### Network
You can define your own network in compose.ini (`subnet` and `gateway`). If you change that, run `docker-clean` (**Be Careful: it removes orphans images, stopped container, etc ....**).


### Services
You can define the list of services you want to have. Each service consists of a yml file in the `services/` directory. Each container ("Virtual Machine") will have a hostname composed of the project name and the service name. To reach, for example, the elasticsearch server from a web application, and if your `project_name = lamp` use `lamp_elasticsearch` or to connect to mysql use `lamp_mysql`. The service names also works (_elasticsearch_ and _mysql_)
```ini
; Comma separated list of services to start, valid values: apache / bonita / elasticsearch / mailcatcher / maildev / mongo / mysql / php / phpmyadmin / xhgui
services=apache,php,mysql
```

A service can launch a post-start script that has the same name with an `.sh` extension (example: `services/mysql.sh`).

### Special case of xhgui service
To be able to profile your script, add the service xhgui and read the [documentation](https://github.com/inetprocess/docker-xhgui)


### Other useful parameters
Project name (will be used as container's prefix). It should be different for each project.
```ini
; Change Machines names only if you need it
project_name=lamp
```

PHP Version :
```ini
; Set your PHP version from 5.3 to 7.0 (5.6 by default)
php.version=7.0
```

MySQL Password if mysql is defined in the services list:
```ini
; Password set on first start. Once the data exist won't be changed
mysql.root_password=changeme
```

Memory assigned to the VMS:
```ini
apache.ram=512M
elasticsearch.ram=512M
mysql.ram=512M
php.ram=512M
```

# Files location
* All files served by the web server are located into `www/`
* MySQL data is into `mysql/` (created on the first run). If you need to override the mysql configuration you can put a file in `conf/mysql-override` with a `.cnf` extension. Logs for MySQL are also located into `mysql/` (slow and error).
* Mongo data is into `mongo/` (created on the first run)
* Logs for Apache and PHP are located into `logs/`
* If you need to override the PHP configuration you can put a file in `conf/php-fpm-override` with a `.conf` extension. The format is the fpm configuration files one. Example: `php_value[memory_limit] = 127M`.

## Add binaries
You can add binaries (such as phpunit) that will automatically be available from the PATH by putting it to
`home/www-data/bin/`


# Before running any command
You have to be in a virtual environement. If you have autoenv, and if you kept the name of the virtualenv as described above, just enter the directory, and it'll be automatically activated. Else:
```bash
$ source ${PWD##*/}_lamp/bin/activate
```

To leave that environment:
```bash
$ deactivate
```


# Usage
__WARNING: Make sure that you are in a virtual environment. To verify that, check that your prompt starts with something like `(xyz_lamp) `__

## Get Help
To get a list of commands do `lamp --help` and to get help for a specific command : `lamp start --help`


## Start the servers
Run `lamp start` to start the docker environment.

After the run you'll get something like that (contain all the useful URLs):
```bash
lamp is running

To access the web server use : http://172.18.0.7

For maildev use : http://172.18.0.6
            and in your VM use the server "maildev" with the port 25

For phpMyAdmin use : http://172.18.0.6
```

**INFO**: If you want to make sure that you have the latest images, do a `lamp start --pull --recreate` 


## Stop the servers
Run `lamp stop` to stop all applications.


## Restart the servers
Run `lamp restart` to restart all applications (_because you changed the config.ini or you overriden the php or mysql configuration_).


## Status
Run `lamp status` to see the list of running VMS


## Enter a VM
If you need to run some commands into a VM you can use the console mode by running `lamp console` with the vm name at the end (only PHP and MySQL are supported).

Example to enter the PHP Machine:
```bash
lamp console php
```

You can also define the user to run the commands with by setting `--user` (choices are _www-data_ or _root_)

**Be careful that all changes are overwritten when you change a parameter in the config and run a start that will update the images (in case the official images have been updated). If you need a definitive change, ask an sysadmin.**


## PHP usage
Use `lamp run php -f www/filename.php` to launch PHP scripts like if you were locally. The path is relative so launch everything from your docker project root (the same folder than this file). If you want to run it from a sub-directory, just use the full path of lamp (example: `/home/user/docker/lamp`) and the relative path of your file.

That:
```bash
cd /home/user/docker
lamp run php -f www/filename.php
```
Is equal to:
```bash
cd /home/user/docker/www
/home/user/docker/lamp run php -f filename.php
```

You can also use that command to run any PHP command (example: `lamp run php -v`). You can also define the user to run the commands with by setting `--user` (choices are _www-data_ or _root_)


## MySQL usage
Use `lamp run mysql` to enter the mysql console.


If you want to create a Database (You can also use the phpMyAdmin service of course):
```bash
lamp run mysql -e "CREATE DATABASE my_db;"
```

If you need to import a file, read it and pipe the command like below:
```bash
zcat file.sql.gz | lamp run mysql db
```

## DNS
If you want to have an access of your container via a hostname and not via its IP (mainly because the IP could change on each start),
start the dns server that will update your /etc/resolv.conf

To start it :
```bash
lamp dns start
```

To stop it :
```bash
lamp dns stop
```

**Warning**: you can start only one DNS for one instance of marina. It looks like a limitation of *mgood/resolve* that is not able to handle multiple networks. 

We also recommand to remove dnsmasq from Network Manager and to uninstall `libnss-mdns` (with `sudo apt-get remove libnss-mdns`)


# Plugins
## Writing a plugin
To write a plugin you need to create a folder in the plugins/ directory that contains your commands. Each file with a
`.py` extension will be taken as a plugin. The main function should be named exactly like the file.

Example for a file that is in `plugins/my_command/hi.py`:
```python
import click


@click.command(help="Example")
def hi():
    print('Hi!')
```

Once your plugin has been written you need to re-run:
```bash
$ lamp refresh-plugins
```

## Installing a plugin
To install a plugin
```bash
$ cd plugins/
$ git clone https://github.com/xyz/marina-myplugin myplugin
$ lamp refresh-plugins
```

You can, for example install the sugarcli plugin:
```bash
$ cd plugins/
$ git clone https://github.com/inetprocess/marina-sugarcli sugarcli
$ lamp refresh-plugins
```

As well as the composer one:
```bash
$ cd plugins/
$ git clone https://github.com/edyan/marina-composer composer
$ lamp refresh-plugins
```

## Define services in your plugins
By creating a `services/` directory you can either override or create new services with your plugins.
Example: `plugins/myplugin/services/mysql.yml` will override the default mysql service while `plugins/myplugin/services/nginx.yml` will define a new service.

Each service added by a plugin must be added in `compose.ini` to be started.


## List of existing plugins
* [marina-composer](https://github.com/edyan/marina-composer) : Download and run composer
* [marina-sugarcli](https://github.com/inetprocess/marina-sugarcli) : Download and run sugarcli
* [marina-phing](https://github.com/edyan/marina-phing) : Download and run Phing


