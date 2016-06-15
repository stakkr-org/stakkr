## Uncomment for your sugar/PHP version
#source conf/php56.env
#source conf/php70.env


# Set the mysql root password.
MYSQL_ROOT_PASSWORD="changeme"

# Change Machines names only if you need it
COMPOSE_PROJECT_NAME="dockerlamop"
COMPOSE_PROJECT_NAME+=$(basename `pwd`)
