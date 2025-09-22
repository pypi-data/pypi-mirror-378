"""
Command Line Interface pentru BebeConn
"""
import argparse
import sys
import os
from .core import BebeConn
from .server import BebeServer
from .agent import BebeAgent

# Fix encoding pentru Windows
if sys.platform == "win32":
    # Setează encoding-ul pentru stdout/stderr
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    # Setează variabila de mediu pentru Python
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

def main():
    """Functia principala pentru CLI."""
    parser = argparse.ArgumentParser(
        description="BebeConn - Monitorizare Laptop de la Distanta",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple de utilizare:
  bebe-conn start                    # Porneste totul local
  bebe-conn start --ngrok           # Porneste cu ngrok pentru acces extern
  bebe-conn start --port 8080       # Porneste pe portul 8080
  bebe-conn start --screenshot 60   # Screenshot la fiecare 60 secunde
  bebe-conn server                  # Porneste doar serverul
  bebe-conn agent                   # Porneste doar agentul
        """
    )
    
    # Subcomenzile principale
    subparsers = parser.add_subparsers(dest='command', help='Comenzi disponibile')
    
    # Comanda start (server + agent)
    start_parser = subparsers.add_parser('start', help='Porneste serverul si agentul')
    start_parser.add_argument('--port', type=int, default=5000, 
                             help='Portul pentru server (default: 5000)')
    start_parser.add_argument('--host', default='127.0.0.1',
                             help='Host-ul pentru server (default: 127.0.0.1)')
    start_parser.add_argument('--ngrok', action='store_true',
                             help='Foloseste ngrok pentru acces extern')
    start_parser.add_argument('--screenshot', type=int, default=30,
                             help='Interval screenshot in secunde (default: 30)')
    start_parser.add_argument('--debug', action='store_true',
                             help='Activeaza modul debug')
    
    # Comanda server
    server_parser = subparsers.add_parser('server', help='Porneste doar serverul web')
    server_parser.add_argument('--port', type=int, default=5000,
                              help='Portul pentru server (default: 5000)')
    server_parser.add_argument('--host', default='127.0.0.1',
                              help='Host-ul pentru server (default: 127.0.0.1)')
    server_parser.add_argument('--debug', action='store_true',
                              help='Activeaza modul debug')
    
    # Comanda agent
    agent_parser = subparsers.add_parser('agent', help='Porneste doar agentul de monitorizare')
    agent_parser.add_argument('--interval', type=int, default=30,
                             help='Interval de actualizare in secunde (default: 30)')
    agent_parser.add_argument('--screenshot', type=int, default=30,
                             help='Interval screenshot in secunde (default: 30)')
    
    # Comanda status
    status_parser = subparsers.add_parser('status', help='Afiseaza statusul sistemului')
    
    # Comanda stop
    stop_parser = subparsers.add_parser('stop', help='Opreste toate procesele BebeConn')
    
    try:
        args = parser.parse_args()
    except UnicodeEncodeError:
        # Fallback pentru probleme de encoding
        print("Eroare de encoding. Incearca sa rulezi comanda intr-un terminal cu suport UTF-8.")
        sys.exit(1)
    except SystemExit as e:
        # argparse apeleaza sys.exit() pentru --help
        sys.exit(e.code)
    
    # Executa comanda
    if not args.command:
        parser.print_help()
        return
    
    try:
        # În cli.py, în secțiunea pentru args.command == 'start':
        if args.command == 'start':
            print(f"Pornesc BebeConn pe {args.host}:{args.port}")
            if args.ngrok:
                print("Ngrok va fi activat pentru acces extern...")
            
            # Creează instanța BebeConn cu parametrii corecți
            bebe_conn = BebeConn(
                ngrok=args.ngrok, 
                port=args.port, 
                screenshot_interval=args.screenshot
            )
            
            # Pornește sistemul (nu start_all!)
            bebe_conn.start()
            
        elif args.command == 'server':
            print(f"Pornesc doar serverul BebeConn pe {args.host}:{args.port}")
            server = BebeServer(host=args.host, port=args.port, debug=args.debug)
            server.start()
            
        elif args.command == 'agent':
            print(f"Pornesc doar agentul de monitorizare (interval: {args.interval}s)")
            agent = BebeAgent(
                update_interval=args.interval,
                screenshot_interval=args.screenshot
            )
            agent.start()
            
        elif args.command == 'status':
            print("Verific statusul BebeConn...")
            
            # Verifică simplu dacă serverul răspunde
            import requests
            try:
                response = requests.get(f"http://127.0.0.1:5000/api/status", timeout=3)
                if response.status_code == 200:
                    print("Server: Activ")
                    data = response.json()
                    print(f"Agent: {'Activ' if data.get('agent_status', {}).get('connected') else 'Inactiv'}")
                else:
                    print("Server: Inactiv")
            except:
                print("Server: Inactiv")
                print("Agent: Inactiv")
            
        elif args.command == 'stop':
            print("Opresc toate procesele BebeConn...")
            bebe_conn = BebeConn()
            bebe_conn.stop_all()
            print("Toate procesele au fost oprite.")
            
    except KeyboardInterrupt:
        print("\nOprire cu Ctrl+C detectata. Se inchide...")
        sys.exit(0)
    except Exception as e:
        print(f"Eroare: {e}")
        if args.debug if 'args' in locals() and hasattr(args, 'debug') else False:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()