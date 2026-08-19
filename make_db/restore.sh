#!/usr/bin/env bash

set -uo pipefail

USAGE=$(cat <<'EOF'
USAGE:

   bash restore.sh path/to/.env [-o|--overwrite]?

where --overwrite will delete the existing database named `$DB_NAME`
and recreate it with the contents of the dump file.
EOF
)

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# parse args: ENV_FILE and OVERWRITE
ENV_FILE="$1"
[[ "${2:-}" == "--overwrite" || "${2:-}" == "-o" ]] && OVERWRITE=true || OVERWRITE=false

# validate .env
if [ ! -f "$ENV_FILE" ]; then
  echo "$USAGE"
  echo "ERROR: .env file not found ! (looked at: '$ENV_FILE')"
  exit 1
fi
source "$ENV_FILE"

# admin connection: used for existence check / create / drop, since we can't
# connect with -d "$DB_NAME" until the database actually exists
CMD_PSQL_ADMIN=(psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d postgres)
# target connection: used once the db exists, to load the dump
CMD_PSQL=(psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$DB_NAME")

DB_EXISTS=false
if "${CMD_PSQL_ADMIN[@]}" -lqt | cut -d '|' -f 1 | grep -qw "$DB_NAME"; then
  DB_EXISTS=true
fi

# if the db exists and --overwrite wasn't passed, prompt the user
if $DB_EXISTS && [ "$OVERWRITE" != "true" ]; then
  read -p "database '$DB_NAME' exists. do you wish to overwrite its contents ? [y/n] " overwrite
  if [ "$overwrite" = "y" ]; then
    OVERWRITE=true
  else
    echo "database '$DB_NAME' already exists and was not recreated. exiting..."
    exit 1
  fi
fi

# either create or recreate the target db
if $DB_EXISTS; then
  "${CMD_PSQL_ADMIN[@]}" -c "DROP DATABASE \"$DB_NAME\";"
fi
"${CMD_PSQL_ADMIN[@]}" -c "CREATE DATABASE \"$DB_NAME\""

# populate it
"${CMD_PSQL[@]}" < "$DUMP_FILE"