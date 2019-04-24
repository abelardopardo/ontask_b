#!/usr/bin/env bash
psql -U postgres -c "CREATE USER $DB_USER"
psql -U postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER"
