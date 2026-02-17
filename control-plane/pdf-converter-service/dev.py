"""
Local development server with auto-reload
Run this for local testing and development
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Set development environment variables
os.environ.setdefault('PORT', '8080')
os.environ.setdefault('GCS_BUCKET', 'tensrgrid-raw-data')
os.environ.setdefault('OUTPUT_FOLDER', 'tensrgrid/markdown-output')

# Check for credentials
if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
    print("WARNING: GOOGLE_APPLICATION_CREDENTIALS not set")
    print("Set it to your service account key file:")
    print("  export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json")
    print()

if not os.environ.get('GCP_PROJECT_ID'):
    print("WARNING: GCP_PROJECT_ID not set")
    print("Set it to your GCP project ID:")
    print("  export GCP_PROJECT_ID=your-project-id")
    print()

# Import and run the app
from main import app

if __name__ == '__main__':
    print("=" * 60)
    print("PDF Converter Service - Development Server")
    print("=" * 60)
    print(f"Port: {os.environ.get('PORT', '8080')}")
    print(f"Bucket: {os.environ.get('GCS_BUCKET', 'tensrgrid-raw-data')}")
    print(f"Output: {os.environ.get('OUTPUT_FOLDER', 'tensrgrid/markdown-output')}")
    print("=" * 60)
    print()
    print("Health check: http://localhost:8080/health")
    print("Service endpoint: http://localhost:8080/")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8080)),
        debug=True,
        use_reloader=True
    )
