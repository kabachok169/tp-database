#!/usr/bin/env bash

service postgresql start
psql -h localhost -U anton -d anton -f ./schema.sql
python3 ./src/app.py