#!/bin/sh
mongod --port $1 --dbpath ./db_folder -shutdown
rm -rf db_folder