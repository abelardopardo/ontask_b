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

# Create the documentation
>&2 echo "Creating the documentation"
cd $PROJECT_DIR/docs_src
make clean html copy_to_docs

cd $PROJECT_DIR/src

# Apply migrations
>&2 echo "Migrating"
python3 manage.py migrate --noinput

# Initial data
>&2 echo "Creating initial data (instructors)"
python3 manage.py initialize_db -i $PROJECT_DIR/src/scripts/initial_instructors.csv

>&2 echo "Creating initial data (learners)"
python3 manage.py initialize_db $PROJECT_DIR/src/scripts/initial_learners.csv

>&2 echo "Creating superuser "
python3 manage.py create_superuser

# Collect static
>&2 echo "Collecting static"
python3 manage.py collectstatic --noinput

# Start supervisor
# >&2 echo "Starting supervisor"
# supervisord -c $PROJECT_DIR/supervisor/supervisor.conf

# Wait for the database to be up and running
until psql $DATABASE_URL -c '\l'; do
 >&2 echo "Postgres is not available in $DATABASE_URL - sleeping"
 sleep 3
done

>&2 echo "Postgres is up in $DATABASE_URL - continuing"

exec "$@"
