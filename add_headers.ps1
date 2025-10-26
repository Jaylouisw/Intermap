# Add copyright headers to source files
# Copyright (c) 2025 Jay Wenden

$header = @"
"""
Intermap - Distributed P2P Internet Topology Mapper
Copyright (c) 2025 Jay Wenden
Licensed under CC-BY-NC-SA 4.0
"""

"@

$pythonFiles = Get-ChildItem -Path "src", "tests" -Filter "*.py" -Recurse -File

foreach ($file in $pythonFiles) {
    $content = Get-Content $file.FullName -Raw
    
    # Skip if already has copyright
    if ($content -match "Copyright.*Jay Wenden") {
        Write-Host "Skipping $($file.Name) - already has header" -ForegroundColor Yellow
        continue
    }
    
    # Add header
    $newContent = $header + $content
    Set-Content -Path $file.FullName -Value $newContent -NoNewline
    Write-Host "Added header to $($file.Name)" -ForegroundColor Green
}

Write-Host "`nDone!" -ForegroundColor Cyan
