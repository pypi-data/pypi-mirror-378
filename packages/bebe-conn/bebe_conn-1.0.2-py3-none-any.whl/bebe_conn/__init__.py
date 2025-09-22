"""
BebeConn - Monitorizare Laptop de la Distanță
============================================

O librărie Python simplă pentru monitorizarea laptopului de la distanță,
cu interfață web și actualizări în timp real.

Utilizare:
    import bebe_conn
    bebe_conn.start()  # Pornește totul automat

Sau din linia de comandă:
    bebe-conn start
    bebe-conn start --ngrok  # Cu ngrok pentru acces extern
"""

__version__ = "1.0.0"
__author__ = "Ionel Balauta"
__email__ = "ionel@example.com"

from .core import BebeConn
from .server import BebeServer
from .agent import BebeAgent

def start(ngrok=False, port=5000, screenshot_interval=120):
    """
    Pornește sistemul complet de monitorizare.
    
    Args:
        ngrok (bool): Dacă să folosească ngrok pentru acces extern
        port (int): Portul pentru server (default: 5000)
        screenshot_interval (int): Intervalul pentru screenshot-uri în secunde (default: 120)
    """
    bebe = BebeConn(ngrok=ngrok, port=port, screenshot_interval=screenshot_interval)
    bebe.start()

def start_server(port=5000):
    """Pornește doar serverul."""
    server = BebeServer(port=port)
    server.start()

def start_agent(server_url="http://localhost:5000", screenshot_interval=120):
    """Pornește doar agentul."""
    agent = BebeAgent(server_url=server_url, screenshot_interval=screenshot_interval)
    agent.start()

__all__ = [
    'BebeConn',
    'BebeServer', 
    'BebeAgent',
    'start',
    'start_server',
    'start_agent'
]
