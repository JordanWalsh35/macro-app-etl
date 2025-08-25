#!/bin/bash
set -e

APP_USER="ubuntu"
APP_DIR="/home/ubuntu/macro-app-etl"
SERVICE_NAME="streamlit"

# Write the systemd unit
sudo tee /etc/systemd/system/${SERVICE_NAME}.service >/dev/null <<EOF
[Unit]
Description=Streamlit App
After=network.target

[Service]
User=${APP_USER}
WorkingDirectory=${APP_DIR}
Environment=PATH=${APP_DIR}/.venv/bin
#EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/.venv/bin/streamlit run "_01. Business Cycle.py" --server.address 0.0.0.0 --server.port 8501
Restart=always
RestartSec=5
StandardOutput=append:${APP_DIR}/streamlit.out.log
StandardError=append:${APP_DIR}/streamlit.err.log

[Install]
WantedBy=multi-user.target
EOF

# Reload, enable on boot, start now (use restart for idempotency)
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl restart ${SERVICE_NAME}

echo "Service ${SERVICE_NAME} installed and started."
echo "ℹStatus: sudo systemctl status ${SERVICE_NAME}"
echo "Logs:   journalctl -u ${SERVICE_NAME} -f"
