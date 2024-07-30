#!/bin/sh
rm -rf db_folder
mkdir db_folder
mongod --port $1 --dbpath ./db_folder --quiet &
python3 load-json.py $1 $2