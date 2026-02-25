$body = @{
    model = "claude-sonnet-4-20250514"
    max_tokens = 10
    messages = @(
        @{
            role = "user"
            content = "ping"
        }
    )
} | ConvertTo-Json -Depth 3

$headers = @{
    "x-api-key" = "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"
    "anthropic-version" = "2023-06-01"
    "content-type" = "application/json"
}

try {
    $response = Invoke-WebRequest -Uri "https://api.anthropic.com/v1/messages" -Method POST -Headers $headers -Body $body -UseBasicParsing
    Write-Output "STATUS: $($response.StatusCode)"
    Write-Output "BODY: $($response.Content)"
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $responseBody = $reader.ReadToEnd()
    Write-Output "STATUS: $statusCode"
    Write-Output "BODY: $responseBody"
}
