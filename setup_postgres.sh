#!/bin/bash

# setup_postgres.sh - Установка и настройка PostgreSQL на macOS

set -e  # Остановить скрипт при ошибке

echo "=== Настройка PostgreSQL на macOS ==="

# Проверяем, установлен ли Homebrew
if ! command -v brew &> /dev/null; then
    echo "Установка Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
    source ~/.zshrc
else
    echo "✓ Homebrew уже установлен"
fi

# Проверяем, установлен ли PostgreSQL
if ! brew list postgresql@16 &> /dev/null; then
    echo "Установка PostgreSQL 16..."
    brew install postgresql@16
    
    # Добавляем PostgreSQL в PATH
    echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
    source ~/.zshrc
else
    echo "✓ PostgreSQL уже установлен"
fi

# Запускаем PostgreSQL сервис
echo "Запуск PostgreSQL..."
brew services start postgresql@16

# Ждем запуска сервиса
sleep 5

# Настройка переменных окружения
DB_NAME="askme_db"
DB_USER="askme_user"
DB_PASSWORD=$(openssl rand -base64 12)  # Генерация случайного пароля
DB_HOST="localhost"
DB_PORT="5432"

echo ""
echo "=== Создание базы данных и пользователя ==="

# Создаем пользователя и базу данных
echo "Создание пользователя: $DB_USER"
psql postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" || echo "Пользователь уже существует или ошибка"

echo "Создание базы данных: $DB_NAME"
psql postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" || echo "База данных уже существует или ошибка"

# Даем все права пользователю на базу данных
echo "Настройка прав..."
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo ""
echo "=== Настройка завершена! ==="
echo ""
echo "Данные для подключения Django:"
echo "DB_NAME=$DB_NAME"
echo "DB_USER=$DB_USER"
echo "DB_PASSWORD=$DB_PASSWORD"
echo "DB_HOST=$DB_HOST"
echo "DB_PORT=$DB_PORT"
echo ""
echo "Добавьте эти значения в ваш .env файл"
echo "или settings.py Django"
echo ""
echo "Для остановки PostgreSQL: brew services stop postgresql@16"
echo "Для перезапуска: brew services restart postgresql@16"