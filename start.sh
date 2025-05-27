#!/bin/bash

# Crea el archivo temporal con el cronjob
echo "0 5-21 * * 0-5 USERNAME=$USERNAME PASSWORD=$PASSWORD python3 /app/main.py >> /var/log/cron.log 2>&1" > /tmp/mycron

# Instala el cronjob para el usuario root
crontab /tmp/mycron

# Borra el archivo temporal si quieres (opcional)
rm /tmp/mycron

# Asegúrate que el log existe
touch /var/log/cron.log

# Inicia el demonio cron en background
cron

# Mantiene el container vivo mostrando logs
tail -f /var/log/cron.log
