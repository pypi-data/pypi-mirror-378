#!/usr/bin/env python3

"""
Mova RSS Server - serwer RSS do monitoringu systemu w czasie rzeczywistym
"""

import argparse
import asyncio
import json
import signal
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from feedgen.feed import FeedGenerator
    from feedgen.entry import FeedEntry
except ImportError:
    print("❌ feedgen nie jest zainstalowany. Instaluj: pip install feedgen")
    sys.exit(1)

try:
    from aiohttp import web, ClientSession
    import aiohttp
except ImportError:
    print("❌ aiohttp nie jest zainstalowany. Instaluj: pip install aiohttp")
    sys.exit(1)

try:
    # Add CLI directory to Python path
    import sys
    import os
    cli_dir = os.path.dirname(os.path.abspath(__file__))
    if cli_dir not in sys.path:
        sys.path.insert(0, cli_dir)
    
    from config_manager import ConfigManager
    from service_connectors import ServiceManager
except ImportError as e:
    print("⚠️ Moduły Mova nie są dostępne - funkcje podstawowe")
    print(f"💡 Import error: {e}")
    ConfigManager = None
    ServiceManager = None


class MovaRSSServer:
    """Serwer RSS dla Mova"""
    
    def __init__(self, port: int = 8011, mova_server: str = "http://localhost:8094"):
        self.port = port
        self.mova_server = mova_server
        self.app = web.Application()
        self.config_manager = ConfigManager() if ConfigManager else None
        self.service_manager = ServiceManager(self.config_manager) if ServiceManager and self.config_manager else None
        
        # Cache dla danych RSS
        self.rss_cache = {
            'logs': [],
            'services': {},
            'last_update': None
        }
        
        # Konfiguracja RSS
        self.rss_config = self.config_manager.get_rss_config() if self.config_manager else {
            'title': 'Mova System Monitor',
            'description': 'Real-time system monitoring via RSS',
            'max_items': 100,
            'refresh_interval': 30
        }
        
        self._setup_routes()
        self._setup_signal_handlers()
    
    def _setup_routes(self):
        """Konfiguruj routing dla serwera"""
        self.app.router.add_get('/', self.handle_index)
        self.app.router.add_get('/rss', self.handle_rss_feed)
        self.app.router.add_get('/rss.xml', self.handle_rss_feed)
        self.app.router.add_get('/status', self.handle_status)
        self.app.router.add_get('/services', self.handle_services)
        self.app.router.add_get('/logs', self.handle_logs)
        self.app.router.add_get('/health', self.handle_health)
    
    def _setup_signal_handlers(self):
        """Konfiguruj obsługę sygnałów"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Otrzymano sygnał {signum}, zamykanie serwera RSS...")
            if self.config_manager:
                self.config_manager.set_rss_server_state(False)
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def handle_index(self, request):
        """Strona główna z listą dostępnych endpointów"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mova RSS Server</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                .endpoint {{ margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 5px; }}
                .endpoint h3 {{ margin: 0 0 10px 0; color: #0066cc; }}
                .endpoint code {{ background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }}
                .status {{ color: #00aa00; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>📡 Mova RSS Server</h1>
            <p class="status">✅ Serwer działa na porcie {self.port}</p>
            
            <h2>Dostępne endpointy:</h2>
            
            <div class="endpoint">
                <h3>🔗 RSS Feed</h3>
                <p><code><a href="/rss">/rss</a></code> - Główny feed RSS z logami i statusem usług</p>
            </div>
            
            <div class="endpoint">
                <h3>📊 Status</h3>
                <p><code><a href="/status">/status</a></code> - Status serwera RSS i statystyki</p>
            </div>
            
            <div class="endpoint">
                <h3>🔧 Usługi</h3>
                <p><code><a href="/services">/services</a></code> - Status monitorowanych usług systemowych</p>
            </div>
            
            <div class="endpoint">
                <h3>📝 Logi</h3>
                <p><code><a href="/logs">/logs</a></code> - Ostatnie logi systemowe w formacie JSON</p>
            </div>
            
            <div class="endpoint">
                <h3>❤️ Health</h3>
                <p><code><a href="/health">/health</a></code> - Health check serwera</p>
            </div>
            
            <h2>Konfiguracja RSS:</h2>
            <ul>
                <li><strong>Maksymalna liczba elementów:</strong> {self.rss_config['max_items']}</li>
                <li><strong>Interwał odświeżania:</strong> {self.rss_config['refresh_interval']} sekund</li>
                <li><strong>Serwer Mova:</strong> {self.mova_server}</li>
            </ul>
            
            <p><em>Ostatnia aktualizacja: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
        </body>
        </html>
        """
        return web.Response(text=html_content, content_type='text/html')
    
    async def handle_rss_feed(self, request):
        """Generuj feed RSS"""
        try:
            # Odśwież dane jeśli potrzeba
            await self._refresh_data()
            
            # Utwórz generator RSS
            fg = FeedGenerator()
            fg.id(f'http://localhost:{self.port}/rss')
            fg.title(self.rss_config['title'])
            fg.link(href=f'http://localhost:{self.port}', rel='alternate')
            fg.description(self.rss_config['description'])
            fg.language('pl')
            fg.lastBuildDate(datetime.now(timezone.utc))
            fg.generator('Mova RSS Server')
            
            # Dodaj wpisy z logów
            for log_entry in self.rss_cache['logs'][-self.rss_config['max_items']:]:
                fe = fg.add_entry()
                
                # ID unikalny dla każdego wpisu
                entry_id = f"log-{log_entry.get('timestamp', '')}-{hash(log_entry.get('message', ''))}"
                fe.id(entry_id)
                
                # Tytuł z poziomem loga i usługą
                level = log_entry.get('level', 'info').upper()
                service = log_entry.get('service', 'system')
                title = f"[{level}] {service}"
                fe.title(title)
                
                # Opis z wiadomością
                message = log_entry.get('message', '')
                description = f"""
                <h3>{title}</h3>
                <p><strong>Usługa:</strong> {service}</p>
                <p><strong>Poziom:</strong> {level}</p>
                <p><strong>Wiadomość:</strong> {message}</p>
                <p><strong>Czas:</strong> {log_entry.get('timestamp', '')}</p>
                """
                fe.description(description)
                
                # Data publikacji
                try:
                    timestamp_str = log_entry.get('timestamp', '')
                    if timestamp_str:
                        # Handle different timestamp formats
                        if 'Z' in timestamp_str:
                            pub_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        elif '+' in timestamp_str or timestamp_str.endswith('00:00'):
                            pub_date = datetime.fromisoformat(timestamp_str)
                        else:
                            # Assume UTC if no timezone info
                            pub_date = datetime.fromisoformat(timestamp_str).replace(tzinfo=timezone.utc)
                    else:
                        pub_date = datetime.now(timezone.utc)
                    fe.pubDate(pub_date)
                except Exception as e:
                    # Fallback to current time with UTC timezone
                    fe.pubDate(datetime.now(timezone.utc))
                
                # Link do szczegółów
                fe.link(href=f"http://localhost:{self.port}/logs")
            
            # Dodaj wpisy ze statusem usług
            if self.rss_cache['services']:
                fe = fg.add_entry()
                fe.id(f"services-status-{int(time.time())}")
                fe.title("🔧 Status usług systemowych")
                
                services_html = "<h3>Status usług:</h3><ul>"
                for service_name, status in self.rss_cache['services'].items():
                    available = status.get('available', False)
                    status_icon = "✅" if available else "❌"
                    services_html += f"<li>{status_icon} {service_name.upper()}: {'Dostępna' if available else 'Niedostępna'}</li>"
                services_html += "</ul>"
                
                fe.description(services_html)
                fe.pubDate(datetime.now(timezone.utc))
                fe.link(href=f"http://localhost:{self.port}/services")
            
            # Wygeneruj XML
            rss_xml = fg.rss_str(pretty=True)
            return web.Response(body=rss_xml, content_type='application/rss+xml', charset='utf-8')
            
        except Exception as e:
            print(f"❌ Błąd generowania RSS: {e}")
            return web.Response(text=f"Błąd generowania RSS: {e}", status=500)
    
    async def handle_status(self, request):
        """Status serwera RSS"""
        try:
            await self._refresh_data()
            
            status_data = {
                'server': {
                    'running': True,
                    'port': self.port,
                    'uptime': time.time() - getattr(self, 'start_time', time.time()),
                    'mova_server': self.mova_server
                },
                'rss': {
                    'title': self.rss_config['title'],
                    'max_items': self.rss_config['max_items'],
                    'refresh_interval': self.rss_config['refresh_interval'],
                    'last_update': self.rss_cache.get('last_update'),
                    'logs_count': len(self.rss_cache['logs']),
                    'services_count': len(self.rss_cache['services'])
                },
                'timestamp': datetime.now().isoformat()
            }
            
            return web.json_response(status_data)
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def handle_services(self, request):
        """Status usług systemowych"""
        try:
            await self._refresh_data()
            
            services_data = {
                'services': self.rss_cache['services'],
                'timestamp': datetime.now().isoformat(),
                'total_services': len(self.rss_cache['services'])
            }
            
            return web.json_response(services_data)
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def handle_logs(self, request):
        """Ostatnie logi systemowe"""
        try:
            await self._refresh_data()
            
            limit = int(request.query.get('limit', 50))
            logs_data = {
                'logs': self.rss_cache['logs'][-limit:],
                'timestamp': datetime.now().isoformat(),
                'total_logs': len(self.rss_cache['logs'])
            }
            
            return web.json_response(logs_data)
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def handle_health(self, request):
        """Health check"""
        return web.json_response({
            'status': 'healthy',
            'server': 'mova-rss',
            'port': self.port,
            'timestamp': datetime.now().isoformat()
        })
    
    async def _refresh_data(self):
        """Odśwież dane z serwera Mova i usług"""
        now = datetime.now()
        
        # Sprawdź czy potrzeba odświeżenia
        if (self.rss_cache['last_update'] and 
            (now - datetime.fromisoformat(self.rss_cache['last_update'])).seconds < self.rss_config['refresh_interval']):
            return
        
        try:
            # Pobierz logi z serwera Mova
            async with ClientSession() as session:
                try:
                    async with session.get(f"{self.mova_server}/api/logs?limit=100") as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            self.rss_cache['logs'] = data.get('logs', [])
                        else:
                            print(f"⚠️ Błąd pobierania logów: {resp.status}")
                except Exception as e:
                    print(f"⚠️ Nie można połączyć się z serwerem Mova: {e}")
            
            # Pobierz status usług
            if self.service_manager:
                try:
                    services_status = self.service_manager.get_enabled_services_status()
                    self.rss_cache['services'] = services_status
                except Exception as e:
                    print(f"⚠️ Błąd pobierania statusu usług: {e}")
            
            self.rss_cache['last_update'] = now.isoformat()
            
        except Exception as e:
            print(f"❌ Błąd odświeżania danych: {e}")
    
    async def start_server(self):
        """Uruchom serwer RSS"""
        self.start_time = time.time()
        
        print(f"🚀 Uruchamianie serwera RSS na porcie {self.port}...")
        print(f"🌐 Dostępny pod: http://localhost:{self.port}")
        print(f"📡 RSS Feed: http://localhost:{self.port}/rss")
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        
        print(f"✅ Serwer RSS uruchomiony pomyślnie")
        
        # Uruchom w nieskończonej pętli
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Zatrzymywanie serwera RSS...")
        finally:
            await runner.cleanup()


def main():
    """Główna funkcja serwera RSS"""
    parser = argparse.ArgumentParser(description='Mova RSS Server')
    parser.add_argument('--port', type=int, default=8011, help='Port serwera RSS')
    parser.add_argument('--mova-server', type=str, default='http://localhost:8094', 
                       help='Adres serwera Mova')
    
    args = parser.parse_args()
    
    # Utwórz i uruchom serwer
    server = MovaRSSServer(port=args.port, mova_server=args.mova_server)
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        print("\n👋 Serwer RSS zatrzymany przez użytkownika")
    except Exception as e:
        print(f"❌ Błąd serwera RSS: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
