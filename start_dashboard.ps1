# Start Dashboard with dependency installation
Write-Host "🚀 Installing Dashboard Dependencies..." -ForegroundColor Cyan
python -m pip install flask flask-cors psutil --quiet

Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host "🌐 Starting Ultimate Adaptive ECMP Dashboard..." -ForegroundColor Cyan
python ultimate_dashboard.py
