param(
    [string]$Token = "rnd_FgqEM0qGrlZ0wA7EVBLI2cM1uy4n",
    [string]$RepoUrl = "https://github.com/NoizceEra/pet-rpg.git",
    [string]$VercelUrl = "https://pet-rpg-coral.vercel.app"
)

# Render API deployment
$headers = @{
    "Authorization" = "Bearer $Token"
    "Content-Type" = "application/json"
}

$body = @{
    "type" = "web_service"
    "name" = "moltgotchi-api"
    "repo" = $RepoUrl
    "branch" = "main"
    "buildCommand" = "pip install -r requirements.txt"
    "startCommand" = "python api/app.py"
    "envVars" = @(
        @{"key" = "FLASK_ENV"; "value" = "production"},
        @{"key" = "PORT"; "value" = "5000"},
        @{"key" = "CORS_ORIGINS"; "value" = $VercelUrl}
    )
} | ConvertTo-Json

Write-Host "🚀 Deploying to Render..."
Write-Host "Token: $Token"
Write-Host "Repo: $RepoUrl"

try {
    $response = Invoke-WebRequest -Uri "https://api.render.com/v1/services" `
        -Method POST `
        -Headers $headers `
        -Body $body `
        -ContentType "application/json" `
        -ErrorAction Stop
    
    Write-Host "✅ Render deployment initiated!"
    Write-Host $response.Content
} catch {
    Write-Host "⚠️ Render API response:"
    Write-Host $_.Exception.Response.StatusCode
    Write-Host $_.Exception.Message
}
