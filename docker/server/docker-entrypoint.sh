#!/bin/bash
set -e

# Create the log files
>&2 echo "Touching log files"
touch /data/web/logs/django.log
touch /data/web/logs/project.log
touch /data/web/logs/scheduler.log
touch /data/web/logs/script.log
touch /data/web/logs/celery.log
chown -R www-data.www-data /data/web/logs

cd $PROJECT_DIR

# Apply migrations
>&2 echo "Migrating"
python3 manage.py migrate --noinput

# Initial data
>&2 echo "Creating initial data (instructors)"
python3 manage.py initialize_db -i $PROJECT_DIR/scripts/initial_instructors.csv

>&2 echo "Creating initial data (learners)"
python3 manage.py initialize_db $PROJECT_DIR/scripts/initial_learners.csv

>&2 echo "Creating superuser "
python3 manage.py create_superuser -u '$SUPERUSER_NAME' -e '$SUPERUSER_EMAIL' -p '$SUPERUSER_PWD'

# Collect static
>&2 echo "Collecting static"
python3 manage.py collectstatic --noinput

# Change ownership of the whole project
chown -R www-data.www-data /data/web

# Wait for the database to be up and running
until psql $DATABASE_URL -c '\l'; do
 >&2 echo "Postgres is not available in $DATABASE_URL - sleeping"
 sleep 3
done

>&2 echo "Postgres is up in $DATABASE_URL - continuing"

exec "$@"
