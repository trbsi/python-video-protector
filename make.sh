#!/usr/bin/env bash
# protectapp.sh - Docker + Django helper script

set -e  # Exit immediately if a command fails

DOCKER_DIR="./docker"
DJANGO_CONTAINER="protectapp-django"

# Functions
builddocker() {
    echo "Building and starting Docker containers..."
    cd "$DOCKER_DIR"
    docker compose up -d --build
    cd - >/dev/null
}

migrate() {
    echo "Running Django migrations..."
    docker exec -it "$DJANGO_CONTAINER" poetry run python manage.py migrate
}

makemigrations() {
    echo "Creating Django migrations..."
    docker exec -it "$DJANGO_CONTAINER" poetry run python manage.py makemigrations
}

seed() {
    echo "Seeding..."
    docker exec -it "$DJANGO_CONTAINER" poetry run python manage.py seed_database_command local --truncate
}

test() {
    docker exec -it "$DJANGO_CONTAINER" poetry run python manage.py test
}

# Parse command-line argument
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 {builddocker|migrate|makemigrations}"
    exit 1
fi

case "$1" in
    builddocker)
        builddocker
        ;;
    migrate)
        migrate
        ;;
    makemigrations)
        makemigrations
        ;;
    seed)
        seed
        ;;
    test)
        test
        ;;
    *)
        echo "Unknown command: $1"
        echo "Usage: $0 {builddocker|migrate|makemigrations}"
        exit 1
        ;;
esac
