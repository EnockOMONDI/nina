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

# Smoke test admin login page render to catch production-only 500s before release.
# Use HTTPS + follow redirects so SECURE_SSL_REDIRECT does not create a false failure.
python3 manage.py shell --settings=tours_travels.settings_prod -c "from django.test import Client; c=Client(); r=c.get('/admin/login/?next=/admin/', HTTP_HOST='ninatoursandtravel.com', secure=True, follow=True); print(f'✅ Admin login smoke final status: {r.status_code} redirects={len(getattr(r, \"redirect_chain\", []))}'); raise SystemExit(1 if r.status_code != 200 else 0)"
echo "✅ Admin login smoke test passed"

python3 manage.py collectstatic --noinput --settings=tours_travels.settings_prod
echo "📁 Static files collected"
python3 manage.py createcachetable --settings=tours_travels.settings_prod
echo "💾 Cache table created"
echo "✅ Build completed successfully"
