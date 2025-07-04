#!/bin/bash
set -e

# --- Wait for Database ---
# A simple function to wait for the PostgreSQL container to be ready.
wait_for_db() {
  echo "Waiting for database to be ready..."
  # The `pg_isready` command checks the connection status.
  # We use a loop to keep checking until it succeeds.
  until docker-compose exec -T postgres pg_isready -U user -d findb; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 1
  done
  >&2 echo "Postgres is up - executing commands"
}

# --- Main Execution ---

# 1. Run Database Migrations
# This command uses pnpm to run the prisma migrate script, which sets up the database schema.
echo "Running database migrations..."
pnpm --filter database db:migrate

# 2. Install Python Dependencies
echo "Installing Python dependencies for data-adapter..."
(cd packages/data-adapter && poetry install --no-root)

# 3. Seed the Database
# This command runs the python script to add the essential analysis templates to the database.
# We run it from the data-adapter directory within the poetry environment.
echo "Seeding the database with analysis templates..."
(cd packages/data-adapter && poetry run python ../../scripts/seed_template.py)

echo "Setup complete. Starting the web server..."

# 4. Start the Web Server
# This is the original command for the web service. `exec "$@"` passes control to it.
exec "$@" 