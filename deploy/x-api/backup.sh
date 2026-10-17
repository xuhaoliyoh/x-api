#!/usr/bin/env bash
set -euo pipefail
umask 077
cd /opt/x-api
mkdir -p backups
stamp=$(date -u +%Y%m%dT%H%M%SZ)
stage=$(mktemp -d backups/.pending-XXXXXX)
trap 'rm -rf "$stage"' EXIT
docker compose exec -T postgres pg_dump -U xapi -d xapi -Fc > "$stage/database.dump"
# Config and app-data contain encryption keys needed to restore upstream credentials.
cp .env compose.yaml "$stage/"
docker compose exec -T app tar -C /app/data -czf - . > "$stage/app-data.tar.gz"
tar -C "$stage" -czf "backups/$stamp.tar.gz.partial" .
mv "backups/$stamp.tar.gz.partial" "backups/$stamp.tar.gz"
# Keep completed backups for fourteen days; do not touch other files.
find backups -maxdepth 1 -type f -name '20??????T??????Z.tar.gz' -mtime +14 -delete
echo "X-API backup saved: /opt/x-api/backups/$stamp.tar.gz"
