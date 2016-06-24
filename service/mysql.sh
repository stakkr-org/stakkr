#!/bin/bash
for i in $(seq 1 90); do
    docker exec -i $1 bash -c 'mysql -p$MYSQL_ROOT_PASSWORD -e "SHOW DATABASES"' > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        break
    fi
done
docker exec -i $1 bash -c 'mysql -p$MYSQL_ROOT_PASSWORD -e "SET GLOBAL max_allowed_packet = 104857600;"'
