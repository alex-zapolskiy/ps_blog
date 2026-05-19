#!/usr/bin/env bash
# Остановка при ошибке
set -o errexit

# Установка зависимостей
pip install -r requirements.txt

# Сбор статических файлов
python manage.py collectstatic --no-input

# Применение миграций базы данных
python manage.py migrate