import shutil
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


def switch_env(target):
    if target == "dev":
        source = BASE_DIR / ".env.development"
    elif target == "prod":
        candidates = [
            BASE_DIR / ".env.production",
            BASE_DIR / ".env.production.fixed",
            BASE_DIR / ".env.production.template",
        ]
        source = next((item for item in candidates if item.exists()), None)
    else:
        raise ValueError("Use 'dev', 'prod', or 'status'.")

    if target in ("dev", "prod"):
        if ENV_FILE.exists():
            shutil.copyfile(ENV_FILE, BASE_DIR / ".env.backup")
        if source and source.exists():
            shutil.copyfile(source, ENV_FILE)
            print(f"Switched to {target} environment.")
        else:
            if ENV_FILE.exists():
                content = ENV_FILE.read_text()
                content = content.replace("DEBUG=True", "DEBUG=False")
                content = content.replace("PRODUCTION_ENVIRONMENT=False", "PRODUCTION_ENVIRONMENT=True")
                ENV_FILE.write_text(content)
                print("Set production flags in .env.")
            else:
                print("No .env found to update.")

        print("Next steps:")
        print("- Restart server")
        print("- Run: python manage.py runserver 8005")


def status():
    if not ENV_FILE.exists():
        print(".env file not found")
        return
    content = ENV_FILE.read_text()
    debug = "DEBUG=True" in content
    site_url = None
    for line in content.splitlines():
        if line.startswith("SITE_URL="):
            site_url = line.split("=", 1)[1]
            break
    print(f"DEBUG={debug}")
    print(f"SITE_URL={site_url}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python switch_env.py dev|prod|status")
        sys.exit(1)
    cmd = sys.argv[1].strip().lower()
    if cmd == "status":
        status()
    else:
        switch_env(cmd)
