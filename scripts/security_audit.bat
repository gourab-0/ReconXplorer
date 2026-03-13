@echo off
echo [INFO] Running Dependency Security Audit...

echo [INFO] Checking Python dependencies...
cd backend
pip install pip-audit --quiet
pip-audit
cd ..

echo [INFO] Checking Frontend dependencies...
cd frontend/dashboard
npm audit
cd ../..

echo [INFO] Audit Complete.
