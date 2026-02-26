"""
Moltgotchi - Static Website Server
Minimal Flask app to serve static website on Vercel
"""

from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='website', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('website', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Try to serve the file, fallback to index.html for SPA routing
    if os.path.exists(os.path.join('website', path)):
        return send_from_directory('website', path)
    return send_from_directory('website', 'index.html')

@app.route('/api/health')
def health():
    return {'status': 'ok', 'mode': 'offline'}, 200

if __name__ == '__main__':
    app.run(debug=False, port=5000)
