"""
Teste de bază pentru BebeConn
"""

import unittest
import sys
import os

# Adaugă directorul părinte la path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bebe_conn import BebeConn, BebeServer, BebeAgent

class TestBebeConn(unittest.TestCase):
    """Teste pentru clasa principală BebeConn."""
    
    def test_bebe_conn_init(self):
        """Testează inițializarea BebeConn."""
        bebe = BebeConn(ngrok=False, port=5000, screenshot_interval=120)
        self.assertIsNotNone(bebe)
        self.assertEqual(bebe.port, 5000)
        self.assertEqual(bebe.screenshot_interval, 120)
        self.assertFalse(bebe.ngrok)
    
    def test_bebe_conn_with_ngrok(self):
        """Testează inițializarea BebeConn cu ngrok."""
        bebe = BebeConn(ngrok=True, port=8080, screenshot_interval=60)
        self.assertTrue(bebe.ngrok)
        self.assertEqual(bebe.port, 8080)
        self.assertEqual(bebe.screenshot_interval, 60)

class TestBebeServer(unittest.TestCase):
    """Teste pentru BebeServer."""
    
    def test_server_init(self):
        """Testează inițializarea serverului."""
        server = BebeServer(port=5000)
        self.assertIsNotNone(server)
        self.assertEqual(server.port, 5000)
        self.assertIsNotNone(server.app)
    
    def test_data_store_init(self):
        """Testează inițializarea data_store."""
        server = BebeServer(port=5000)
        self.assertIn('agent_status', server.data_store)
        self.assertIn('screenshots', server.data_store)
        self.assertIn('logs', server.data_store)
        self.assertFalse(server.data_store['agent_status']['connected'])

class TestBebeAgent(unittest.TestCase):
    """Teste pentru BebeAgent."""
    
    def test_agent_init(self):
        """Testează inițializarea agentului."""
        agent = BebeAgent(server_url="http://localhost:5000", screenshot_interval=120)
        self.assertIsNotNone(agent)
        self.assertEqual(agent.server_url, "http://localhost:5000")
        self.assertEqual(agent.screenshot_interval, 120)
        self.assertFalse(agent.running)
    
    def test_get_system_info(self):
        """Testează obținerea informațiilor despre sistem."""
        agent = BebeAgent()
        system_info = agent.get_system_info()
        
        self.assertIsInstance(system_info, dict)
        if system_info:  # Dacă funcționează pe sistemul curent
            self.assertIn('basic_info', system_info)
            self.assertIn('system_stats', system_info)
            self.assertIn('running_processes', system_info)

if __name__ == '__main__':
    unittest.main()
