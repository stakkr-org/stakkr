[main]
; Comma separated, valid values: mongo / mongoclient / mysql / mailcatcher (or maildev) / elasticsearch
; services=mongo,mailcatcher,elasticsearch,mysql

; Change Machines names only if you need it
; project_name=lamp

; Same for group id and user id
; uid=1005
; gid=1005

; Set your sugar version to 5.6 or 7.0 (5.6 by default)
; php.version=7.0
; php.ram=512M

; Set the max upload size for PMA
; phpmyadmin.upload_max_filesize=128M

; Set your apache version to 2.2
; apache.version=2.2
; apache.ram=512M

; Check https://hub.docker.com/_/mongo/ (3.3 by default)
; mongo.version=3.3

; Check https://hub.docker.com/_/mysql/ (5.7 by default)
; mysql.version=5.7
; mysql.ram=1024M
;
; Password set on first start. Once the data exist won't be changed
; mysql.root_password=changeme


; Check https://hub.docker.com/_/elasticsearch/
; elasticsearch.version=2
; elasticsearch.ram=512M
