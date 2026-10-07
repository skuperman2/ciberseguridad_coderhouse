<#
 Simulador INOFENSIVO de beaconing (laboratorio Semana 4).
 Hace un pedido HTTP a un servidor del laboratorio cada N segundos.
 No modifica el sistema, no descarga ni ejecuta nada.

 Uso:
   Set-ExecutionPolicy -Scope Process Bypass
   .\beacon.ps1 -Servidor 192.168.56.10 -Intervalo 5 -Repeticiones 12
   .\beacon.ps1 -Servidor 192.168.56.10 -Intervalo 5 -Jitter 3   # con variación aleatoria
#>
param(
    [Parameter(Mandatory = $true)][string]$Servidor,
    [int]$Puerto = 8080,
    [int]$Intervalo = 5,
    [int]$Repeticiones = 12,
    [int]$Jitter = 0
)

# Seguridad: solo direcciones privadas del laboratorio
if ($Servidor -notmatch '^(192\.168\.|10\.|172\.(1[6-9]|2\d|3[01])\.)') {
    Write-Error "Por seguridad, este script solo funciona contra IPs privadas del laboratorio."
    exit 1
}

$id = $env:COMPUTERNAME
for ($i = 1; $i -le $Repeticiones; $i++) {
    $url = "http://${Servidor}:${Puerto}/beacon?id=$id&n=$i"
    try {
        Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 3 | Out-Null
        Write-Host ("[{0}] beacon {1}/{2} -> {3}" -f (Get-Date -Format HH:mm:ss), $i, $Repeticiones, $Servidor)
    } catch {
        # El servidor responde 404 (no hay archivo): igual se generó el tráfico
        Write-Host ("[{0}] beacon {1}/{2} enviado" -f (Get-Date -Format HH:mm:ss), $i, $Repeticiones)
    }
    $espera = $Intervalo
    if ($Jitter -gt 0) { $espera += Get-Random -Minimum (-$Jitter) -Maximum ($Jitter + 1) }
    if ($espera -lt 1) { $espera = 1 }
    if ($i -lt $Repeticiones) { Start-Sleep -Seconds $espera }
}
Write-Host "Listo."
