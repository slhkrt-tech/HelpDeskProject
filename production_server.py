"""
Waitress WSGI Configuration for Alpha Production (Windows)
HelpDesk Alpha Release - Windows Production Server Setup
"""

import os
from waitress import serve
from helpdesk.wsgi import application

def run_production_server():
    """
    Alpha Production Server - Windows optimized
    Using Waitress instead of Gunicorn for Windows compatibility
    """
    
    print("🚀 HelpDesk Alpha Production Server (Windows)")
    print("=" * 50)
    print("📍 Server: http://localhost:8000")
    print("👤 Admin: admin / alpha123!")
    print("🛑 Stop: Ctrl+C")
    print("=" * 50)
    
    # Waitress production server
    serve(
        application,
        host='0.0.0.0',
        port=8000,
        threads=6,  # Multi-threading for better performance
        channel_timeout=120,
        cleanup_interval=30,
        connection_limit=1000,
        send_bytes=18000,
        expose_tracebacks=False,  # Security: hide tracebacks
        ident='HelpDesk-Alpha-v1.0.0'  # Server identification
    )

if __name__ == '__main__':
    run_production_server()