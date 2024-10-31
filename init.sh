#!/bin/bash

# Path to the password file
PWFILE="/mosquitto/config/pwfile"

# Create SQLite3 database if it doesn't exist
DB_DIR="./mosquitto/data"
DB_FILE="$DB_DIR/mosquitto.db"

if [ ! -d "$DB_DIR" ]; then
    mkdir -p "$DB_DIR"
fi

if [ ! -f "$DB_FILE" ]; then
    sqlite3 "$DB_FILE" ".databases"
    echo "SQLite3 database created at $DB_FILE"
fi

# List of users and passwords
declare -A USERS
USERS=(
  ["fastapi"]="fastapi"
  ["arduino"]="arduino"
)

first_user=true
for user in "${!USERS[@]}"; do
  if $first_user; then
    docker compose run --rm mqtt5 mosquitto_passwd -c -b $PWFILE "$user" "${USERS[$user]}"
    first_user=false
  else
    docker compose run --rm mqtt5 mosquitto_passwd -b $PWFILE "$user" "${USERS[$user]}"
  fi
done
