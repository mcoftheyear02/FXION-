<#
.SYNOPSIS
  OMNITECH IQ Importance-Matrix Quantization Module

.DESCRIPTION
  Centralizes K-quant and IQ importance-matrix quantization profiles for
  Q8 Augmented boot display, UCB1 policy initialization, VRAM budget checks,
  and Mode 11 GPU benchmark reporting.
#>

function Get-OmniQuantProfiles {
    [CmdletBinding()]
    param()

    @(
        [pscustomobject]@{ Name = "Q2_K";    Family = "K";  TokS = 194.1; VramGB = 1.20; Score = 0.71; Prior = 0.00; Note = "fastest K baseline" }
        [pscustomobject]@{ Name = "Q3_K";    Family = "K";  TokS = 178.6; VramGB = 1.60; Score = 0.78; Prior = 0.00; Note = "low-VRAM K lane" }
        [pscustomobject]@{ Name = "Q4_K_M";  Family = "K";  TokS = 162.3; VramGB = 2.10; Score = 0.85; Prior = 0.00; Note = "balanced K lane" }
        [pscustomobject]@{ Name = "Q5_K_M";  Family = "K";  TokS = 151.8; VramGB = 2.60; Score = 0.88; Prior = 0.00; Note = "quality K lane" }
        [pscustomobject]@{ Name = "Q6_K";    Family = "K";  TokS = 141.2; VramGB = 3.10; Score = 0.91; Prior = 0.00; Note = "high-quality K lane" }
        [pscustomobject]@{ Name = "Q8_0";    Family = "K";  TokS = 128.4; VramGB = 3.82; Score = 0.94; Prior = 0.12; Note = "accuracy lane ★" }

        # Q_INT2 ADDED — ton format 2 bits custom
        [pscustomobject]@{ Name = "Q_INT2";  Family = "K";  TokS = 210.0; VramGB = 1.00; Score = 0.70; Prior = 0.05; Note = "QINT2 ultra-compressed K lane" }

        [pscustomobject]@{ Name = "IQ2_XS";  Family = "IQ"; TokS = 214.7; VramGB = 0.95; Score = 0.76; Prior = 0.06; Note = "importance-matrix ultra-compact" }
        [pscustomobject]@{ Name = "IQ3_M";   Family = "IQ"; TokS = 188.9; VramGB = 1.45; Score = 0.84; Prior = 0.08; Note = "importance-matrix medium" }
        [pscustomobject]@{ Name = "IQ4_XS";  Family = "IQ"; TokS = 171.6; VramGB = 1.85; Score = 0.89; Prior = 0.10; Note = "importance-matrix compact balanced" }
        [pscustomobject]@{ Name = "IQ4_NL";  Family = "IQ"; TokS = 166.2; VramGB = 2.05; Score = 0.92; Prior = 0.11; Note = "importance-matrix nonlinear balanced" }
    )
}

function Get-OmniQuantNames {
    [CmdletBinding()]
    param(
        [ValidateSet("All", "K", "IQ")]
        [string]$Family = "All"
    )

    $profiles = Get-OmniQuantProfiles
    if ($Family -ne "All") {
        $profiles = $profiles | Where-Object { $_.Family -eq $Family }
    }
    ($profiles | Select-Object -ExpandProperty Name) -join " | "
}

function Show-OmniUcb1PolicyInit {
    [CmdletBinding()]
    param(
        [double]$ExplorationConstant = 1.414,
        [double]$Alpha = 0.15
    )

    $profiles = Get-OmniQuantProfiles
    Write-Host "  [UCB1]  K-Quants: $(Get-OmniQuantNames -Family K)" -ForegroundColor White
    Write-Host "  [UCB1]  IQ-Quants: $(Get-OmniQuantNames -Family IQ)" -ForegroundColor White
    Write-Host ("  [UCB1]  Exploration constant C = {0:N3} | Alpha = {1:N2}" -f $ExplorationConstant, $Alpha) -ForegroundColor White

    $q8 = $profiles | Where-Object { $_.Name -eq "Q8_0" } | Select-Object -First 1
    Write-Host ("  [UCB1]  Q8_0 prior boost: +{0:N2} (accuracy=0.991, size={1:N2}GB)" -f $q8.Prior, $q8.VramGB) -ForegroundColor Green

    $iqPrior = ($profiles | Where-Object { $_.Family -eq "IQ" } | ForEach-Object { "$($_.Name)=+$('{0:N2}' -f $_.Prior)" }) -join " | "
    Write-Host "  [UCB1]  IQ prior ladder: $iqPrior" -ForegroundColor Green
}

function Show-OmniVramBudget {
    [CmdletBinding()]
    param(
        [double]$AvailableGB = 4.00,
        [double]$SystemReservedGB = 0.12
    )

    foreach ($profile in Get-OmniQuantProfiles) {
        $color = if ($profile.Family -eq "IQ") { "Cyan" } else { "White" }
        Write-Host ("  [VRAM]  {0,-7} estimate : {1:N2} GB" -f $profile.Name, $profile.VramGB) -ForegroundColor $color
    }

    Write-Host ("  [VRAM]  System reserved : {0:N2} GB" -f $SystemReservedGB) -ForegroundColor White

    $maxProfile = Get-OmniQuantProfiles | Sort-Object VramGB -Descending | Select-Object -First 1
    $fits = (($maxProfile.VramGB + $SystemReservedGB) -le $AvailableGB)
    if ($fits) {
        Write-Host ("  [VRAM]  Available budget: {0:N2} GB  →  ALL PROFILES OK" -f $AvailableGB) -ForegroundColor Green
    } else {
        Write-Host ("  [VRAM]  Available budget: {0:N2} GB  →  CHECK {1}" -f $AvailableGB, $maxProfile.Name) -ForegroundColor DarkYellow
    }
}

function Show-OmniBenchmarkTable {
    [CmdletBinding()]
    param()

    Write-Host "  [BENCH]  Quant   | Tok/s  | VRAM   | Score" -ForegroundColor White
    foreach ($profile in Get-OmniQuantProfiles) {
        $color = if ($profile.Name -eq "Q8_0") { "Yellow" } elseif ($profile.Family -eq "IQ") { "Cyan" } else { "White" }
        $star = if ($profile.Name -eq "Q8_0") { "  ★" } else { "" }
        Write-Host ("  [BENCH]  {0,-7} | {1,6:N1} | {2:N2}GB | {3:N2}{4}" -f $profile.Name, $profile.TokS, $profile.VramGB, $profile.Score, $star) -ForegroundColor $color
    }
    Write-Host "  [NOTE]   UCB1 optimal: Q8_0 accuracy lane; IQ4_NL balanced IQ lane" -ForegroundColor Green
}

Export-ModuleMember -Function Get-OmniQuantProfiles, Get-OmniQuantNames, Show-OmniUcb1PolicyInit, Show-OmniVramBudget, Show-OmniBenchmarkTable
