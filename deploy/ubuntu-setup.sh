#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y python3 python3-venv
cd /home/ubuntu/wraith
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
sudo cp deploy/beelzebub-simulator.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable beelzebub-simulator.service
