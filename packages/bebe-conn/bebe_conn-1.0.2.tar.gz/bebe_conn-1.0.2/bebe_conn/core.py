"""
Clasa principală BebeConn - coordonează serverul și agentul
"""

import threading
import time
import subprocess
import sys
import os
from .server import BebeServer
from .agent import BebeAgent

class BebeConn:
    """
    Clasa principală care coordonează serverul și agentul.
    """
    
    def __init__(self, ngrok=False, port=5000, screenshot_interval=120):
        self.ngrok = ngrok
        self.port = port
        self.screenshot_interval = screenshot_interval
        self.server = None
        self.agent = None
        self.ngrok_process = None
        self.server_thread = None
        self.agent_thread = None
        
    def start(self):
        """Pornește sistemul complet."""
        print("🚀 BebeConn - Monitorizare Laptop de la Distanță")
        print("=" * 50)
        
        try:
            # Pornește serverul
            print("📡 Pornesc serverul...")
            self.server = BebeServer(port=self.port)
            self.server_thread = threading.Thread(target=self.server.start, daemon=True)
            self.server_thread.start()
            
            # Așteaptă ca serverul să pornească
            time.sleep(3)
            
            # Pornește ngrok dacă este necesar
            if self.ngrok:
                print("🌐 Pornesc ngrok...")
                self._start_ngrok()
                time.sleep(5)  # Așteaptă ca ngrok să pornească
                
                # Obține URL-ul ngrok
                ngrok_url = self._get_ngrok_url()
                if ngrok_url:
                    print(f"🔗 URL ngrok: {ngrok_url}")
                    server_url = ngrok_url
                else:
                    print("⚠️  Nu s-a putut obține URL-ul ngrok, folosesc localhost")
                    server_url = f"http://localhost:{self.port}"
            else:
                server_url = f"http://localhost:{self.port}"
                print(f"🔗 URL local: {server_url}")
            
            # Pornește agentul
            print("🤖 Pornesc agentul...")
            self.agent = BebeAgent(server_url=server_url, screenshot_interval=self.screenshot_interval)
            self.agent_thread = threading.Thread(target=self.agent.start, daemon=True)
            self.agent_thread.start()
            
            print("\n✅ Sistem pornit cu succes!")
            print(f"📱 Accesează dashboard-ul: {server_url}")
            print("⏹️  Apasă Ctrl+C pentru a opri")
            print("-" * 50)
            
            # Menține aplicația activă
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n⏹️  Oprire sistem...")
                self.stop()
                
        except Exception as e:
            print(f"❌ Eroare la pornirea sistemului: {e}")
            self.stop()
    
    def _start_ngrok(self):
        """Pornește ngrok."""
        try:
            # Verifică dacă ngrok este instalat
            result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ ngrok nu este instalat. Instalează-l de la https://ngrok.com/download")
                return False
                
            # Pornește ngrok
            self.ngrok_process = subprocess.Popen(
                ['ngrok', 'http', str(self.port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return True
            
        except FileNotFoundError:
            print("❌ ngrok nu este instalat. Instalează-l de la https://ngrok.com/download")
            return False
        except Exception as e:
            print(f"❌ Eroare la pornirea ngrok: {e}")
            return False
    
    def _get_ngrok_url(self):
        """Obține URL-ul ngrok."""
        try:
            import requests
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get('tunnels', [])
                for tunnel in tunnels:
                    if tunnel.get('proto') == 'https':
                        return tunnel.get('public_url')
            return None
        except Exception as e:
            print(f"⚠️  Nu s-a putut obține URL-ul ngrok: {e}")
            return None
    
    def stop(self):
        """Oprește sistemul."""
        print("⏹️  Oprire sistem...")
        
        if self.ngrok_process:
            self.ngrok_process.terminate()
            print("✅ ngrok oprit")
            
        if self.agent:
            self.agent.stop()
            print("✅ Agent oprit")
            
        if self.server:
            self.server.stop()
            print("✅ Server oprit")
            
        print("✅ Sistem oprit complet")
