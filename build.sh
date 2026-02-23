#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Starting Ziada Travel build process..."
python3 -m pip install --upgrade pip
pip install -r requirements.txt
echo "📦 Dependencies installed successfully"
python3 manage.py collectstatic --noinput --settings=tours_travels.settings_prod
echo "📁 Static files collected"
python3 manage.py migrate --settings=tours_travels.settings_prod
echo "🗄️ Database migrations applied"
python3 manage.py createcachetable --settings=tours_travels.settings_prod
echo "💾 Cache table created"
echo "✅ Build completed successfully"
