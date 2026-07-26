$ROOT = "C:\Users\Cristan\OneDrive\Desktop\FXION-ONYX-FINAL"
$WORKER = "oberon"
$PASS = "St4ytruetoyou"
$POOL = "stratum+tcp://solo.ckpool.org:3333"
$BTC_ADDRESS = "REDACTED_PUBLIC_ADDRESS"

Set-Location $ROOT

New-Item -ItemType Directory -Force -Path ".\vault",".\logs",".\config" | Out-Null

Copy-Item ".\fxion_wallet.py" ".\fxion_wallet_backup_before_refine.py" -Force -ErrorAction SilentlyContinue

# Utilise ton adresse actuelle pour le worker

$config = @{
  pool = $POOL
  worker = $WORKER
  user = "$BTC_ADDRESS.$WORKER"
  pass = $PASS
  payout_address = $BTC_ADDRESS
  mode = "FXION_QZERO_OBERON"
  note = "Wallet payout + worker config. Ne jamais mettre private key ici."
}

$config | ConvertTo-Json -Depth 5 | Set-Content ".\config\miner_pool_config.json" -Encoding UTF8

$launcher = @"
@echo off
echo ==========================================
echo FXION QZERO OBERON MINING CONFIG
echo ==========================================
echo POOL: $POOL
echo USER: $BTC_ADDRESS.$WORKER
echo PASS: $PASS
echo.
echo Mettre ces valeurs dans ton ASIC SHA-256 / miner compatible Stratum.
echo Config sauvegardee: config\miner_pool_config.json
pause
"@

$launcher | Set-Content ".\START_OBERON_POOL.bat" -Encoding ASCII

"[$(Get-Date)] FXION refined + pool config active: $BTC_ADDRESS.$WORKER" |
  Add-Content ".\logs\fxion_refine.log"

Write-Host "[OK] FXION active/refined"
Write-Host "POOL: $POOL"
Write-Host "USER: $BTC_ADDRESS.$WORKER"
Write-Host "PASS: $PASS"
Write-Host "CONFIG: $ROOT\config\miner_pool_config.json"
Write-Host "LAUNCHER: $ROOT\START_OBERON_POOL.bat"
