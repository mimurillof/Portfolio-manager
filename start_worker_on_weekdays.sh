#!/usr/bin/env bash
# Día de la semana (1=Lunes, 5=Viernes)
DOW=$(date +%u)

if [ "$DOW" -lt 6 ]; then
  # Si es de Lunes a Viernes, enciende el worker.
  echo "Día laboral (DOW=$DOW). Encendiendo el worker..."
  heroku ps:scale worker=1 -a portofolio-manager-horizon
else
  # Si es fin de semana, no hace nada.
  echo "Fin de semana (DOW=$DOW). No se enciende el worker."
fi