#!/usr/bin/env bash
# Forward local 3307 -> MySQL on EC2-DB-01 (127.0.0.1:3306 on the instance).
# Usage: EC2_SSH_KEY=~/keys/my.pem ./scripts/ec2-db-tunnel.sh

set -euo pipefail

EC2_HOST="${EC2_HOST:-52.66.146.75}"
EC2_SSH_USER="${EC2_SSH_USER:-ec2-user}"
LOCAL_PORT="${LOCAL_PORT:-3307}"
REMOTE_PORT="${REMOTE_PORT:-3306}"
SSH_KEY="${EC2_SSH_KEY:?Set EC2_SSH_KEY to your .pem file path}"

echo "Tunnel: 127.0.0.1:${LOCAL_PORT} -> ${EC2_HOST}:${REMOTE_PORT}"
echo "In .env set DB_HOST=127.0.0.1 and DB_PORT=${LOCAL_PORT}"
echo "Leave this running while you use Django."
exec ssh -i "$SSH_KEY" -N -L "${LOCAL_PORT}:127.0.0.1:${REMOTE_PORT}" "${EC2_SSH_USER}@${EC2_HOST}"