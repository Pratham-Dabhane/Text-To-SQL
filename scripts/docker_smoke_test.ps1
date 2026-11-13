param(
    [string]$ApiUrl = "http://localhost:8000"
)

$headers = @{}
if ($env:API_KEY) {
    $headers["X-API-Key"] = $env:API_KEY
}

Write-Host "Checking API health..."
$health = Invoke-RestMethod "$ApiUrl/health"
if ($health.status -ne "ok") {
    throw "API health check did not return status=ok."
}

Write-Host "Checking protected history endpoint..."
$history = Invoke-RestMethod "$ApiUrl/v1/history" -Headers $headers
if ($null -eq $history.items) {
    throw "History response did not contain items."
}

Write-Host "Docker smoke test passed."
