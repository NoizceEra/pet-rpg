from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json
import os

app = FastAPI(title="Claw Sniper Dashboard")

WORKSPACE_ROOT = Path(r"C:\Users\vclin_jjufoql\.openclaw\workspace")
SCANNED_LOG = WORKSPACE_ROOT / "scanned_pools.jsonl"
TRADES_LOG = WORKSPACE_ROOT / "trades.jsonl"

@app.get("/api/scanned")
async def get_scanned():
    if not SCANNED_LOG.exists():
        return []
    
    data = []
    with open(SCANNED_LOG, "r") as f:
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line))
                except:
                    continue
    return data[::-1]  # Return newest first

@app.get("/api/trades")
async def get_trades():
    if not TRADES_LOG.exists():
        return []
    
    data = []
    with open(TRADES_LOG, "r") as f:
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line))
                except:
                    continue
    return data[::-1]

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claw Sniper Dashboard 🦀</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card { background-color: #1e1e1e; border: 1px solid #333; margin-bottom: 20px; }
        .table { color: #e0e0e0; }
        .badge-bought { background-color: #2e7d32; }
        .badge-skipped { background-color: #424242; }
        .status-bought { color: #4caf50; font-weight: bold; }
        .status-skipped { color: #9e9e9e; }
        .status-failed { color: #f44336; }
        h1 { color: #ff9800; }
    </style>
</head>
<body class="container py-4">
    <header class="d-flex justify-content-between align-items-center mb-4">
        <h1>Claw Sniper Dashboard 🦀</h1>
        <div>
            <span id="status-badge" class="badge bg-success">Live</span>
        </div>
    </header>

    <div class="row">
        <div class="col-md-12">
            <div class="card p-3">
                <h3>Recent Scanned Pools</h3>
                <div class="table-responsive">
                    <table class="table table-dark table-hover">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Mint</th>
                                <th>Liquidity</th>
                                <th>Holders</th>
                                <th>Risk Score</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="scanned-body">
                            <!-- Data injected here -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function fetchData() {
            try {
                const response = await fetch('/api/scanned');
                const data = await response.json();
                const body = document.getElementById('scanned-body');
                body.innerHTML = '';
                
                data.slice(0, 50).forEach(item => {
                    const row = document.createElement('tr');
                    const time = new Date(item.timestamp).toLocaleTimeString();
                    const mintShort = item.mint.substring(0, 8) + '...';
                    const riskClass = item.total_risk > 60 ? 'text-danger' : 'text-success';
                    
                    row.innerHTML = `
                        <td>${time}</td>
                        <td title="${item.mint}">${mintShort}</td>
                        <td>$${Math.round(item.liquidity).toLocaleString()}</td>
                        <td>${item.holders}</td>
                        <td class="${riskClass}">${item.total_risk}/100</td>
                        <td class="status-${item.status}">${item.status}</td>
                    `;
                    body.appendChild(row);
                });
            } catch (err) {
                console.error('Fetch error:', err);
                document.getElementById('status-badge').className = 'badge bg-danger';
                document.getElementById('status-badge').innerText = 'Offline';
            }
        }

        // Poll every 5 seconds
        fetchData();
        setInterval(fetchData, 5000);
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8888))
    uvicorn.run(app, host="0.0.0.0", port=port)
