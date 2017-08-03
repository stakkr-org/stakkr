#!/bin/bash
for i in $(seq 1 90); do
    docker exec -i $1 bash -c 'mysql -p$MYSQL_ROOT_PASSWORD -e "SHOW DATABASES"' > /dev/null 2>&1

    if [ $i -gt 3 ]; then
        echo "Waiting for MySQL ."
    elif [ $i -gt 4 ]; then
        echo "."
    fi


    if [ $? -eq 0 ]; then
        break
    fi
done
# the following has been moved to a custom conf folder:
#docker exec -i $1 bash -c 'mysql -p$MYSQL_ROOT_PASSWORD -e "SET GLOBAL max_allowed_packet = 104857600;"' > /dev/null 2>&1
