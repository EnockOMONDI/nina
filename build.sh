#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Starting Nina tours build process..."
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-tours_travels.settings_prod}"

python3 -m pip install --upgrade pip
pip install -r requirements.txt
echo "📦 Dependencies installed successfully"

# Fail fast if model changes exist but migration files were not committed.
python3 manage.py makemigrations --check --dry-run --settings=tours_travels.settings_prod
echo "🧭 Migration files check passed"

# Apply DB schema updates before app boots.
python3 manage.py migrate --noinput --settings=tours_travels.settings_prod
echo "🗄️ Database migrations applied"

# Confirm no pending migrations remain (helps detect wrong DB target during deploy).
python3 manage.py showmigrations --settings=tours_travels.settings_prod
python3 manage.py shell --settings=tours_travels.settings_prod -c "from django.db import connections; from django.db.migrations.executor import MigrationExecutor; c=connections['default']; e=MigrationExecutor(c); t=e.loader.graph.leaf_nodes(); p=e.migration_plan(t); print(f'✅ Pending migrations: {len(p)}'); raise SystemExit(1 if p else 0)"
echo "✅ Migration verification passed"

python3 manage.py collectstatic --noinput --settings=tours_travels.settings_prod
echo "📁 Static files collected"
python3 manage.py createcachetable --settings=tours_travels.settings_prod
echo "💾 Cache table created"
echo "✅ Build completed successfully"
