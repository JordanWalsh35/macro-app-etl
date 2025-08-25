#!/bin/bash
set -e  # stop if any command fails

# Update package lists
sudo apt-get update -y

# Install packages
sudo apt-get install -y python3.12-venv

# Adjust path/user
APP_DIR="/home/ubuntu/macro-app-etl"
cd "$APP_DIR"

# Create venv
PYBIN=$(command -v python3)
"$PYBIN" -m venv .venv
source .venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Install PostgreSQL client (if running pg_dump/restore locally)
sudo apt-get install -y postgresql-client

# Print when complete
echo "Setup complete."