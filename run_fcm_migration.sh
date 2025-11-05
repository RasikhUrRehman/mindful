#!/bin/bash
# Script to create and run Alembic migration for FCM token

echo "Creating Alembic migration for FCM token..."

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "Running inside Docker container"
    alembic revision --autogenerate -m "add_fcm_token_to_users"
    alembic upgrade head
else
    echo "Running outside Docker - using docker-compose exec"
    docker-compose exec api alembic revision --autogenerate -m "add_fcm_token_to_users"
    docker-compose exec api alembic upgrade head
fi

echo "Migration completed successfully!"
