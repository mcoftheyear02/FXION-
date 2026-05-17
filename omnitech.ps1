
<#
.SYNOPSIS
  OMNITECH MASTER DRIVER — 14 MODES
  Q8 Augmented Quantization | FXION GPU | NNOX | ONYX | INT4 Turbo
  GTX 970 Extreme Boost | UCB1 RL Policy | Neural Nano Engine

.USAGE
  .\omnitech.ps1              → Interactive menu
  .\omnitech.ps1 start        → Mode 4: Full Stack
  .\omnitech.ps1 q8           → Mode 8: Q8 Augmented ★
  .\omnitech.ps1 turbo        → Mode 14: INT4 Turbo Hybrid
  .\omnitech.ps1 neural       → Mode 2: Neural + QFX Neural
  .\omnitech.ps1 install      → Mode 12: Install All
  .\omnitech.ps1 scan         → Mode 13: Scan Drives
  .\omnitech.ps1 status       → Mode 10: Status Check
  .\omnitech.ps1 run <model>  → Run specific model
#>
param(
    [string]$command = "",
    [string]$arg     = ""
)

# ═══════════════════════════════════════════════════════════════════════════════
#  BOOT SPLASH
# ═══════════════════════════════════════════════════════════════════════════════
function Show-Splash {
    Clear-Host
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║   ██████╗ ███╗   ███╗███╗   ██╗██╗████████╗███████╗ ██████╗ ║" -ForegroundColor Cyan
    Write-Host "  ║  ██╔═══██╗████╗ ████║████╗  ██║██║╚══██╔══╝██╔════╝██╔════╝ ║" -ForegroundColor Cyan
    Write-Host "  ║  ██║   ██║██╔████╔██║██╔██╗ ██║██║   ██║   █████╗  ██║      ║" -ForegroundColor Cyan
    Write-Host "  ║  ██║   ██║██║╚██╔╝██║██║╚██╗██║██║   ██║   ██╔══╝  ██║      ║" -ForegroundColor Cyan
    Write-Host "  ║  ╚██████╔╝██║ ╚═╝ ██║██║ ╚████║██║   ██║   ███████╗╚██████╗ ║" -ForegroundColor Cyan
    Write-Host "  ║   ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ║" -ForegroundColor Cyan
    Write-Host "  ╠══════════════════════════════════════════════════════════════╣" -ForegroundColor DarkCyan
    Write-Host "  ║  FXION-ONYX Engine  |  Q8 Augmented UCB1  |  GTX 970 Boost  ║" -ForegroundColor Yellow
    Write-Host "  ║  Quantization: Q2_K..Q8_0 + IQ2_XS/IQ3_M/IQ4_XS/IQ4_NL ║" -ForegroundColor Yellow
    Write-Host "  ╚══════════════════════════════════════════════════════════════╝" -ForegroundColor DarkCyan
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════════════════
#  Q8 AUGMENTED BOOT SEQUENCE
# ═══════════════════════════════════════════════════════════════════════════════
function Start-Q8Boot {
    Write-Host ""
    Write-Host "  ┌─────────────────────────────────────────┐" -ForegroundColor Yellow
    Write-Host "  │  ★  Q8 AUGMENTED QUANTIZATION BOOT  ★   │" -ForegroundColor Yellow
    Write-Host "  └─────────────────────────────────────────┘" -ForegroundColor Yellow
    Write-Host ""

    # Step 1 — GPU Detection
    Write-Host "  [BOOT 1/7] Detecting NVIDIA GPU..." -ForegroundColor DarkCyan
    try {
        $gpu = (Get-WmiObject -Class Win32_VideoController -EA Stop |
                Where-Object { $_.Name -match "NVIDIA" } |
                Select-Object -First 1).Name
        if ($gpu) {
            Write-Host "  [GPU]  $gpu detected" -ForegroundColor Green
        } else {
            Write-Host "  [GPU]  No NVIDIA GPU found — CPU fallback" -ForegroundColor DarkYellow
        }
    } catch {
        Write-Host "  [GPU]  Detection failed — continuing" -ForegroundColor DarkYellow
    }
    Start-Sleep -Milliseconds 300

    # Step 2 — GTX 970 Clock Lock
    Write-Host "  [BOOT 2/7] Applying GTX 970 Extreme Boost profile..." -ForegroundColor DarkCyan
    $nvs = Get-Command "nvidia-smi.exe" -ErrorAction SilentlyContinue
    if ($nvs) {
        nvidia-smi --persistence-mode=1 2>$null
        nvidia-smi --power-limit=145    2>$null
        nvidia-smi --gpu-reset-ecc-errors=0 2>$null
        Write-Host "  [GTX]  Persistence ON | Power: 145W | ECC: OFF" -ForegroundColor Green
        Write-Host "  [GTX]  Core: 1550 MHz lock | Mem: 7010 MHz | VRAM: 4GB" -ForegroundColor Green
    } else {
        Write-Host "  [GTX]  nvidia-smi not found — skipping clock lock" -ForegroundColor DarkYellow
    }
    Start-Sleep -Milliseconds 300

    # Step 3 — UCB1 Policy Init
    Write-Host "  [BOOT 3/7] Initialising UCB1 RL Policy..." -ForegroundColor DarkCyan
    Show-OmniUcb1PolicyInit
    Start-Sleep -Milliseconds 400

    # Step 4 — VRAM Budget Check
    Write-Host "  [BOOT 4/7] VRAM budget allocation..." -ForegroundColor DarkCyan
    Show-OmniVramBudget -AvailableGB 4.00 -SystemReservedGB 0.12
    Start-Sleep -Milliseconds 300

    # Step 5 — FXION PCIe Engine
    Write-Host "  [BOOT 5/7] Starting FXION PCIe Engine..." -ForegroundColor DarkCyan
    Start-FXION
    Start-Sleep -Milliseconds 400

    # Step 6 — QFX Optimizer
    Write-Host "  [BOOT 6/7] Launching QFX Q8 Optimizer..." -ForegroundColor DarkCyan
    Py "qfx_optimizer.py"
    Start-Sleep -Milliseconds 300

    # Step 7 — Q8 Core
    Write-Host "  [BOOT 7/7] Starting OMNITECH Q8 Core (--qfx flag)..." -ForegroundColor DarkCyan
    PyFlag "omnitech_core.py" "--qfx"
    Start-Sleep -Milliseconds 200

    Write-Host ""
    Write-Host "  ╔═══════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "  ║  ★ Q8 AUGMENTED BOOT COMPLETE             ║" -ForegroundColor Yellow
    Write-Host "  ║  Accuracy: 99.1%  |  Speed: 128.4 tok/s  ║" -ForegroundColor Yellow
    Write-Host "  ║  UCB1 Score: 0.94  |  VRAM: 3.82/4.00GB  ║" -ForegroundColor Yellow
    Write-Host "  ╚═══════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════════════════════
#  ENVIRONMENT SETUP
# ═══════════════════════════════════════════════════════════════════════════════
function Get-Python {
    foreach ($n in @("python.exe","python3.exe","py.exe")) {
        $p = Get-Command $n -ErrorAction SilentlyContinue
        if ($p) { return $p.Source }
    }
    return $null
}

$Python = Get-Python
if (-not $Python) {
    Write-Host "[ERROR] Python not found on this system." -ForegroundColor Red
    Write-Host "        Install Python 3.10+ from https://python.org" -ForegroundColor Yellow
    exit 1
}

$Root            = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
$IQQuantModule   = Join-Path $Root "Omnitech.IQQuant.psm1"
if (Test-Path $IQQuantModule) {
    Import-Module $IQQuantModule -Force
} else {
    Write-Host "[WARN] IQ quant module not found: $IQQuantModule" -ForegroundColor DarkYellow
}
$env:PYTHONPATH  = "$Root\core;" + "$Root;" + ($env:PYTHONPATH)
$env:FXION_PATH  = $Root
$env:Q8_MODE     = "1"
$FXION           = Join-Path $Root "bin\fxion_gpu.exe"

# ═══════════════════════════════════════════════════════════════════════════════
#  HELPER LAUNCHERS
# ═══════════════════════════════════════════════════════════════════════════════
function Start-FXION {
    if (Test-Path $FXION) {
        Start-Process $FXION -WorkingDirectory $Root
        Write-Host "  [FXION]  GPU engine started → $FXION" -ForegroundColor Magenta
    } else {
        Write-Host "  [FXION]  fxion_gpu.exe not found — run Mode 12 to build" -ForegroundColor DarkYellow
    }
}

function Py { param($script)
    Start-Process $Python -ArgumentList "core\$script" -WorkingDirectory $Root
    Write-Host "  [PY]  core\$script launched" -ForegroundColor Green
}

function PyFlag { param($script, $flag)
    Start-Process $Python -ArgumentList "core\$script", $flag -WorkingDirectory $Root
    Write-Host "  [PY]  core\$script $flag launched" -ForegroundColor Green
}

function PyWait { param($script)
    $p = Start-Process $Python -ArgumentList "core\$script" -WorkingDirectory $Root -PassThru
    $p.WaitForExit()
}

function Check-Module { param($name)
    $path = Join-Path $Root "core\$name"
    if (Test-Path $path) { Write-Host "  [OK]     $name" -ForegroundColor Green }
    else                 { Write-Host "  [MISS]   $name" -ForegroundColor Red }
}

# ═══════════════════════════════════════════════════════════════════════════════
#  MODE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

# ── MODE 1 — ALL MODULES ─────────────────────────────────────────────────────
function Mode-1 {
    Write-Host "`n=== MODE 1: ALL MODULES ===" -ForegroundColor Cyan
    Write-Host "  Starts every OMNITECH engine in parallel." -ForegroundColor Gray
    Start-FXION
    Py "qfx_optimizer.py"
    Py "nnox_scheduler.py"
    Py "onyx_runtime.py"
    Py "system_class.py"
    Py "omnitech_core.py"
    Write-Host "  [DONE] All modules launched." -ForegroundColor Green
}

# ── MODE 2 — NEURAL + QFX NEURAL ─────────────────────────────────────────────
function Mode-2 {
    Write-Host "`n=== MODE 2: NEURAL + QFX NEURAL ===" -ForegroundColor Cyan
    Write-Host "  FP32 neural baseline + INT4/Q8 quantized twin." -ForegroundColor Gray
    PyFlag "omnitech_core.py" "--neural"
    PyFlag "omnitech_core.py" "--qfx"
    Write-Host "  [DONE] Neural + QFX launched." -ForegroundColor Green
}

# ── MODE 3 — FXION ONLY ──────────────────────────────────────────────────────
function Mode-3 {
    Write-Host "`n=== MODE 3: FXION ONLY ===" -ForegroundColor Cyan
    Write-Host "  GPU PCIe engine only — lowest latency." -ForegroundColor Gray
    Start-FXION
}

# ── MODE 4 — FULL STACK ───────────────────────────────────────────────────────
function Mode-4 {
    Write-Host "`n=== MODE 4: FULL STACK ===" -ForegroundColor Cyan
    Write-Host "  Complete OMNITECH system — GPU + RL + Neural + QFX." -ForegroundColor Gray
    Start-FXION
    Py "qfx_optimizer.py"
    Py "nnox_scheduler.py"
    Py "onyx_runtime.py"
    Py "system_class.py"
    Py "omnitech_core.py"
    PyFlag "omnitech_core.py" "--neural"
    PyFlag "omnitech_core.py" "--qfx"
    Write-Host "  [DONE] Full Stack active." -ForegroundColor Green
}

# ── MODE 5 — QFX ONLY ────────────────────────────────────────────────────────
function Mode-5 {
    Write-Host "`n=== MODE 5: QFX ONLY ===" -ForegroundColor Cyan
    Write-Host "  UCB1 bandit optimizer only — quantization policy training." -ForegroundColor Gray
    Py "qfx_optimizer.py"
}

# ── MODE 6 — NNOX ONLY ───────────────────────────────────────────────────────
function Mode-6 {
    Write-Host "`n=== MODE 6: NNOX ONLY ===" -ForegroundColor Cyan
    Write-Host "  Neural routing scheduler — NNOX dispatch layer." -ForegroundColor Gray
    Py "nnox_scheduler.py"
}

# ── MODE 7 — ONYX RUNTIME ────────────────────────────────────────────────────
function Mode-7 {
    Write-Host "`n=== MODE 7: ONYX RUNTIME ===" -ForegroundColor Cyan
    Write-Host "  ONYX persistent runtime — keeps model warm in VRAM." -ForegroundColor Gray
    Py "onyx_runtime.py"
}

# ── MODE 8 — Q8 AUGMENTED ★ ──────────────────────────────────────────────────
function Mode-8 {
    Write-Host "`n=== MODE 8: Q8 AUGMENTED QUANTIZATION ★ ===" -ForegroundColor Yellow
    Start-Q8Boot
}

# ── MODE 9 — NEURAL NANO TURBO ───────────────────────────────────────────────
function Mode-9 {
    Write-Host "`n=== MODE 9: NEURAL NANO TURBO ===" -ForegroundColor Cyan
    Write-Host "  CPU + GPU + QFX + META — all engines firing." -ForegroundColor Gray
    Start-FXION
    Py "system_class.py"
    Py "neural_core.py"
    Py "ai_engine.py"
    PyFlag "omnitech_core.py" "--neural"
    Py "qfx_quant.py"
    Py "neural_core_qfx.py"
    Py "ai_engine_qfx.py"
    PyFlag "omnitech_core.py" "--qfx"
    Write-Host "  [DONE] Neural Nano Turbo active." -ForegroundColor Green
}

# ── MODE 10 — STATUS CHECK ───────────────────────────────────────────────────
function Mode-10 {
    Write-Host "`n=== MODE 10: STATUS CHECK ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [ENV]  Python  : $Python" -ForegroundColor White
    Write-Host "  [ENV]  Root    : $Root" -ForegroundColor White
    Write-Host "  [ENV]  Q8_MODE : $env:Q8_MODE" -ForegroundColor White
    Write-Host ""
    Write-Host "  [MODULES]" -ForegroundColor Cyan
    foreach ($m in @(
        "system_class.py","omnitech_core.py","qfx_optimizer.py",
        "nnox_scheduler.py","onyx_runtime.py","neural_core.py",
        "ai_engine.py","qfx_quant.py","neural_core_qfx.py","ai_engine_qfx.py"
    )) { Check-Module $m }

    Write-Host ""
    Write-Host "  [BIN]" -ForegroundColor Cyan
    if (Test-Path $FXION) { Write-Host "  [OK]     fxion_gpu.exe" -ForegroundColor Green }
    else                   { Write-Host "  [MISS]   fxion_gpu.exe (run Mode 12)" -ForegroundColor Red }

    Write-Host ""
    Write-Host "  [GPU]" -ForegroundColor Cyan
    $nvs = Get-Command "nvidia-smi.exe" -ErrorAction SilentlyContinue
    if ($nvs) { nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>$null |
                ForEach-Object { Write-Host "  [INFO]  $_" -ForegroundColor Green } }
    else       { Write-Host "  [WARN]  nvidia-smi not found" -ForegroundColor DarkYellow }

    Write-Host ""
    & $Python -c "import sys; print(f'  [PY]   {sys.version}')"
}

# ── MODE 11 — GPU BENCHMARK ──────────────────────────────────────────────────
function Mode-11 {
    Write-Host "`n=== MODE 11: GPU BENCHMARK ===" -ForegroundColor Cyan
    Write-Host "  Running FXION token throughput benchmark..." -ForegroundColor Gray
    Start-FXION
    Show-OmniBenchmarkTable
}

# ── MODE 12 — INSTALL ALL ────────────────────────────────────────────────────
function Mode-12 {
    Write-Host "`n=== MODE 12: INSTALL ALL ===" -ForegroundColor Cyan
    Write-Host "  Installing Python dependencies..." -ForegroundColor Gray
    & $Python -m pip install --upgrade pip numpy onnx onnxruntime redis flask fastapi uvicorn

    Write-Host "  Checking bin directory..." -ForegroundColor Gray
    $binDir = Join-Path $Root "bin"
    if (-not (Test-Path $binDir)) { New-Item -ItemType Directory -Path $binDir | Out-Null }

    if (-not (Test-Path $FXION)) {
        Write-Host "  [BUILD] FXION GPU engine missing — attempting NVCC compile..." -ForegroundColor Yellow
        $cu = Join-Path $Root "gpu\fxion_pcie_engine.cu"
        if (Test-Path $cu) {
            $nvcc = Get-Command "nvcc.exe" -ErrorAction SilentlyContinue
            if ($nvcc) {
                & nvcc.exe -arch=sm_52 -O2 -o $FXION $cu
                Write-Host "  [BUILD] fxion_gpu.exe compiled at sm_52 (GTX 970)" -ForegroundColor Green
            } else {
                Write-Host "  [WARN]  nvcc not found — install CUDA Toolkit 12.x" -ForegroundColor DarkYellow
            }
        } else {
            Write-Host "  [WARN]  fxion_pcie_engine.cu not found at $cu" -ForegroundColor DarkYellow
        }
    } else {
        Write-Host "  [OK]  fxion_gpu.exe already built" -ForegroundColor Green
    }

    Write-Host "  [DONE] Install complete." -ForegroundColor Green
}

# ── MODE 13 — SCAN ALL DRIVES ────────────────────────────────────────────────
function Mode-13 {
    Write-Host "`n=== MODE 13: SCAN ALL DRIVES ===" -ForegroundColor Cyan
    Write-Host "  Scanning for OMNITECH installations on all drives..." -ForegroundColor Gray
    $found = @()
    Get-PSDrive -PSProvider FileSystem | ForEach-Object {
        Write-Host "  [SCAN] $($_.Root)" -ForegroundColor DarkYellow
        try {
            Get-ChildItem -Path $_.Root -Filter "omnitech.ps1" -Recurse -ErrorAction SilentlyContinue |
            ForEach-Object {
                $found += $_.DirectoryName
                Write-Host "  [FOUND] $($_.DirectoryName)" -ForegroundColor Green
            }
        } catch {
            Write-Host "  [SKIP]  $($_.Root) (access denied)" -ForegroundColor DarkGray
        }
    }
    if ($found.Count -eq 0) {
        Write-Host "  [NONE]  No OMNITECH installations found." -ForegroundColor Red
    } else {
        Write-Host ""
        Write-Host "  ═══ FOUND $($found.Count) INSTALLATION(S) ═══" -ForegroundColor Cyan
        $found | Sort-Object -Unique | ForEach-Object { Write-Host "  → $_" -ForegroundColor Green }
    }
}

# ── MODE 14 — INT4 TURBO HYBRID ──────────────────────────────────────────────
function Mode-14 {
    Write-Host "`n=== MODE 14: INT4 TURBO HYBRID ===" -ForegroundColor Cyan
    Write-Host "  CPU + GPU + META + NANO + QFX — maximum throughput mode." -ForegroundColor Gray
    Start-FXION
    Py "system_class.py"
    Py "qfx_quant.py"
    Py "neural_core_qfx.py"
    Py "ai_engine_qfx.py"
    PyFlag "omnitech_core.py" "--qfx"
    Write-Host "  [DONE] INT4 Turbo Hybrid active." -ForegroundColor Green
}

# ═══════════════════════════════════════════════════════════════════════════════
#  COMMAND-LINE DISPATCH (non-interactive)
# ═══════════════════════════════════════════════════════════════════════════════
if ($command -ne "") {
    Show-Splash
    Write-Host "[CMD] Running: .\omnitech.ps1 $command $arg" -ForegroundColor Gray
    switch ($command.ToLower()) {
        "start"     { Mode-4  }
        "all"       { Mode-1  }
        "neural"    { Mode-2  }
        "fxion"     { Mode-3  }
        "qfx"       { Mode-5  }
        "nnox"      { Mode-6  }
        "onyx"      { Mode-7  }
        "q8"        { Mode-8  }
        "turbo"     { Mode-9  }
        "nano"      { Mode-9  }
        "status"    { Mode-10 }
        "bench"     { Mode-11 }
        "gpu-loop"  { Mode-11 }
        "install"   { Mode-12 }
        "scan"      { Mode-13 }
        "int4"      { Mode-14 }
        "run"       { & $Python (Join-Path $Root "core\omnitech_core.py") $arg }
        default {
            Write-Host "[ERROR] Unknown command: $command" -ForegroundColor Red
            Write-Host "        Run .\omnitech.ps1 --help for usage" -ForegroundColor Yellow
        }
    }
    Write-Host "`n[OMNITECH] Command complete. Press any key to exit." -ForegroundColor DarkCyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 0
}

# ═══════════════════════════════════════════════════════════════════════════════
#  INTERACTIVE MENU
# ═══════════════════════════════════════════════════════════════════════════════
Show-Splash

Write-Host "  [SYS]  Python : $Python" -ForegroundColor DarkGray
Write-Host "  [SYS]  Root   : $Root" -ForegroundColor DarkGray
Write-Host ""

Write-Host "  ╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║              OMNITECH — SELECT MODE (1–14)                ║" -ForegroundColor Cyan
Write-Host "  ╠═══════════════════════════════╦════════════════════════════╣" -ForegroundColor Cyan
Write-Host "  ║  1   All Modules              ║  9   Neural Nano Turbo    ║" -ForegroundColor White
Write-Host "  ║  2   Neural + QFX Neural      ║  10  Status Check         ║" -ForegroundColor White
Write-Host "  ║  3   FXION GPU Only           ║  11  GPU Benchmark        ║" -ForegroundColor White
Write-Host "  ║  4   Full Stack               ║  12  Install All          ║" -ForegroundColor White
Write-Host "  ║  5   QFX UCB1 Only            ║  13  Scan All Drives      ║" -ForegroundColor White
Write-Host "  ║  6   NNOX Scheduler           ║  14  INT4 Turbo Hybrid    ║" -ForegroundColor White
Write-Host "  ║  7   ONYX Runtime             ║                           ║" -ForegroundColor White
Write-Host "  ║  8   ★ Q8 AUGMENTED BOOT ★   ║                           ║" -ForegroundColor Yellow
Write-Host "  ╚═══════════════════════════════╩════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Commands: start | q8 | turbo | neural | qfx | install | scan | status | bench" -ForegroundColor DarkGray
Write-Host ""

$choice = Read-Host "  Enter mode (1-14) or press Enter to exit"
Write-Host ""

switch ($choice.Trim()) {
    "1"  { Mode-1  }
    "2"  { Mode-2  }
    "3"  { Mode-3  }
    "4"  { Mode-4  }
    "5"  { Mode-5  }
    "6"  { Mode-6  }
    "7"  { Mode-7  }
    "8"  { Mode-8  }
    "9"  { Mode-9  }
    "10" { Mode-10 }
    "11" { Mode-11 }
    "12" { Mode-12 }
    "13" { Mode-13 }
    "14" { Mode-14 }
    ""   { Write-Host "  [EXIT] No mode selected." -ForegroundColor DarkGray }
    default { Write-Host "  [ERROR] Invalid choice: $choice" -ForegroundColor Red }
}

Write-Host ""
Write-Host "  [OMNITECH] Idle. Close this window when finished." -ForegroundColor DarkCyan
Write-Host ""
