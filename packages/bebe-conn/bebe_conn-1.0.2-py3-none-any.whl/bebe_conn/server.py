"""
Server Flask pentru BebeConn
"""

from flask import Flask, jsonify, request, send_file
import json
import os
import base64
import io
from datetime import datetime
import threading
import time

class BebeServer:
    """
    Server Flask pentru monitorizarea laptopului.
    """
    
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.server = None
        self.running = False
        
        # Stocare date
        self.data_store = {
            'agent_status': {
                'connected': False,
                'last_seen': None,
                'laptop_info': {}
            },
            'screenshots': [],
            'logs': [],
            'latest_screenshot': None
        }
        
        # Creează directorul pentru screenshot-uri
        self.screenshots_dir = os.path.join(os.path.dirname(__file__), "..", "..", "screenshots")
        self.screenshots_dir = os.path.abspath(self.screenshots_dir)
        os.makedirs(self.screenshots_dir, exist_ok=True)
        print(f"📁 Director screenshots: {self.screenshots_dir}")
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Configurează rutele Flask."""
        
        @self.app.route('/')
        def dashboard():
            return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>BebeConn - Monitor Laptop</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
                    .card { background: white; padding: 20px; margin: 10px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .status { font-size: 24px; font-weight: bold; }
                    .online { color: green; }
                    .offline { color: red; }
                    .process { background: #f9f9f9; padding: 10px; margin: 5px 0; border-left: 4px solid #007bff; }
                    .screenshot { max-width: 100%; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
                </style>
            </head>
            <body>
                <h1>🖥️ BebeConn - Monitor Laptop</h1>
                
                <div class="card">
                    <h2>Status: <span id="status" class="status">Se încarcă...</span></h2>
                    <p>Ultima actualizare: <span id="last-seen">-</span></p>
                </div>
                
                <div class="card">
                    <h3>📸 Screenshot Recent</h3>
                    <img id="screenshot" class="screenshot" src="" alt="Niciun screenshot" style="display: none;">
                    <p id="no-screenshot">Niciun screenshot disponibil</p>
                </div>
                
                <div class="card">
                    <h3>🔧 Procese Active</h3>
                    <div id="processes">Se încarcă...</div>
                </div>
                
                <div class="card">
                    <h3>📊 Statistici Sistem</h3>
                    <div id="stats">Se încarcă...</div>
                </div>

                <script>
                    async function loadData() {
                        try {
                            const response = await fetch('/api/status');
                            const data = await response.json();
                            
                            // Update status
                            const statusEl = document.getElementById('status');
                            const lastSeenEl = document.getElementById('last-seen');
                            
                            if (data.agent_status.connected) {
                                statusEl.textContent = 'ONLINE';
                                statusEl.className = 'status online';
                                if (data.agent_status.last_seen) {
                                    lastSeenEl.textContent = new Date(data.agent_status.last_seen).toLocaleString('ro-RO');
                                }
                            } else {
                                statusEl.textContent = 'OFFLINE';
                                statusEl.className = 'status offline';
                                lastSeenEl.textContent = 'Agentul nu este conectat';
                            }
                            
                            // Update processes
                            if (data.agent_status.laptop_info.running_processes) {
                                const processes = data.agent_status.laptop_info.running_processes;
                                const processesHTML = processes.map(proc => 
                                    `<div class="process">
                                        <strong>${proc.name || 'Unknown'}</strong> 
                                        (PID: ${proc.pid || 'N/A'})<br>
                                        CPU: ${proc.cpu_percent ? proc.cpu_percent.toFixed(1) : '0.0'}% | 
                                        RAM: ${proc.memory_percent ? proc.memory_percent.toFixed(1) : '0.0'}%
                                    </div>`
                                ).join('');
                                document.getElementById('processes').innerHTML = processesHTML;
                            }
                            
                            // Update stats
                            if (data.agent_status.laptop_info.system_stats) {
                                const stats = data.agent_status.laptop_info.system_stats;
                                const statsHTML = `
                                    <p><strong>CPU:</strong> ${stats.cpu ? stats.cpu.percent.toFixed(1) : '0'}%</p>
                                    <p><strong>RAM:</strong> ${stats.memory ? stats.memory.percent.toFixed(1) : '0'}%</p>
                                    <p><strong>Disk:</strong> ${stats.disk ? stats.disk.percent.toFixed(1) : '0'}%</p>
                                `;
                                document.getElementById('stats').innerHTML = statsHTML;
                            }
                            
                            // Update screenshot
                            if (data.latest_screenshot) {
                                document.getElementById('screenshot').src = '/api/screenshot/' + data.latest_screenshot;
                                document.getElementById('screenshot').style.display = 'block';
                                document.getElementById('no-screenshot').style.display = 'none';
                            }
                            
                        } catch (error) {
                            console.error('Eroare:', error);
                        }
                    }
                    
                    // Load data every 3 seconds
                    loadData();
                    setInterval(loadData, 3000);
                </script>
            </body>
            </html>
            '''
        
        @self.app.route('/api/status')
        def get_status():
            try:
                # Adaugă latest_screenshot la nivelul rădăcină pentru dashboard
                status_data = self.data_store.copy()
                if 'latest_screenshot' not in status_data:
                    status_data['latest_screenshot'] = None
                return jsonify(status_data)
            except Exception as e:
                print(f"❌ Eroare în /api/status: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/agent/heartbeat', methods=['POST'])
        def agent_heartbeat():
            try:
                data = request.get_json()
                self.data_store['agent_status']['connected'] = True
                self.data_store['agent_status']['last_seen'] = datetime.now().isoformat()
                self.data_store['agent_status']['laptop_info'] = data
                self.data_store['logs'].append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'heartbeat',
                    'data': data
                })
                return jsonify({'status': 'ok'})
            except Exception as e:
                print(f"❌ Eroare în heartbeat: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/agent/screenshot', methods=['POST'])
        def receive_screenshot():
            try:
                data = request.get_json()
                
                if 'screenshot' in data:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"screenshot_{timestamp}.png"
                    
                    # Salvează screenshot-ul real
                    screenshot_data = base64.b64decode(data['screenshot'])
                    filepath = os.path.join(self.screenshots_dir, filename)
                    print(f"💾 Salvez screenshot în: {filepath}")
                    with open(filepath, 'wb') as f:
                        f.write(screenshot_data)
                    print(f"✅ Screenshot salvat: {filename}")
                    
                    self.data_store['screenshots'].append(filename)
                    self.data_store['latest_screenshot'] = filename
                    
                    # Păstrează doar ultimele 10 screenshot-uri
                    if len(self.data_store['screenshots']) > 10:
                        old_screenshot = self.data_store['screenshots'].pop(0)
                        old_filepath = os.path.join(self.screenshots_dir, old_screenshot)
                        if os.path.exists(old_filepath):
                            os.remove(old_filepath)
                    
                    return jsonify({'status': 'saved', 'filename': filename})
                else:
                    return jsonify({'status': 'error', 'message': 'No screenshot data'})
                    
            except Exception as e:
                print(f"❌ Eroare în receive_screenshot: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/screenshot/<filename>')
        def get_screenshot(filename):
            try:
                filepath = os.path.join(self.screenshots_dir, filename)
                print(f"🔍 Caut screenshot în: {filepath}")
                
                if os.path.exists(filepath):
                    print(f"✅ Găsit screenshot: {filename}")
                    return send_file(filepath, mimetype='image/png')
                else:
                    print(f"❌ Screenshot nu există: {filepath}")
                    return "Screenshot nu a fost găsit", 404
                    
            except Exception as e:
                print(f"❌ Eroare la get_screenshot: {e}")
                return "Eroare la încărcarea screenshot-ului", 500
    
    def start(self):
        """Pornește serverul."""
        try:
            print(f"Server pornit pe {self.host}:{self.port}")
            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
        except Exception as e:
            print(f"Eroare la pornirea serverului: {e}")
    
    def stop(self):
        """Oprește serverul."""
        self.running = False
        if self.server:
            self.server.shutdown()
