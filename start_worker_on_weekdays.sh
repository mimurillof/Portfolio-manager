#!/usr/bin/env bash
set -euo pipefail

# Día de la semana (1=Lunes, 5=Viernes)
DOW=$(date +%u)

if [ "$DOW" -lt 6 ]; then
  echo "Día laboral (DOW=$DOW). Encendiendo el worker..."
  APP_NAME="${HEROKU_APP_NAME:-portofolio-manager-horizon}"

  if command -v heroku >/dev/null 2>&1; then
    heroku ps:scale worker=1 -a "$APP_NAME"
  else
    if [ -z "${HEROKU_API_KEY:-}" ]; then
      echo "HEROKU_API_KEY no está definido; no se puede escalar el worker."
      exit 1
    fi

    API_HOST="${HEROKU_API_HOST:-https://api.heroku.com}"
    set +e
    RESPONSE=$(curl --silent --show-error \
      --request PATCH \
      --header "Accept: application/vnd.heroku+json; version=3" \
      --header "Content-Type: application/json" \
      --header "Authorization: Bearer ${HEROKU_API_KEY}" \
      --data '{"quantity":1}' \
      "${API_HOST}/apps/${APP_NAME}/formation/worker" \
      --write-out "HTTPSTATUS:%{http_code}")
    CURL_EXIT=$?
    set -e

    if [ "$CURL_EXIT" -ne 0 ]; then
      echo "Error de red al invocar la API de Heroku (exit $CURL_EXIT)."
      exit "$CURL_EXIT"
    fi

    HTTP_STATUS=${RESPONSE##*HTTPSTATUS:}
    BODY=${RESPONSE%HTTPSTATUS:*}

    if [ "$HTTP_STATUS" -ge 200 ] && [ "$HTTP_STATUS" -lt 300 ]; then
      echo "Escalado del worker completado vía API (HTTP $HTTP_STATUS)."
    else
      echo "Fallo al escalar el worker (HTTP $HTTP_STATUS): ${BODY}"
      exit 1
    fi
  fi
else
  echo "Fin de semana (DOW=$DOW). No se enciende el worker."
fi