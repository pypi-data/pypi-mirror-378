#!/usr/bin/env python3

"""
Mova Configuration Manager - zarządzanie konfiguracją usług i ustawień systemowych
"""

import json
import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class ConfigManager:
    """Menedżer konfiguracji Mova"""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir or os.path.expanduser("~/.mova"))
        self.config_file = self.config_dir / "config.yaml"
        self.services_file = self.config_dir / "services.yaml"
        self.state_file = self.config_dir / "state.json"
        
        # Utwórz katalog konfiguracji jeśli nie istnieje
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Załaduj domyślną konfigurację
        self._ensure_default_config()
        
    def _ensure_default_config(self):
        """Upewnij się, że istnieje domyślna konfiguracja"""
        default_config = {
            'mova': {
                'server_url': 'http://localhost:8094',
                'auto_start': False,
                'log_level': 'INFO',
                'services_enabled': True,
                'rss_enabled': False,
                'rss_port': 8011,
                'voice_enabled': False,
                'voice_default_language': 'pl'
            },
            'services': {
                'docker': {
                    'enabled': False,
                    'socket_path': '/var/run/docker.sock',
                    'monitor_containers': True,
                    'monitor_images': True
                },
                'systemd': {
                    'enabled': False,
                    'monitor_services': []
                },
                'custom': {
                    'enabled': False,
                    'scripts': []
                }
            },
            'rss': {
                'title': 'Mova System Monitor',
                'description': 'Real-time system monitoring via RSS',
                'max_items': 100,
                'refresh_interval': 30
            },
            'voice': {
                'whisper_model': 'base',
                'languages': {
                    'pl': {
                        'name': 'Polski',
                        'tts_voice': 'pl',
                        'enabled': True
                    },
                    'en': {
                        'name': 'English',
                        'tts_voice': 'en',
                        'enabled': True
                    },
                    'de': {
                        'name': 'Deutsch',
                        'tts_voice': 'de',
                        'enabled': True
                    }
                }
            }
        }
        
        if not self.config_file.exists():
            self.save_config(default_config)
            
        # Domyślny stan usług
        default_state = {
            'last_updated': datetime.now().isoformat(),
            'services': {},
            'rss_server': {
                'running': False,
                'port': None,
                'pid': None
            },
            'voice_session': {
                'active': False,
                'language': 'pl'
            }
        }
        
        if not self.state_file.exists():
            self.save_state(default_state)
    
    def load_config(self) -> Dict[str, Any]:
        """Załaduj konfigurację"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Błąd ładowania konfiguracji: {e}")
            return {}
    
    def save_config(self, config: Dict[str, Any]):
        """Zapisz konfigurację"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"❌ Błąd zapisywania konfiguracji: {e}")
    
    def load_state(self) -> Dict[str, Any]:
        """Załaduj stan aplikacji"""
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Błąd ładowania stanu: {e}")
            return {}
    
    def save_state(self, state: Dict[str, Any]):
        """Zapisz stan aplikacji"""
        try:
            state['last_updated'] = datetime.now().isoformat()
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Błąd zapisywania stanu: {e}")
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Pobierz konfigurację konkretnej usługi"""
        config = self.load_config()
        return config.get('services', {}).get(service_name, {})
    
    def set_service_enabled(self, service_name: str, enabled: bool):
        """Ustaw czy usługa jest włączona"""
        config = self.load_config()
        if 'services' not in config:
            config['services'] = {}
        if service_name not in config['services']:
            config['services'][service_name] = {}
        
        config['services'][service_name]['enabled'] = enabled
        self.save_config(config)
        
        # Zaktualizuj stan
        state = self.load_state()
        if 'services' not in state:
            state['services'] = {}
        state['services'][service_name] = {
            'enabled': enabled,
            'last_changed': datetime.now().isoformat()
        }
        self.save_state(state)
    
    def is_service_enabled(self, service_name: str) -> bool:
        """Sprawdź czy usługa jest włączona"""
        config = self.load_config()
        return config.get('services', {}).get(service_name, {}).get('enabled', False)
    
    def get_enabled_services(self) -> List[str]:
        """Pobierz listę włączonych usług"""
        config = self.load_config()
        enabled_services = []
        
        for service_name, service_config in config.get('services', {}).items():
            if service_config.get('enabled', False):
                enabled_services.append(service_name)
        
        return enabled_services
    
    def update_service_state(self, service_name: str, state_data: Dict[str, Any]):
        """Zaktualizuj stan usługi"""
        state = self.load_state()
        if 'services' not in state:
            state['services'] = {}
        
        if service_name not in state['services']:
            state['services'][service_name] = {}
        
        state['services'][service_name].update(state_data)
        state['services'][service_name]['last_updated'] = datetime.now().isoformat()
        
        self.save_state(state)
    
    def get_service_state(self, service_name: str) -> Dict[str, Any]:
        """Pobierz stan usługi"""
        state = self.load_state()
        return state.get('services', {}).get(service_name, {})
    
    def set_auto_start(self, enabled: bool):
        """Ustaw auto-start Mova"""
        config = self.load_config()
        config['mova']['auto_start'] = enabled
        self.save_config(config)
    
    def is_auto_start_enabled(self) -> bool:
        """Sprawdź czy auto-start jest włączony"""
        config = self.load_config()
        return config.get('mova', {}).get('auto_start', False)
    
    def get_rss_config(self) -> Dict[str, Any]:
        """Pobierz konfigurację RSS"""
        config = self.load_config()
        return config.get('rss', {})
    
    def get_voice_config(self) -> Dict[str, Any]:
        """Pobierz konfigurację głosową"""
        config = self.load_config()
        return config.get('voice', {})
    
    def set_rss_server_state(self, running: bool, port: Optional[int] = None, pid: Optional[int] = None):
        """Ustaw stan serwera RSS"""
        state = self.load_state()
        state['rss_server'] = {
            'running': running,
            'port': port,
            'pid': pid,
            'last_updated': datetime.now().isoformat()
        }
        self.save_state(state)
    
    def get_rss_server_state(self) -> Dict[str, Any]:
        """Pobierz stan serwera RSS"""
        state = self.load_state()
        return state.get('rss_server', {})
