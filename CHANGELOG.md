# v0.9
* Minor issue with DNSes (docker error message was displayed)

# v0.8
* Added DNSes to have a local resolution of containers names (See documentation)
* Solved a problem with MySQL 5.7 as the /var/log/mysql does not have the right permissions. Logs are now in mysql/ (and not in logs/mysql/)
* Added Bonita as a service (Thanks rbindels)

# v0.7
* Updated images

# v0.6
* Added a new --pull option to start
* Added an xhgui service and defined hostnames for each container
