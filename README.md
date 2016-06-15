Docker-lamp
=====

Docker compose for a lamp stack (with MongoDB and not MySQL!).


Docker installation
=====
Read https://docs.docker.com/engine/installation/ubuntulinux/ but in summary (be careful to define the right user):
```
sudo su - 
apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
nano /etc/apt/sources.list.d/docker.list
# add the right repo according to the doc. Such as:
# deb https://apt.dockerproject.org/repo ubuntu-trusty main
apt-get update
apt-get purge lxc-docker
apt-get install linux-image-extra-$(uname -r)
apt-get install docker-engine
service docker start
usermod -aG docker {LDAP USER}
```

Reboot your computer

Docker compose installation
=====
Read https://docs.docker.com/compose/install/
```
sudo su - 
curl -L https://github.com/docker/compose/releases/download/1.5.2/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
exit
```

Verify with `docker-compose --version`


Configuration
-----
Copy the file `conf/compose.env.tpl` to `conf/compose.env` and set the right PHP Version.
```
source conf/php70.env
```

Informations
----
Mongo Server : mongo

SMTP Server : smtp

Mail catcher interface: http://{yourip}:1080


First start or update
----
Run `./lamop fullstart` to build and start the docker environment.

Quick start
-----
Run `./lamop start` to start the docker environment.

Access your environment with http://{yourip}
Be careful not to use 127.0.0.1 or localhost

Stop
----
Run `./lamop stop` to stop all applications.


PHP usage
----
Use `bin/php www/filename.php` to launch PHP scripts like if you were locally. The path is relative so launch everything from your docker project root (the same folder than this file).
