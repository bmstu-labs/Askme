#!/bin/bash
set -e

if [[ "$OSTYPE" == "darwin"* ]]; then
    brew services start postgresql@16
    sleep 5
    PSQL_CMD="psql"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v systemctl &> /dev/null; then
        sudo systemctl start postgresql
        sleep 3
    elif command -v service &> /dev/null; then
        sudo service postgresql start
        sleep 3
    fi
    PSQL_CMD="sudo -u postgres psql"
else
    echo "Unsupported OS"
    exit 1
fi

DB_NAME="askme_db"
DB_USER="askme_user"
DB_PASSWORD=$(openssl rand -base64 12)
DB_HOST="localhost"
DB_PORT="5432"

echo "Creating database and user"
$PSQL_CMD postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || true
$PSQL_CMD postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || true
$PSQL_CMD postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo "Database setup complete"
echo "DB_NAME=$DB_NAME"
echo "DB_USER=$DB_USER"
echo "DB_PASSWORD=$DB_PASSWORD"
echo "DB_HOST=$DB_HOST"
echo "DB_PORT=$DB_PORT"