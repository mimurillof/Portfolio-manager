#!/usr/bin/env bash
echo "Apagando el worker al final del día..."
heroku ps:scale worker=0 -a portofolio-manager-horizon