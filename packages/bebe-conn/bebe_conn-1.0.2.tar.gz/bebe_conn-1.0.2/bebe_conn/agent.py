"""
Agent de monitorizare pentru BebeConn
"""

import requests
import psutil
import platform
import socket
from datetime import datetime
import time
import json
import base64
import io
from PIL import Image
import pyautogui

class BebeAgent:
    """
    Agent de monitorizare care colectează date despre sistem.
    """
    
    def __init__(self, server_url="http://localhost:5000", screenshot_interval=120):
        self.server_url = server_url
        self.screenshot_interval = screenshot_interval
        self.hostname = socket.gethostname()
        self.platform = platform.system()
        self.running = False
        
        # Configurare screenshot
        pyautogui.FAILSAFE = False
        
    def get_system_info(self):
        """Obține informații despre sistem."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # RAM
            memory = psutil.virtual_memory()
            
            # Disk
            disk = psutil.disk_usage('/')
            
            # Procese
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > 0 or proc_info['memory_percent'] > 1:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sortează după CPU
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            
            return {
                'basic_info': {
                    'hostname': self.hostname,
                    'platform': self.platform,
                    'platform_version': platform.platform(),
                    'architecture': platform.architecture()[0],
                    'timestamp': datetime.now().isoformat()
                },
                'system_stats': {
                    'cpu': {
                        'percent': cpu_percent,
                        'count': cpu_count
                    },
                    'memory': {
                        'total': memory.total,
                        'available': memory.available,
                        'percent': memory.percent,
                        'used': memory.used,
                        'free': memory.free
                    },
                    'disk': {
                        'total': disk.total,
                        'used': disk.used,
                        'free': disk.free,
                        'percent': (disk.used / disk.total) * 100
                    }
                },
                'running_processes': processes[:15]  # Top 15 procese
            }
        except Exception as e:
            print(f"❌ Eroare la obținerea informațiilor: {e}")
            return {}
    
    def take_screenshot(self):
        """Face un screenshot al ecranului."""
        try:
            # Capturează screenshot
            screenshot = pyautogui.screenshot()
            
            # Redimensionează pentru a reduce mărimea
            screenshot = screenshot.resize((1280, 720), Image.Resampling.LANCZOS)
            
            # Convertește în bytes
            img_buffer = io.BytesIO()
            screenshot.save(img_buffer, format='PNG', optimize=True, quality=85)
            img_buffer.seek(0)
            
            # Encodează în base64
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            
            return img_base64
        except Exception as e:
            print(f"❌ Eroare la capturarea screenshot-ului: {e}")
            return None
    
    def send_heartbeat(self):
        """Trimite heartbeat la server."""
        try:
            system_data = self.get_system_info()
            
            response = requests.post(
                f"{self.server_url}/api/agent/heartbeat",
                json=system_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Heartbeat trimis la {datetime.now().strftime('%H:%M:%S')}")
                return True
            else:
                print(f"❌ Eroare heartbeat: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Eroare la trimiterea heartbeat: {e}")
            return False
    
    def send_screenshot(self):
        """Trimite screenshot la server."""
        try:
            screenshot_data = self.take_screenshot()
            if screenshot_data:
                response = requests.post(
                    f"{self.server_url}/api/agent/screenshot",
                    json={'screenshot': screenshot_data},
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"📸 Screenshot trimis la {datetime.now().strftime('%H:%M:%S')}")
                    return True
                else:
                    print(f"❌ Eroare screenshot: {response.status_code}")
                    return False
            else:
                print("❌ Nu s-a putut captura screenshot-ul")
                return False
                
        except Exception as e:
            print(f"❌ Eroare la trimiterea screenshot: {e}")
            return False
    
    def start(self):
        """Pornește monitorizarea."""
        print("🤖 BebeConn Agent pornit!")
        print(f"🌐 Server: {self.server_url}")
        print(f"📸 Screenshot la fiecare {self.screenshot_interval} secunde")
        print("⏹️  Apasă Ctrl+C pentru a opri")
        print("-" * 50)
        
        self.running = True
        screenshot_counter = 0
        
        try:
            while self.running:
                self.send_heartbeat()
                
                # Trimite screenshot la intervalul specificat
                screenshot_counter += 1
                if screenshot_counter >= (self.screenshot_interval // 30):  # La fiecare 30s
                    self.send_screenshot()
                    screenshot_counter = 0
                
                time.sleep(30)  # Trimite la fiecare 30 secunde
                
        except KeyboardInterrupt:
            print("\n⏹️  Agent oprit de utilizator")
        except Exception as e:
            print(f"❌ Eroare în agent: {e}")
        finally:
            self.running = False
            print("✅ Agent oprit")
    
    def stop(self):
        """Oprește agentul."""
        self.running = False
