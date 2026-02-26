"""
Moltgotchi - Static Website Server for Vercel
Serves static HTML/CSS/JS with proper path handling
"""

from flask import Flask, send_file, jsonify
import os

# Get the absolute path to the website folder
WEBSITE_DIR = os.path.join(os.path.dirname(__file__), 'website')

app = Flask(__name__)

@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve(path):
    """Serve static files or fallback to index.html for SPA routing"""
    
    # Sanitize path
    path = path.strip('/')
    
    # Try to serve the requested file
    file_path = os.path.join(WEBSITE_DIR, path)
    
    # Security: prevent directory traversal
    if not os.path.abspath(file_path).startswith(os.path.abspath(WEBSITE_DIR)):
        return {'error': 'Not found'}, 404
    
    # If it's a directory or doesn't exist, serve index.html (SPA routing)
    if not os.path.isfile(file_path):
        file_path = os.path.join(WEBSITE_DIR, 'index.html')
    
    try:
        return send_file(file_path)
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'mode': 'offline', 'version': '0.2.0'})

@app.errorhandler(404)
def not_found(e):
    """Serve index.html for 404s (SPA routing)"""
    return send_file(os.path.join(WEBSITE_DIR, 'index.html'))

@app.errorhandler(500)
def server_error(e):
    """Handle server errors"""
    return {'error': 'Internal server error', 'details': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
