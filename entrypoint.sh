#!/bin/bash

DB_NAME="recruitment_db_azsj"
DB_USER="odoo15__2022"
DB_HOST="dpg-d3bk0mali9vc73cr2j50-a"
DB_PASSWORD="myObBrEeNvS573HJPDDNRyxVA1wuTClt"
DUMP_FILE="/recruitment_db.dump"

export PGPASSWORD=$DB_PASSWORD

# Chờ PostgreSQL sẵn sàng
until pg_isready -h $DB_HOST -U $DB_USER; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Khôi phục database nếu chưa tồn tại
if ! psql -h $DB_HOST -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
  echo "Restoring database from dump..."
  createdb -h $DB_HOST -U $DB_USER $DB_NAME
  pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME $DUMP_FILE
else
  echo "Database already exists, skipping restore."
fi

# Chạy Odoo
exec python3 /odoo/odoo-bin -c /etc/odoo/odoo.conf
