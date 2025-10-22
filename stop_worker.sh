#!/usr/bin/env bash
set -euo pipefail

echo "Apagando el worker al final del día..."

# Usa Python con el paquete requests (ya instalado en tu app)
python3 - <<'PYTHON_SCRIPT'
import os
import sys
import requests

app_name = os.getenv("HEROKU_APP_NAME", "portofolio-manager-horizon")
api_key = os.getenv("HEROKU_API_KEY")

if not api_key:
    print("ERROR: HEROKU_API_KEY no está configurado.", file=sys.stderr)
    print("Configúralo con: heroku config:set HEROKU_API_KEY=$(heroku auth:token) -a {}".format(app_name), file=sys.stderr)
    sys.exit(1)

url = f"https://api.heroku.com/apps/{app_name}/formation/worker"
headers = {
    "Accept": "application/vnd.heroku+json; version=3",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}
data = {"quantity": 0}

try:
    response = requests.patch(url, json=data, headers=headers, timeout=10)
    response.raise_for_status()
    print(f"✓ Worker apagado exitosamente (HTTP {response.status_code}).")
    print(f"  Detalles: {response.json()}")
except requests.exceptions.HTTPError as e:
    print(f"✗ Error HTTP {e.response.status_code}: {e.response.text}", file=sys.stderr)
    sys.exit(1)
except requests.exceptions.RequestException as e:
    print(f"✗ Error de red: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT