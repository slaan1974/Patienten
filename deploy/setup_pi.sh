#!/bin/bash
set -e

echo "=== Patient Management System - Raspberry Pi Setup ==="

PROJECT_DIR="$HOME/Patient"

if [ ! -d "$PROJECT_DIR/backend" ]; then
  echo "ERROR: Could not find $PROJECT_DIR/backend"
  echo "Make sure you copied the project to $PROJECT_DIR first."
  echo ""
  echo "From your development machine, run:"
  echo "  rsync -avz --exclude='__pycache__' --exclude='.pytest_cache' \\"
  echo "    --exclude='node_modules' --exclude='venv' --exclude='*.db' \\"
  echo "    /home/slaan1974/Documents/Patient/ pi@<pi-ip>:~/Patient/"
  exit 1
fi

echo ""
echo "1. Creating Python virtual environment..."
cd "$PROJECT_DIR/backend"
python3 -m venv venv
source venv/bin/activate

echo ""
echo "2. Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "3. Creating .env file with a secure secret key..."
if [ ! -f .env ]; then
  SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  cat > .env << EOF
SECRET_KEY=$SECRET
EOF
  echo "   .env created"
else
  echo "   .env already exists, skipping"
fi

echo ""
echo "4. Installing systemd service..."
sudo tee /etc/systemd/system/patient.service > /dev/null << 'SVC'
[Unit]
Description=Patient Management System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Patient/backend
ExecStart=/home/pi/Patient/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8002
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVC

sudo systemctl daemon-reload
sudo systemctl enable patient
sudo systemctl start patient

echo ""
echo "5. Checking service status..."
sleep 3
sudo systemctl status patient --no-pager
curl -s http://localhost:8002/api/health

echo ""
echo "=== Setup complete! ==="
echo "The app is running at http://$(hostname -I | awk '{print $1}'):8002"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status patient   - Check status"
echo "  sudo journalctl -u patient -f   - Follow logs"
echo "  sudo systemctl restart patient  - Restart the service"
