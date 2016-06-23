#!/bin/bash
docker exec -i $1 bash -c 'mysql -p$MYSQL_ROOT_PASSWORD -e "SET GLOBAL max_allowed_packet = 104857600;"'
