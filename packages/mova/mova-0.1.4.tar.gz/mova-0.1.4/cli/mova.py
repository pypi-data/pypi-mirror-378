#!/usr/bin/env python3

"""Mova CLI - narzędzie do komunikacji i zarządzania logami, komendami shell oraz interakcjami z serwerem Mova."""

import argparse
import sys
import json
import requests
import re
import time
import os
import subprocess
import tempfile
import urllib.request
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
import uuid

# Import our new modules
try:
    # Add CLI directory to Python path
    import sys
    cli_dir = os.path.dirname(os.path.abspath(__file__))
    if cli_dir not in sys.path:
        sys.path.insert(0, cli_dir)
    
    from config_manager import ConfigManager
    from service_connectors import ServiceManager
    from security_manager import SecurityManager, ACLRule, CORSPolicy, InstanceProfile, SecurityLevel, AccessAction
    from mova_voice import VoiceInterface, check_voice_dependencies, get_supported_languages
except ImportError as e:
    # Fallback if modules not available
    ConfigManager = None
    ServiceManager = None
    SecurityManager = None
    ACLRule = None
    CORSPolicy = None
    InstanceProfile = None
    SecurityLevel = None
    AccessAction = None
    VoiceInterface = None
    check_voice_dependencies = None
    get_supported_languages = None
    print("⚠️ Service management, security, and voice modules not available")
    print(f"💡 Import error: {e}")
    print("🔧 Run 'make install' to setup dependencies")

# Configuration
DEFAULT_SERVER = "http://localhost:8094"

def detect_service_name():
    """Inteligentna detekcja nazwy usługi na podstawie kontekstu"""
    try:
        # Pobierz bieżący katalog roboczy
        cwd = os.getcwd()
        cwd_path = Path(cwd)
        
        # 1. Sprawdź czy jesteśmy w repozytorium Git
        try:
            git_result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], 
                                      capture_output=True, text=True, timeout=5)
            if git_result.returncode == 0:
                git_root = Path(git_result.stdout.strip())
                # Użyj nazwy repozytorium Git jako nazwy usługi
                service_name = git_root.name
                if service_name and service_name != '.':
                    return f"git:{service_name}"
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # 2. Sprawdź czy jesteśmy w katalogu z charakterystycznymi plikami
        characteristic_files = {
            'package.json': 'nodejs',
            'requirements.txt': 'python',
            'Cargo.toml': 'rust', 
            'go.mod': 'golang',
            'pom.xml': 'java',
            'docker-compose.yml': 'docker',
            'Dockerfile': 'docker',
            '.env': 'env'
        }
        
        for file_name, tech in characteristic_files.items():
            if (cwd_path / file_name).exists():
                return f"{tech}:{cwd_path.name}"
        
        # 3. Sprawdź nazwa katalogu nadrzędnego (projekt)
        if cwd_path.name and cwd_path.name not in ['.', '/', 'home']:
            return f"dir:{cwd_path.name}"
        
        # 4. Sprawdź katalog nadrzędny jeśli obecny to 'src', 'app', etc.
        if cwd_path.name in ['src', 'app', 'lib', 'cli', 'server']:
            parent = cwd_path.parent
            if parent.name and parent.name not in ['.', '/', 'home']:
                return f"proj:{parent.name}"
        
        # 5. Użyj nazwy użytkownika i ostatniego katalogu
        username = os.getenv('USER', os.getenv('USERNAME', 'user'))
        return f"{username}:{cwd_path.name}"
        
    except Exception:
        # Fallback - użyj nazwy katalogu lub unknown
        try:
            cwd = os.getcwd()
            dir_name = os.path.basename(cwd)
            return dir_name if dir_name else "unknown"
        except:
            return "unknown"

def make_request(method: str, endpoint: str, data: Optional[dict] = None, server: str = DEFAULT_SERVER) -> dict:
    """Make HTTP request to Mova server"""
    url = f"{server}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, params=data or {})
        elif method.upper() == "POST":
            response = requests.post(url, json=data or {})
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f"❌ Błąd: Nie można połączyć się z serwerem Mova na {server}")
        print(f"💡 Upewnij się, że serwer jest uruchomiony: make server")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"❌ Błąd HTTP {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Błąd: {str(e)}")
        sys.exit(1)

def parse_time_duration(duration: str) -> float:
    """Parse duration string like '5m', '1h', '30s' into minutes"""
    if not duration:
        return None
        
    match = re.match(r'^(\d+)([smh])$', duration)
    if not match:
        raise ValueError("Invalid duration format. Use: 30s, 5m, 1h")
    
    value, unit = match.groups()
    multipliers = {'s': 1/60, 'm': 1, 'h': 60}
    return int(value) * multipliers[unit]

def format_log_output(logs: list, full_messages: bool = False) -> None:
    """Format and print logs"""
    if not logs:
        print("📭 Brak logów do wyświetlenia")
        return
        
    print(f"📊 Znaleziono {len(logs)} logów:")
    print("-" * 80)
    
    for log in logs:
        timestamp = log.get('timestamp', '')
        level = log.get('level', 'info').upper()
        service = log.get('service', 'unknown')
        message = log.get('message', '')
        
        # Color coding for levels
        level_colors = {
            'ERROR': '🔴',
            'WARNING': '🟡', 
            'INFO': '🔵',
            'DEBUG': '⚪'
        }
        
        icon = level_colors.get(level, '📝')
        
        if full_messages:
            # Wyświetl pełną wiadomość z podziałem na linie jeśli jest długa
            print(f"{icon} [{timestamp[:19]}] {level:7} | {service}")
            print(f"    📄 Treść: {message}")
            print("-" * 60)
        else:
            # Standardowe wyświetlanie z potencjalnym obcięciem
            display_message = message[:100] + "..." if len(message) > 100 else message
            print(f"{icon} [{timestamp[:19]}] {level:7} | {service:10} | {display_message}")

def main():
    parser = argparse.ArgumentParser(description='Mova CLI - narzędzie komunikacyjne')
    subparsers = parser.add_subparsers(dest='command')

    # Global options
    parser.add_argument('--server', type=str, default=DEFAULT_SERVER, help='Adres serwera Mova')

    # Komenda shell
    shell_parser = subparsers.add_parser('shell', help='Wykonaj komendę shell')
    shell_parser.add_argument('cmd', type=str, help='Komenda do wykonania')
    shell_parser.add_argument('--timeout', type=int, default=30, help='Timeout w sekundach')

    # Komenda list
    list_parser = subparsers.add_parser('list', help='Lista logów lub zdarzeń')
    list_parser.add_argument('level', type=str, help='Poziom logów (error, info, warning, all)')
    list_parser.add_argument('--last', type=str, help='Czas od ostatniego zdarzenia (np. 5m, 1h, 30s)')
    list_parser.add_argument('--service', type=str, help='Filtruj po nazwie serwisu')
    list_parser.add_argument('--limit', type=int, default=20, help='Maksymalna liczba logów')

    # Komenda info
    info_parser = subparsers.add_parser('info', help='Wyślij log informacyjny')
    info_parser.add_argument('message', type=str, help='Wiadomość logu')
    info_parser.add_argument('--service', type=str, help='Nazwa serwisu')

    # Komenda warning
    warning_parser = subparsers.add_parser('warning', help='Wyślij ostrzeżenie')
    warning_parser.add_argument('message', type=str, help='Wiadomość ostrzeżenia')
    warning_parser.add_argument('--service', type=str, help='Nazwa serwisu')
    warning_parser.add_argument('--mqtt-broker', type=str, help='Adres brokera MQTT')
    warning_parser.add_argument('--mqtt-topic', type=str, help='Temat MQTT')

    # Komenda error
    error_parser = subparsers.add_parser('error', help='Wyślij błąd')
    error_parser.add_argument('message', type=str, help='Wiadomość błędu')
    error_parser.add_argument('--service', type=str, help='Nazwa usługi')

    # Komenda http
    http_parser = subparsers.add_parser('http', help='Wykonaj kod JS w przeglądarce')
    http_parser.add_argument('address', type=str, help='Adres hosta (localhost, IP, domain)')
    http_parser.add_argument('js_code', type=str, help='Kod JS do wykonania')
    http_parser.add_argument('--port', type=int, default=8094, help='Port serwera Mova')

    # Komenda health (health check)
    health_parser = subparsers.add_parser('health', help='Sprawdź status serwera')

    # Komenda watch (continuous monitoring)
    watch_parser = subparsers.add_parser('watch', help='Monitoruj logi w czasie rzeczywistym')
    watch_parser.add_argument('level', choices=['info', 'warning', 'error', 'all'], help='Poziom logów do monitorowania')
    watch_parser.add_argument('--service', type=str, help='Filtruj według nazwy serwisu')
    watch_parser.add_argument('--interval', type=int, default=2, help='Interwał odświeżania w sekundach (domyślnie: 2)')
    watch_parser.add_argument('--limit', type=int, default=10, help='Liczba wyświetlanych logów (domyślnie: 10)')
    watch_parser.add_argument('--follow', action='store_true', help='Pokazuj tylko nowe logi (jak tail -f)')
    watch_parser.add_argument('--full', action='store_true', help='Pokazuj pełne wiadomości bez obcięć')
    watch_parser.add_argument('--server', type=str, default=DEFAULT_SERVER, help='Adres serwera Mova')

    # ===== NOWE FUNKCJONALNOŚCI =====
    
    # Komenda services (zarządzanie usługami)
    services_parser = subparsers.add_parser('services', help='Zarządzaj zintegrowanymi usługami systemowymi')
    services_subparsers = services_parser.add_subparsers(dest='services_action')
    
    # mova services list
    services_list_parser = services_subparsers.add_parser('list', help='Pokaż listę dostępnych usług')
    services_list_parser.add_argument('--detailed', action='store_true', help='Pokaż szczegółowe informacje')
    
    # mova services enable/disable
    services_enable_parser = services_subparsers.add_parser('enable', help='Włącz monitoring usługi')
    services_enable_parser.add_argument('service_name', help='Nazwa usługi do włączenia')
    
    services_disable_parser = services_subparsers.add_parser('disable', help='Wyłącz monitoring usługi')
    services_disable_parser.add_argument('service_name', help='Nazwa usługi do wyłączenia')
    
    # mova services status
    services_status_parser = services_subparsers.add_parser('status', help='Pokaż status usług')
    services_status_parser.add_argument('service_name', nargs='?', help='Nazwa konkretnej usługi (opcjonalnie)')
    
    # mova services info
    services_info_parser = services_subparsers.add_parser('info', help='Szczegółowe informacje o usłudze')
    services_info_parser.add_argument('service_name', help='Nazwa usługi')
    
    # Komenda RSS
    rss_parser = subparsers.add_parser('rss', help='Uruchom serwer RSS dla monitoringu')
    rss_parser.add_argument('--port', type=int, default=8011, help='Port serwera RSS (domyślnie: 8011)')
    rss_parser.add_argument('--stop', action='store_true', help='Zatrzymaj serwer RSS')
    rss_parser.add_argument('--status', action='store_true', help='Sprawdź status serwera RSS')
    
    # Komenda on/off (auto-start)
    on_parser = subparsers.add_parser('on', help='Włącz auto-start Mova przy starcie systemu')
    off_parser = subparsers.add_parser('off', help='Wyłącz auto-start Mova')
    
    # Komenda talk (funkcje głosowe)
    talk_parser = subparsers.add_parser('talk', help='Interakcja głosowa z Mova')
    talk_parser.add_argument('language', choices=['pl', 'en', 'de'], help='Język interfejsu głosowego')
    talk_parser.add_argument('--listen-only', action='store_true', help='Tylko nasłuchuj, nie odpowiadaj głosowo')
    talk_parser.add_argument('--text-only', action='store_true', help='Tylko odpowiedzi tekstowe')
    talk_parser.add_argument('--continuous', action='store_true', help='Tryb ciągłego nasłuchiwania')
    talk_parser.add_argument('--debug-tts', action='store_true', help='Tryb debug TTS - testuj TTS nawet z --text-only')
    
    # Komenda read (zaawansowane czytanie logów)
    read_parser = subparsers.add_parser('read', help='Czytaj logi z zaawansowanym filtrowaniem czasowym')
    read_parser.add_argument('level', choices=['error', 'info', 'warning', 'all'], help='Poziom logów do odczytu')
    read_parser.add_argument('--last', type=str, help='Czas od ostatniego zdarzenia (np. 5m, 1h, 30s, 2d)')
    read_parser.add_argument('--watch', action='store_true', help='Tryb ciągłego monitorowania w czasie rzeczywistym')
    read_parser.add_argument('--service', type=str, help='Filtruj według nazwy serwisu')
    read_parser.add_argument('--limit', type=int, default=50, help='Maksymalna liczba logów (domyślnie: 50)')
    read_parser.add_argument('--interval', type=int, default=2, help='Interwał odświeżania w trybie --watch (sekundy)')
    read_parser.add_argument('--format', choices=['compact', 'detailed', 'json', 'ndjson'], default='compact', help='Format wyświetlania (ndjson = newline-delimited JSON)')
    read_parser.add_argument('--tts', action='store_true', help='Odczytaj logi głosowo używając TTS (Text-to-Speech)')

    # ===== ZARZĄDZANIE URZĄDZENIAMI AUDIO =====
    
    # Komenda audio (zarządzanie wszystkimi urządzeniami audio)
    audio_parser = subparsers.add_parser('audio', help='Zarządzaj urządzeniami audio dla TTS i STT')
    audio_subparsers = audio_parser.add_subparsers(dest='audio_action')
    
    # mova audio list
    audio_list_parser = audio_subparsers.add_parser('list', help='Pokaż wszystkie dostępne urządzenia audio (wejścia i wyjścia)')
    audio_list_parser.add_argument('--detailed', action='store_true', help='Szczegółowe informacje o urządzeniach')
    audio_list_parser.add_argument('--test', action='store_true', help='Przetestuj działanie każdego urządzenia')
    
    # mova audio get - NOWA KOMENDA
    audio_get_parser = audio_subparsers.add_parser('get', help='Pokaż aktualnie ustawione domyślne urządzenia audio')
    audio_get_parser.add_argument('--detailed', action='store_true', help='Szczegółowe informacje o aktualnych urządzeniach')
    
    # mova audio set
    audio_set_parser = audio_subparsers.add_parser('set', help='Ustaw urządzenia audio')
    audio_set_subparsers = audio_set_parser.add_subparsers(dest='audio_set_action')
    
    # mova audio set auto
    audio_set_auto_parser = audio_set_subparsers.add_parser('auto', help='Automatycznie wybierz najlepsze urządzenia audio dla TTS i STT')
    audio_set_auto_parser.add_argument('--test', action='store_true', help='Przetestuj wybrane urządzenia po ustawieniu')
    audio_set_auto_parser.add_argument('--save', action='store_true', help='Zapisz wybór jako domyślny w konfiguracji')
    
    # Komenda speaker (zarządzanie głośnikami/wyjściem TTS)
    speaker_parser = subparsers.add_parser('speaker', help='Zarządzaj głośnikami i wyjściem audio dla TTS')
    speaker_subparsers = speaker_parser.add_subparsers(dest='speaker_action')
    
    # mova speaker list
    speaker_list_parser = speaker_subparsers.add_parser('list', help='Pokaż dostępne głośniki i urządzenia wyjściowe')
    speaker_list_parser.add_argument('--test', action='store_true', help='Przetestuj każdy głośnik z próbką audio')
    speaker_list_parser.add_argument('--current', action='store_true', help='Pokaż aktualnie wybrany głośnik')
    
    # mova speaker set
    speaker_set_parser = speaker_subparsers.add_parser('set', help='Ustaw domyślny głośnik dla TTS')
    speaker_set_parser.add_argument('device_selector', help='Indeks urządzenia z listy (mova speaker list) lub "auto" dla automatycznego wyboru')
    speaker_set_parser.add_argument('--test', action='store_true', help='Przetestuj głośnik po ustawieniu')
    speaker_set_parser.add_argument('--save', action='store_true', help='Zapisz wybór jako domyślny w konfiguracji')
    
    # Komenda mic (zarządzanie mikrofonami/wejściem STT)
    mic_parser = subparsers.add_parser('mic', help='Zarządzaj mikrofonami i wejściem audio dla STT')
    mic_subparsers = mic_parser.add_subparsers(dest='mic_action')
    
    # mova mic list
    mic_list_parser = mic_subparsers.add_parser('list', help='Pokaż dostępne mikrofony i urządzenia wejściowe')
    mic_list_parser.add_argument('--test', action='store_true', help='Przetestuj każdy mikrofon z nagrywaniem próbki')
    mic_list_parser.add_argument('--current', action='store_true', help='Pokaż aktualnie wybrany mikrofon')
    
    # mova mic set
    mic_set_parser = mic_subparsers.add_parser('set', help='Ustaw domyślny mikrofon dla STT')
    mic_set_parser.add_argument('device_selector', help='Indeks urządzenia z listy (mova mic list) lub "auto" dla automatycznego wyboru')
    mic_set_parser.add_argument('--test', action='store_true', help='Przetestuj mikrofon po ustawieniu')
    mic_set_parser.add_argument('--save', action='store_true', help='Zapisz wybór jako domyślny w konfiguracji')

    # ===== SYSTEM BEZPIECZEŃSTWA =====
    
    # Komenda ACL (Access Control Lists)
    acl_parser = subparsers.add_parser('acl', help='Zarządzaj regułami kontroli dostępu (ACL)')
    acl_subparsers = acl_parser.add_subparsers(dest='acl_action')
    
    # mova acl list
    acl_list_parser = acl_subparsers.add_parser('list', help='Pokaż wszystkie reguły ACL')
    acl_list_parser.add_argument('--detailed', action='store_true', help='Szczegółowe informacje o regułach')
    
    # mova acl add
    acl_add_parser = acl_subparsers.add_parser('add', help='Dodaj nową regułę ACL')
    acl_add_parser.add_argument('name', help='Nazwa reguły')
    acl_add_parser.add_argument('source_pattern', help='Wzorzec źródła (IP, domena, wzorzec instancji)')
    acl_add_parser.add_argument('target_resource', help='Docelowy zasób lub endpoint')
    acl_add_parser.add_argument('action', choices=['allow', 'deny', 'log', 'challenge'], help='Akcja kontroli dostępu')
    acl_add_parser.add_argument('--priority', type=int, default=100, help='Priorytet reguły (niższy = wyższy priorytet)')
    acl_add_parser.add_argument('--expires', help='Data wygaśnięcia (YYYY-MM-DD lub YYYY-MM-DD HH:MM)')
    acl_add_parser.add_argument('--description', help='Opis reguły')
    
    # mova acl remove
    acl_remove_parser = acl_subparsers.add_parser('remove', help='Usuń regułę ACL')
    acl_remove_parser.add_argument('rule_id', help='ID reguły do usunięcia')
    
    # mova acl test
    acl_test_parser = acl_subparsers.add_parser('test', help='Przetestuj dostęp na podstawie reguł ACL')
    acl_test_parser.add_argument('source', help='Źródło dostępu (IP, domena)')
    acl_test_parser.add_argument('resource', help='Zasób docelowy')
    acl_test_parser.add_argument('--instance', help='ID instancji źródłowej')
    
    # mova acl status
    acl_status_parser = acl_subparsers.add_parser('status', help='Status systemu ACL')
    
    # Komenda CORS (Cross-Origin Resource Sharing)
    cors_parser = subparsers.add_parser('cors', help='Zarządzaj politykami CORS')
    cors_subparsers = cors_parser.add_subparsers(dest='cors_action')
    
    # mova cors list
    cors_list_parser = cors_subparsers.add_parser('list', help='Pokaż wszystkie polityki CORS')
    cors_list_parser.add_argument('--detailed', action='store_true', help='Szczegółowe informacje o politykach')
    
    # mova cors add
    cors_add_parser = cors_subparsers.add_parser('add', help='Dodaj nową politykę CORS')
    cors_add_parser.add_argument('name', help='Nazwa polityki')
    cors_add_parser.add_argument('--origins', nargs='+', required=True, help='Dozwolone originy (domeny)')
    cors_add_parser.add_argument('--methods', nargs='+', default=['GET', 'POST'], help='Dozwolone metody HTTP')
    cors_add_parser.add_argument('--headers', nargs='+', default=['Content-Type'], help='Dozwolone nagłówki')
    cors_add_parser.add_argument('--credentials', action='store_true', help='Zezwalaj na uwierzytelnianie')
    cors_add_parser.add_argument('--max-age', type=int, default=3600, help='Maksymalny wiek cache (sekundy)')
    cors_add_parser.add_argument('--expose-headers', nargs='+', help='Nagłówki do udostępnienia')
    cors_add_parser.add_argument('--description', help='Opis polityki')
    
    # mova cors remove
    cors_remove_parser = cors_subparsers.add_parser('remove', help='Usuń politykę CORS')
    cors_remove_parser.add_argument('policy_id', help='ID polityki do usunięcia')
    
    # mova cors test
    cors_test_parser = cors_subparsers.add_parser('test', help='Przetestuj nagłówki CORS')
    cors_test_parser.add_argument('origin', help='Origin do testowania')
    cors_test_parser.add_argument('--instance', help='ID instancji')
    
    # Komenda instance (zarządzanie instancjami)
    instance_parser = subparsers.add_parser('instance', help='Zarządzaj instancjami Mova i profilami bezpieczeństwa')
    instance_subparsers = instance_parser.add_subparsers(dest='instance_action')
    
    # mova instance register
    instance_register_parser = instance_subparsers.add_parser('register', help='Zarejestruj nową instancję')
    instance_register_parser.add_argument('instance_id', help='Unikatowy identyfikator instancji')
    instance_register_parser.add_argument('instance_type', choices=['frontend', 'backend', 'firmware', 'mobile', 'desktop'], help='Typ instancji')
    instance_register_parser.add_argument('--security-level', choices=['open', 'restricted', 'secure', 'isolated'], default='restricted', help='Poziom bezpieczeństwa')
    instance_register_parser.add_argument('--trusted', nargs='*', help='Lista zaufanych instancji')
    instance_register_parser.add_argument('--blocked', nargs='*', help='Lista zablokowanych instancji')
    
    # mova instance list
    instance_list_parser = instance_subparsers.add_parser('list', help='Pokaż wszystkie zarejestrowane instancje')
    instance_list_parser.add_argument('--detailed', action='store_true', help='Szczegółowe informacje')
    
    # mova instance unregister
    instance_unregister_parser = instance_subparsers.add_parser('unregister', help='Wyrejestruj instancję')
    instance_unregister_parser.add_argument('instance_id', help='ID instancji do wyrejestrowania')
    
    # mova security (ogólne zarządzanie bezpieczeństwem)
    security_parser = subparsers.add_parser('security', help='Ogólne zarządzanie bezpieczeństwem')
    security_subparsers = security_parser.add_subparsers(dest='security_action')
    
    # mova security status
    security_status_parser = security_subparsers.add_parser('status', help='Status całego systemu bezpieczeństwa')
    
    # mova security audit
    security_audit_parser = security_subparsers.add_parser('audit', help='Pokaż logi audytu bezpieczeństwa')
    security_audit_parser.add_argument('--last', type=int, default=20, help='Liczba ostatnich wpisów')
    
    # mova security init
    security_init_parser = security_subparsers.add_parser('init', help='Inicjalizuj system bezpieczeństwa')
    security_init_parser.add_argument('profile', choices=['development', 'production'], help='Profil bezpieczeństwa do zastosowania')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute commands
    try:
        if args.command == 'shell':
            execute_shell_command(args)
        elif args.command == 'list':
            list_logs(args)
        elif args.command in ['info', 'warning', 'error']:
            send_log(args)
        elif args.command == 'http':
            execute_http_command(args)
        elif args.command == 'health':
            check_health(args)
        elif args.command == 'watch':
            watch_logs(args)
        elif args.command == 'services':
            handle_services_command(args)
        elif args.command == 'rss':
            handle_rss_command(args)
        elif args.command == 'on':
            handle_autostart_on(args)
        elif args.command == 'off':
            handle_autostart_off(args)
        elif args.command == 'talk':
            handle_talk_command(args)
        elif args.command == 'read':
            read_logs_advanced(args)
        elif args.command == 'audio':
            handle_audio_command(args)
        elif args.command == 'speaker':
            handle_speaker_command(args)
        elif args.command == 'mic':
            handle_mic_command(args)
        elif args.command == 'acl':
            handle_acl_command(args)
        elif args.command == 'cors':
            handle_cors_command(args)
        elif args.command == 'instance':
            handle_instance_command(args)
        elif args.command == 'security':
            handle_security_command(args)
        else:
            print(f"❌ Nieznana komenda: {args.command}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Przerwano przez użytkownika")
        sys.exit(0)

def execute_shell_command(args):
    """Execute shell command on server"""
    print(f"🐚 Wykonywanie komendy shell: {args.cmd}")
    
    data = {
        "cmd": args.cmd,
        "timeout": args.timeout
    }
    
    result = make_request("POST", "/api/shell", data, args.server)
    
    if result.get("success"):
        print(f"✅ Komenda wykonana pomyślnie (kod: {result.get('returncode', 0)})")
        if result.get("stdout"):
            print("📤 Stdout:")
            print(result["stdout"])
    else:
        print(f"❌ Komenda zakończona błędem (kod: {result.get('returncode', -1)})")
        if result.get("stderr"):
            print("📥 Stderr:")
            print(result["stderr"])
        if result.get("stdout"):
            print("📤 Stdout:")
            print(result["stdout"])

def list_logs(args):
    """List logs from server"""
    print(f"📋 Pobieranie logów (poziom: {args.level})")
    
    params = {
        "level": args.level if args.level != "all" else None,
        "service": args.service,
        "limit": args.limit
    }
    
    if args.last:
        try:
            params["last_minutes"] = parse_time_duration(args.last)
        except ValueError as e:
            print(f"❌ Błąd parsowania czasu: {e}")
            sys.exit(1)
    
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}
    
    result = make_request("GET", "/api/logs", params, args.server)
    logs = result.get("logs", [])
    
    print(f"📊 Znaleziono {result.get('count', 0)} logów z {result.get('total_stored', 0)} zapisanych")
    format_log_output(logs, getattr(args, 'full', False))

def send_log(args):
    """Send log message to server"""
    level_icons = {
        'info': '🔵',
        'warning': '🟡',
        'error': '🔴'
    }
    
    icon = level_icons.get(args.command, '📝')
    print(f"{icon} Wysyłanie logu {args.command.upper()}: {args.message}")
    
    # Użyj inteligentnej detekcji usługi jeśli nie podano explicite
    service_name = args.service if args.service else detect_service_name()
    
    data = {
        "level": args.command,
        "message": args.message,
        "service": service_name
    }
    
    result = make_request("POST", "/api/log", data, args.server)
    
    if result.get("status") == "logged":
        print(f"✅ Log zapisany pomyślnie")
        timestamp = result.get("entry", {}).get("timestamp", "")
        print(f"🔖 ID: {timestamp}")
    else:
        print("❌ Błąd podczas zapisywania logu")

def execute_http_command(args):
    """Execute JavaScript in browser via HTTP"""
    print(f"🌐 Wysyłanie komendy JS do {args.address}: {args.js_code[:50]}{'...' if len(args.js_code) > 50 else ''}")
    
    data = {
        "js_code": args.js_code,
        "target": args.address
    }
    
    result = make_request("POST", "/api/http-exec", data, args.server)
    
    if result.get("status") == "queued":
        print("✅ Komenda JavaScript została umieszczona w kolejce")
        print(f"🎯 Cel: {result.get('target')}")
        print(f"💡 {result.get('message', 'Użyj WebSocket dla wykonania w czasie rzeczywistym')}")
    else:
        print("❌ Błąd podczas wysyłania komendy JavaScript")

def check_health(args):
    """Check server health"""
    print(f"🔍 Sprawdzanie statusu serwera: {args.server}")
    
    result = make_request("GET", "/health", server=args.server)
    
    status = result.get("status", "unknown")
    if status == "healthy":
        print("✅ Serwer jest zdrowy")
    else:
        print(f"⚠️ Status serwera: {status}")
    
    print(f"🕐 Timestamp: {result.get('timestamp', 'unknown')}")
    print(f"🏷️ Wersja: {result.get('version', 'unknown')}")
    print(f"🐚 Shell włączony: {'✅ TAK' if result.get('shell_enabled') else '❌ NIE'}")
    
    # Test basic connectivity
    try:
        root_response = make_request("GET", "/", server=args.server)
        print("🌐 Połączenie HTTP: ✅ OK")
    except:
        print("🌐 Połączenie HTTP: ❌ BŁĄD")

def watch_logs(args):
    """Continuously monitor logs from server"""
    print(f"👁️ Uruchamianie monitora logów (poziom: {args.level})")
    print(f"🔄 Interwał odświeżania: {args.interval}s")
    if args.service:
        print(f"🏷️ Filtr serwisu: {args.service}")
    if args.follow:
        print("📈 Tryb follow: pokazywanie tylko nowych logów")
    print("⏹️ Naciśnij Ctrl+C aby zatrzymać monitoring\n")
    
    last_timestamp = None
    seen_log_ids = set()
    
    try:
        while True:
            params = {
                "level": args.level if args.level != "all" else None,
                "service": args.service,
                "limit": args.limit if not args.follow else 50  # Więcej logów w trybie follow
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            try:
                result = make_request("GET", "/api/logs", params, args.server)
                logs = result.get("logs", [])
                
                if args.follow:
                    # W trybie follow pokazuj tylko nowe logi
                    new_logs = []
                    for log in logs:
                        log_id = f"{log.get('timestamp', '')}-{log.get('message', '')}"
                        if log_id not in seen_log_ids:
                            new_logs.append(log)
                            seen_log_ids.add(log_id)
                    
                    # Ogranicz rozmiar zestawu seen_log_ids
                    if len(seen_log_ids) > 1000:
                        seen_log_ids = set(list(seen_log_ids)[-500:])
                    
                    if new_logs:
                        print(f"🆕 {len(new_logs)} nowych logów:")
                        format_log_output(new_logs, args.full)
                        print("-" * 60)
                else:
                    # W trybie normalnym pokazuj wszystkie logi z czyszczeniem ekranu
                    print("\033[2J\033[H")  # Clear screen
                    print(f"👁️ Monitor logów Mova - {datetime.now().strftime('%H:%M:%S')}")
                    print(f"📊 Poziom: {args.level} | Interwał: {args.interval}s | Limit: {args.limit}")
                    if args.service:
                        print(f"🏷️ Serwis: {args.service}")
                    print("=" * 70)
                    
                    if logs:
                        format_log_output(logs, args.full)
                    else:
                        print("📭 Brak logów do wyświetlenia")
                    
                    print("=" * 70)
                    print("⏹️ Naciśnij Ctrl+C aby zatrzymać monitoring")
                
            except Exception as e:
                print(f"❌ Błąd pobierania logów: {e}")
            
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print(f"\n👋 Monitoring zatrzymany")
        sys.exit(0)

# ===== IMPLEMENTACJA NOWYCH FUNKCJONALNOŚCI =====

def handle_services_command(args):
    """Obsługa komend zarządzania usługami"""
    if not ConfigManager or not ServiceManager:
        print("❌ Moduły zarządzania usługami niedostępne")
        print("💡 Zainstaluj zależności: pip install -r requirements.txt")
        sys.exit(1)
    
    config_manager = ConfigManager()
    service_manager = ServiceManager(config_manager)
    
    if not hasattr(args, 'services_action') or not args.services_action:
        print("❌ Brak akcji. Użyj: mova services --help")
        sys.exit(1)
    
    if args.services_action == 'list':
        services = service_manager.get_available_services()
        
        print("🔧 Dostępne usługi systemowe:")
        print("=" * 60)
        
        for service in services:
            name = service['name']
            enabled = "✅ WŁĄCZONA" if service['enabled'] else "❌ WYŁĄCZONA"
            available = "🟢 DOSTĘPNA" if service['available'] else "🔴 NIEDOSTĘPNA"
            
            print(f"📋 {name.upper():<12} | {enabled:<12} | {available}")
            
            if args.detailed and service['available']:
                status = service['status']
                for key, value in status.items():
                    if key != 'available':
                        print(f"   └─ {key}: {value}")
                print()
        
        print("=" * 60)
        print("💡 Użyj 'mova services enable/disable <nazwa>' do zarządzania")
    
    elif args.services_action == 'enable':
        service_name = args.service_name
        print(f"🔄 Włączanie monitoringu usługi: {service_name}")
        
        if service_manager.enable_service(service_name):
            print(f"✅ Usługa {service_name} została włączona")
        else:
            print(f"❌ Nie można włączyć usługi {service_name}")
    
    elif args.services_action == 'disable':
        service_name = args.service_name
        print(f"🔄 Wyłączanie monitoringu usługi: {service_name}")
        
        if service_manager.disable_service(service_name):
            print(f"✅ Usługa {service_name} została wyłączona")
        else:
            print(f"❌ Nie można wyłączyć usługi {service_name}")
    
    elif args.services_action == 'status':
        if args.service_name:
            # Status konkretnej usługi
            service_name = args.service_name
            info = service_manager.get_service_info(service_name)
            
            if 'error' in info:
                print(f"❌ {info['error']}")
                return
            
            print(f"📊 Status usługi: {service_name.upper()}")
            print("=" * 50)
            print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            # Status wszystkich włączonych usług
            status = service_manager.get_enabled_services_status()
            
            print("📊 Status włączonych usług:")
            print("=" * 50)
            
            for service_name, service_status in status.items():
                print(f"🔧 {service_name.upper()}:")
                print(json.dumps(service_status, indent=2, ensure_ascii=False))
                print("-" * 30)
    
    elif args.services_action == 'info':
        service_name = args.service_name
        info = service_manager.get_service_info(service_name)
        
        print(f"ℹ️  Szczegółowe informacje: {service_name.upper()}")
        print("=" * 60)
        
        if 'error' in info:
            print(f"❌ {info['error']}")
        else:
            print(json.dumps(info, indent=2, ensure_ascii=False))

def handle_rss_command(args):
    """Obsługa komendy RSS"""
    if not ConfigManager:
        print("❌ Moduł konfiguracji niedostępny")
        sys.exit(1)
    
    config_manager = ConfigManager()
    
    if args.status:
        # Sprawdź status serwera RSS
        rss_state = config_manager.get_rss_server_state()
        
        if rss_state.get('running', False):
            port = rss_state.get('port', 'unknown')
            pid = rss_state.get('pid', 'unknown')
            print(f"✅ Serwer RSS działa na porcie {port} (PID: {pid})")
            print(f"🌐 Dostępny pod: http://localhost:{port}/rss")
        else:
            print("❌ Serwer RSS nie działa")
        return
    
    if args.stop:
        # Zatrzymaj serwer RSS
        rss_state = config_manager.get_rss_server_state()
        
        if not rss_state.get('running', False):
            print("❌ Serwer RSS nie działa")
            return
        
        pid = rss_state.get('pid')
        if pid:
            try:
                os.kill(pid, 15)  # SIGTERM
                config_manager.set_rss_server_state(False)
                print("✅ Serwer RSS został zatrzymany")
            except ProcessLookupError:
                print("⚠️ Proces RSS już nie istnieje")
                config_manager.set_rss_server_state(False)
            except Exception as e:
                print(f"❌ Błąd zatrzymywania serwera RSS: {e}")
        return
    
    # Uruchom serwer RSS
    port = args.port
    print(f"🚀 Uruchamianie serwera RSS na porcie {port}...")
    
    # Sprawdź czy port jest wolny
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    
    if result == 0:
        print(f"❌ Port {port} jest już zajęty")
        sys.exit(1)
    
    # Uruchom serwer RSS w tle
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rss_script = os.path.join(script_dir, 'rss_server.py')
    
    try:
        # Najpierw sprawdź czy rss_server.py istnieje
        if not os.path.exists(rss_script):
            print(f"❌ Nie znaleziono rss_server.py w {rss_script}")
            sys.exit(1)
        
        # Uruchom z logowaniem błędów do pliku tymczasowego
        import tempfile
        log_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.log')
        
        process = subprocess.Popen([
            sys.executable, rss_script, '--port', str(port)
        ], stdout=log_file, stderr=subprocess.STDOUT)
        
        # Poczekaj chwilę i sprawdź czy proces nadal działa
        import time
        time.sleep(2)
        
        if process.poll() is not None:
            # Proces zakończył się - sprawdź logi
            log_file.close()
            with open(log_file.name, 'r') as f:
                error_output = f.read()
            os.unlink(log_file.name)
            print(f"❌ Serwer RSS nie mógł się uruchomić:")
            print(error_output)
            sys.exit(1)
        
        config_manager.set_rss_server_state(True, port, process.pid)
        log_file.close()
        os.unlink(log_file.name)
        
        # Sprawdź czy serwer rzeczywiście odpowiada
        time.sleep(1)
        try:
            import urllib.request
            urllib.request.urlopen(f'http://localhost:{port}/status', timeout=3)
            print(f"✅ Serwer RSS uruchomiony i odpowiada na porcie {port}")
            print(f"🌐 Dostępny pod: http://localhost:{port}/rss")
        except Exception as e:
            print(f"⚠️ Serwer RSS uruchomiony ale nie odpowiada: {e}")
            print(f"🌐 Sprawdź: http://localhost:{port}/rss")
        print(f"📡 PID: {process.pid}")
        
    except Exception as e:
        print(f"❌ Błąd uruchamiania serwera RSS: {e}")

def handle_autostart_on(args):
    """Włącz auto-start Mova"""
    if not ConfigManager:
        print("❌ Moduł konfiguracji niedostępny")
        sys.exit(1)
    
    print("🔄 Włączanie auto-start Mova...")
    
    # Utwórz plik usługi systemd
    service_content = f"""[Unit]
Description=Mova System Monitor
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={os.path.dirname(os.path.abspath(__file__))}
ExecStart={sys.executable} {os.path.abspath(__file__)} health
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = '/etc/systemd/system/mova.service'
    
    try:
        # Zapisz plik usługi (wymaga sudo)
        temp_file = '/tmp/mova.service'
        with open(temp_file, 'w') as f:
            f.write(service_content)
        
        # Przenieś plik i włącz usługę
        subprocess.run(['sudo', 'cp', temp_file, service_file], check=True)
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        subprocess.run(['sudo', 'systemctl', 'enable', 'mova.service'], check=True)
        
        # Zaktualizuj konfigurację
        config_manager = ConfigManager()
        config_manager.set_auto_start(True)
        
        print("✅ Auto-start Mova został włączony")
        print("💡 Usługa zostanie uruchomiona przy następnym starcie systemu")
        print("🔧 Aby uruchomić teraz: sudo systemctl start mova")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd konfiguracji systemd: {e}")
        print("💡 Upewnij się, że masz uprawnienia sudo")
    except Exception as e:
        print(f"❌ Błąd: {e}")

def handle_autostart_off(args):
    """Wyłącz auto-start Mova"""
    if not ConfigManager:
        print("❌ Moduł konfiguracji niedostępny")
        sys.exit(1)
    
    print("🔄 Wyłączanie auto-start Mova...")
    
    try:
        # Wyłącz i usuń usługę systemd
        subprocess.run(['sudo', 'systemctl', 'stop', 'mova.service'], check=False)
        subprocess.run(['sudo', 'systemctl', 'disable', 'mova.service'], check=False)
        subprocess.run(['sudo', 'rm', '-f', '/etc/systemd/system/mova.service'], check=False)
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        
        # Zaktualizuj konfigurację
        config_manager = ConfigManager()
        config_manager.set_auto_start(False)
        
        print("✅ Auto-start Mova został wyłączony")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd konfiguracji systemd: {e}")
    except Exception as e:
        print(f"❌ Błąd: {e}")

def handle_talk_command(args):
    """Pełna obsługa interfejsu głosowego z Whisper, SpeechRecognition i TTS"""
    
    # Check if voice interface is available
    if VoiceInterface is None:
        print("❌ Moduł interfejsu głosowego nie jest dostępny")
        print("🔧 Uruchom 'make install' aby zainstalować zależności głosowe")
        return
    
    # Display language information
    language_names = {
        'pl': 'Polski',
        'en': 'English', 
        'de': 'Deutsch'
    }
    
    print(f"🎤 Uruchamianie interfejsu głosowego: {args.language.upper()}")
    print(f"🗣️ Język: {language_names.get(args.language, args.language)}")
    
    # Check voice dependencies
    deps_ok, deps_msg = check_voice_dependencies()
    if not deps_ok:
        print(f"❌ {deps_msg}")
        print("🔧 Zainstaluj zależności:")
        print("   pip install openai-whisper SpeechRecognition pyttsx3 pyaudio")
        print("💡 Na Ubuntu/Debian możesz potrzebować: sudo apt-get install portaudio19-dev")
        return
    
    # Display mode information
    if args.listen_only:
        print("👂 Tryb: tylko nasłuchiwanie (bez odpowiedzi głosowych)")
    elif args.text_only:
        print("📝 Tryb: tylko odpowiedzi tekstowe")
    elif args.continuous:
        print("🔄 Tryb: ciągłe nasłuchiwanie z wykrywaniem słów-kluczy")
    else:
        print("🗣️ Tryb: pełna interakcja głosowa")
    
    try:
        # Create and start voice interface
        print("🚀 Inicjalizacja interfejsu głosowego...")
        
        voice_interface = VoiceInterface(
            language=args.language,
            server=getattr(args, 'server', DEFAULT_SERVER)
        )
        
        # Start voice session with specified mode
        success = voice_interface.start_session(
            listen_only=args.listen_only,
            text_only=args.text_only,
            continuous=args.continuous,
            debug_tts=args.debug_tts
        )
        
        if success:
            print("✅ Sesja głosowa zakończona pomyślnie")
        else:
            print("❌ Sesja głosowa zakończona z błędami")
    
    except KeyboardInterrupt:
        print("\n👋 Interfejs głosowy przerwany przez użytkownika")
    except Exception as e:
        print(f"❌ Błąd interfejsu głosowego: {e}")
        print("💡 Sprawdź czy mikrofon jest podłączony i dostępny")

# ===== SECURITY COMMAND HANDLERS =====

def handle_acl_command(args):
    """Handle ACL (Access Control List) management commands"""
    if SecurityManager is None:
        print("❌ Moduł SecurityManager nie jest dostępny")
        print("🔧 Uruchom 'make install' aby zainstalować zależności")
        return
    
    try:
        security_manager = SecurityManager()
        
        if args.acl_action == 'list':
            rules = security_manager.list_acl_rules()
            if not rules:
                print("📋 Brak zdefiniowanych reguł ACL")
                return
                
            print(f"🔐 Lista reguł ACL ({len(rules)} reguł):")
            print("-" * 80)
            
            for rule in sorted(rules, key=lambda r: r.priority):
                status = "✅" if not rule.expires_at or datetime.fromisoformat(rule.expires_at) > datetime.now() else "⏰"
                print(f"{status} {rule.id[:8]}... | {rule.name:<20} | {rule.action.value.upper():<10} | P:{rule.priority}")
                
                if args.detailed:
                    print(f"   📍 Źródło: {rule.source_pattern}")
                    print(f"   🎯 Zasób: {rule.target_resource}")
                    if rule.description:
                        print(f"   📝 Opis: {rule.description}")
                    if rule.expires_at:
                        expires = datetime.fromisoformat(rule.expires_at)
                        print(f"   ⏰ Wygasa: {expires.strftime('%Y-%m-%d %H:%M')}")
                    print()
        
        elif args.acl_action == 'add':
            rule_id = str(uuid.uuid4())
            
            # Parse expiration date if provided
            expires_at = None
            if args.expires:
                try:
                    if len(args.expires) == 10:  # YYYY-MM-DD
                        expires_at = datetime.strptime(args.expires, '%Y-%m-%d').isoformat()
                    else:  # YYYY-MM-DD HH:MM
                        expires_at = datetime.strptime(args.expires, '%Y-%m-%d %H:%M').isoformat()
                except ValueError:
                    print("❌ Nieprawidłowy format daty. Użyj: YYYY-MM-DD lub YYYY-MM-DD HH:MM")
                    return
            
            rule = ACLRule(
                id=rule_id,
                name=args.name,
                source_pattern=args.source_pattern,
                target_resource=args.target_resource,
                action=AccessAction(args.action),
                priority=args.priority,
                expires_at=expires_at,
                description=args.description or ""
            )
            
            if security_manager.add_acl_rule(rule):
                print(f"✅ Reguła ACL '{args.name}' została dodana")
                print(f"🆔 ID: {rule_id}")
                print(f"📍 Źródło: {args.source_pattern}")
                print(f"🎯 Zasób: {args.target_resource}")
                print(f"🚦 Akcja: {args.action.upper()}")
                print(f"📊 Priorytet: {args.priority}")
            else:
                print("❌ Błąd podczas dodawania reguły ACL")
        
        elif args.acl_action == 'remove':
            if security_manager.remove_acl_rule(args.rule_id):
                print(f"✅ Reguła ACL '{args.rule_id}' została usunięta")
            else:
                print(f"❌ Nie znaleziono reguły o ID: {args.rule_id}")
        
        elif args.acl_action == 'test':
            allowed, reason = security_manager.validate_access(args.source, args.resource, args.instance)
            
            status_icon = "✅" if allowed else "❌"
            status_text = "DOZWOLONY" if allowed else "ODRZUCONY"
            
            print(f"🧪 Test dostępu ACL:")
            print(f"📍 Źródło: {args.source}")
            print(f"🎯 Zasób: {args.resource}")
            if args.instance:
                print(f"🖥️ Instancja: {args.instance}")
            print(f"{status_icon} Status: {status_text}")
            print(f"💡 Powód: {reason}")
        
        elif args.acl_action == 'status':
            status = security_manager.get_security_status()
            print("🔐 Status systemu ACL:")
            print(f"📊 Liczba reguł: {status['acl_rules_count']}")
            if status['expired_rules'] > 0:
                print(f"⏰ Wygasłe reguły: {status['expired_rules']}")
            
            if status['last_audit_entries']:
                print("\n📋 Ostatnie wpisy audytu:")
                for entry in status['last_audit_entries'][-3:]:
                    print(f"   {entry.strip()}")
    
    except Exception as e:
        print(f"❌ Błąd podczas zarządzania ACL: {e}")

def handle_cors_command(args):
    """Handle CORS (Cross-Origin Resource Sharing) management commands"""
    if SecurityManager is None:
        print("❌ Moduł SecurityManager nie jest dostępny")
        print("🔧 Uruchom 'make install' aby zainstalować zależności")
        return
    
    try:
        security_manager = SecurityManager()
        
        if args.cors_action == 'list':
            policies = security_manager.list_cors_policies()
            if not policies:
                print("📋 Brak zdefiniowanych polityk CORS")
                return
                
            print(f"🌐 Lista polityk CORS ({len(policies)} polityk):")
            print("-" * 80)
            
            for policy in policies:
                print(f"🆔 {policy.id[:8]}... | {policy.name:<25} | Origins: {len(policy.allowed_origins)}")
                
                if args.detailed:
                    print(f"   🌍 Dozwolone origins: {', '.join(policy.allowed_origins)}")
                    print(f"   📡 Metody: {', '.join(policy.allowed_methods)}")
                    print(f"   📋 Nagłówki: {', '.join(policy.allowed_headers)}")
                    print(f"   🔐 Credentials: {'Tak' if policy.allow_credentials else 'Nie'}")
                    print(f"   ⏱️ Max Age: {policy.max_age}s")
                    if policy.description:
                        print(f"   📝 Opis: {policy.description}")
                    print()
        
        elif args.cors_action == 'add':
            policy_id = str(uuid.uuid4())
            
            policy = CORSPolicy(
                id=policy_id,
                name=args.name,
                allowed_origins=args.origins,
                allowed_methods=args.methods,
                allowed_headers=args.headers,
                allow_credentials=args.credentials,
                max_age=args.max_age,
                expose_headers=args.expose_headers or [],
                description=args.description or ""
            )
            
            if security_manager.add_cors_policy(policy):
                print(f"✅ Polityka CORS '{args.name}' została dodana")
                print(f"🆔 ID: {policy_id}")
                print(f"🌍 Origins: {', '.join(args.origins)}")
                print(f"📡 Metody: {', '.join(args.methods)}")
                print(f"🔐 Credentials: {'Tak' if args.credentials else 'Nie'}")
            else:
                print("❌ Błąd podczas dodawania polityki CORS")
        
        elif args.cors_action == 'remove':
            if security_manager.remove_cors_policy(args.policy_id):
                print(f"✅ Polityka CORS '{args.policy_id}' została usunięta")
            else:
                print(f"❌ Nie znaleziono polityki o ID: {args.policy_id}")
        
        elif args.cors_action == 'test':
            headers = security_manager.get_cors_headers(args.origin, args.instance)
            
            print(f"🧪 Test nagłówków CORS:")
            print(f"🌍 Origin: {args.origin}")
            if args.instance:
                print(f"🖥️ Instancja: {args.instance}")
            
            if headers:
                print("✅ Wygenerowane nagłówki CORS:")
                for header, value in headers.items():
                    print(f"   {header}: {value}")
            else:
                print("❌ Brak odpowiednich polityk CORS dla tego origin")
    
    except Exception as e:
        print(f"❌ Błąd podczas zarządzania CORS: {e}")

def handle_instance_command(args):
    """Handle instance management commands"""
    if SecurityManager is None:
        print("❌ Moduł SecurityManager nie jest dostępny")
        print("🔧 Uruchom 'make install' aby zainstalować zależności")
        return
    
    try:
        security_manager = SecurityManager()
        
        if args.instance_action == 'register':
            instance = InstanceProfile(
                instance_id=args.instance_id,
                instance_type=args.instance_type,
                security_level=SecurityLevel(args.security_level),
                trusted_instances=set(args.trusted or []),
                blocked_instances=set(args.blocked or []),
                acl_rules=[],
                cors_policies=[],
                api_keys={},
                rate_limits={}
            )
            
            if security_manager.register_instance(instance):
                print(f"✅ Instancja '{args.instance_id}' została zarejestrowana")
                print(f"🏷️ Typ: {args.instance_type}")
                print(f"🔒 Poziom bezpieczeństwa: {args.security_level}")
                if args.trusted:
                    print(f"✅ Zaufane instancje: {', '.join(args.trusted)}")
                if args.blocked:
                    print(f"❌ Zablokowane instancje: {', '.join(args.blocked)}")
            else:
                print("❌ Błąd podczas rejestracji instancji")
        
        elif args.instance_action == 'list':
            instances = security_manager.list_instances()
            if not instances:
                print("📋 Brak zarejestrowanych instancji")
                return
                
            print(f"🖥️ Lista instancji Mova ({len(instances)} instancji):")
            print("-" * 80)
            
            for instance in instances:
                level_icon = {"open": "🔓", "restricted": "🔒", "secure": "🛡️", "isolated": "🏰"}
                icon = level_icon.get(instance.security_level.value, "🔒")
                
                print(f"{icon} {instance.instance_id} | {instance.instance_type:<10} | {instance.security_level.value.upper()}")
                
                if args.detailed:
                    print(f"   📅 Utworzono: {instance.created_at[:19]}")
                    print(f"   🔐 Reguły ACL: {len(instance.acl_rules)}")
                    print(f"   🌐 Polityki CORS: {len(instance.cors_policies)}")
                    if instance.trusted_instances:
                        print(f"   ✅ Zaufane: {', '.join(instance.trusted_instances)}")
                    if instance.blocked_instances:
                        print(f"   ❌ Zablokowane: {', '.join(instance.blocked_instances)}")
                    print()
        
        elif args.instance_action == 'unregister':
            if security_manager.unregister_instance(args.instance_id):
                print(f"✅ Instancja '{args.instance_id}' została wyrejestrowana")
            else:
                print(f"❌ Nie znaleziono instancji o ID: {args.instance_id}")
    
    except Exception as e:
        print(f"❌ Błąd podczas zarządzania instancjami: {e}")

def handle_security_command(args):
    """Handle general security management commands"""
    if SecurityManager is None:
        print("❌ Moduł SecurityManager nie jest dostępny")
        print("🔧 Uruchom 'make install' aby zainstalować zależności")
        return
    
    try:
        security_manager = SecurityManager()
        
        if args.security_action == 'status':
            status = security_manager.get_security_status()
            
            print("🛡️ Status systemu bezpieczeństwa Mova:")
            print("=" * 50)
            print(f"🔐 Reguły ACL: {status['acl_rules_count']}")
            print(f"🌐 Polityki CORS: {status['cors_policies_count']}")
            print(f"🖥️ Instancje: {status['instances_count']}")
            
            if status['expired_rules'] > 0:
                print(f"⏰ Wygasłe reguły: {status['expired_rules']}")
            
            print("\n📊 Rozkład poziomów bezpieczeństwa instancji:")
            for level, count in status['security_levels'].items():
                level_icons = {"open": "🔓", "restricted": "🔒", "secure": "🛡️", "isolated": "🏰"}
                icon = level_icons.get(level, "🔒")
                print(f"   {icon} {level.capitalize()}: {count}")
            
            if status['last_audit_entries']:
                print("\n📋 Ostatnie zdarzenia bezpieczeństwa:")
                for entry in status['last_audit_entries'][-5:]:
                    print(f"   {entry.strip()}")
        
        elif args.security_action == 'audit':
            if security_manager.audit_file.exists():
                with open(security_manager.audit_file, 'r') as f:
                    lines = f.readlines()
                
                print(f"📋 Log audytu bezpieczeństwa (ostatnie {args.last} wpisów):")
                print("-" * 80)
                
                for line in lines[-args.last:]:
                    print(line.strip())
            else:
                print("📋 Brak pliku audytu bezpieczeństwa")
        
        elif args.security_action == 'init':
            from security_manager import DEFAULT_SECURITY_PROFILES
            
            profile = DEFAULT_SECURITY_PROFILES.get(args.profile)
            if not profile:
                print(f"❌ Nieznany profil bezpieczeństwa: {args.profile}")
                return
            
            print(f"🚀 Inicjalizacja profilu bezpieczeństwa: {args.profile}")
            
            # Add default ACL rules
            for rule_data in profile['default_acl_rules']:
                rule_data['id'] = str(uuid.uuid4())
                rule = ACLRule(**rule_data)
                security_manager.add_acl_rule(rule)
                print(f"   ✅ Dodano regułę ACL: {rule.name}")
            
            # Add default CORS policy
            cors_data = profile['default_cors_policy'].copy()
            cors_data['id'] = str(uuid.uuid4())
            cors_policy = CORSPolicy(**cors_data)
            security_manager.set_cors_policy(cors_policy)
            print(f"   ✅ Dodano politykę CORS: {cors_policy.name}")
            
            print(f"🎉 Profil bezpieczeństwa '{args.profile}' został pomyślnie zainicjalizowany!")
        
        else:
            print(f"❌ Nieznana akcja bezpieczeństwa: {args.security_action}")
    
    except Exception as e:
        print(f"❌ Błąd w zarządzaniu bezpieczeństwem: {str(e)}")


def format_log_entry(log, format_type='compact'):
    """
    Formatuj wpis logu zgodnie z wybranym stylem
    """
    timestamp = log.get('timestamp', '')
    level = log.get('level', 'info').upper()
    service = log.get('service', 'unknown')
    message = log.get('message', '')
    
    if format_type == 'compact':
        # Format: 📊 [14:10:21] ERROR | service | message
        icon = {'INFO': '📊', 'WARNING': '⚠️', 'ERROR': '❌'}.get(level, '📝')
        time_part = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp[:8]
        return f"{icon} [{time_part}] {level:7} | {service:10} | {message}"
        
    elif format_type == 'detailed':
        # Szczegółowy format z pełną datą
        return f"""
🕐 Czas: {timestamp}
📊 Poziom: {level}
🏷️  Serwis: {service}
💬 Wiadomość: {message}
{'-' * 60}"""
        
    elif format_type == 'json':
        # Format JSON
        return json.dumps(log, indent=2, ensure_ascii=False)
        
    elif format_type == 'ndjson':
        # Newline-Delimited JSON (NDJSON) - każdy log jako osobna linia JSON
        return json.dumps(log, ensure_ascii=False, separators=(',', ':'))
        
    return str(log)

def handle_audio_command(args):
    """Obsługuje komendy zarządzania urządzeniami audio"""
    if not VoiceInterface:
        print("❌ Moduł głosowy nie jest dostępny")
        print("🔧 Uruchom 'make install' aby zainstalować zależności")
        return
    
    try:
        # Utwórz tymczasową instancję VoiceInterface dla zarządzania urządzeniami
        audio_manager = VoiceInterface()
        
        if args.audio_action == 'list':
            audio_manager.list_all_audio_devices(detailed=args.detailed, test=args.test)
        elif args.audio_action == 'get':
            # NOWA KOMENDA: mova audio get [--detailed]
            audio_manager.get_current_audio_devices(detailed=getattr(args, 'detailed', False))
        elif args.audio_action == 'set':
            if args.audio_set_action == 'auto':
                audio_manager.set_auto_audio_devices(test=getattr(args, 'test', False), save=getattr(args, 'save', False))
            else:
                print(f"❌ Nieznana akcja audio set: {args.audio_set_action}")
                print("💡 Dostępne akcje: auto")
        else:
            print(f"❌ Nieznana akcja audio: {args.audio_action}")
            print("💡 Dostępne akcje: list, get, set")
    except Exception as e:
        print(f"❌ Błąd zarządzania urządzeniami audio: {e}")

def handle_speaker_command(args):
    """Obsługuje komendy zarządzania głośnikami/wyjściem TTS"""
    if not VoiceInterface:
        print("❌ Moduł głosowy nie jest dostępny")
        print("🔧 Uruchom 'make install' aby zainstalować zależności")
        return
    
    try:
        # Utwórz tymczasową instancję VoiceInterface dla zarządzania urządzeniami
        audio_manager = VoiceInterface()
        
        if args.speaker_action == 'list':
            audio_manager.list_speaker_devices(test=getattr(args, 'test', False), current=getattr(args, 'current', False))
        elif args.speaker_action == 'set':
            if args.device_selector.lower() == 'auto':
                audio_manager.set_auto_speaker_device(test=getattr(args, 'test', False), save=getattr(args, 'save', False))
            else:
                try:
                    device_index = int(args.device_selector)
                    audio_manager.set_speaker_device(device_index, test=getattr(args, 'test', False), save=getattr(args, 'save', False))
                except ValueError:
                    print(f"❌ Nieprawidłowy selektor urządzenia: {args.device_selector}")
                    print("💡 Użyj numeru urządzenia (np. 1, 2, 3) lub 'auto' dla automatycznego wyboru")
        else:
            print(f"❌ Nieznana akcja speaker: {args.speaker_action}")
            print("💡 Dostępne akcje: list, set")
    except Exception as e:
        print(f"❌ Błąd zarządzania głośnikami: {e}")

def handle_mic_command(args):
    """Obsługuje komendy zarządzania mikrofonami/wejściem STT"""
    if not VoiceInterface:
        print("❌ Moduł głosowy nie jest dostępny")
        print("🔧 Uruchom 'make install' aby zainstalować zależności")
        return
    
    try:
        # Utwórz tymczasową instancję VoiceInterface dla zarządzania urządzeniami
        audio_manager = VoiceInterface()
        
        if args.mic_action == 'list':
            audio_manager.list_mic_devices(test=getattr(args, 'test', False), current=getattr(args, 'current', False))
        elif args.mic_action == 'set':
            if args.device_selector.lower() == 'auto':
                audio_manager.set_auto_mic_device(test=getattr(args, 'test', False), save=getattr(args, 'save', False))
            else:
                try:
                    device_index = int(args.device_selector)
                    audio_manager.set_mic_device(device_index, test=getattr(args, 'test', False), save=getattr(args, 'save', False))
                except ValueError:
                    print(f"❌ Nieprawidłowy selektor urządzenia: {args.device_selector}")
                    print("💡 Użyj numeru urządzenia (np. 1, 2, 3) lub 'auto' dla automatycznego wyboru")
        else:
            print(f"❌ Nieznana akcja mic: {args.mic_action}")
            print("💡 Dostępne akcje: list, set")
    except Exception as e:
        print(f"❌ Błąd zarządzania mikrofonami: {e}")

def read_logs_advanced(args):
    """
    Zaawansowane czytanie logów z filtrowaniem czasowym i trybem watch
    Przykłady użycia:
    - mova read error --last 10m
    - mova read info --last 1h --service "web-server"
    - mova read all --watch --interval 3
    """
    print(f"📖 Czytanie logów: poziom '{args.level}'")
    
    # Parsuj filtr czasowy
    time_filter_seconds = None
    if args.last:
        time_filter_seconds = parse_time_duration(args.last)
        if time_filter_seconds is None:
            print(f"❌ Nieprawidłowy format czasu: {args.last}")
            print("💡 Użyj formatu jak: 5m, 1h, 30s, 2d")
            return
        print(f"⏰ Filtr czasowy: ostatnie {args.last} ({time_filter_seconds} sekund)")
    
    if args.service:
        print(f"🏷️  Filtr serwisu: {args.service}")
    
    if args.watch:
        print(f"👁️  Tryb ciągłego monitorowania (interwał: {args.interval}s)")
        print("💡 Naciśnij Ctrl+C aby zatrzymać")
    
    # Inicjalizuj TTS jeśli włączone
    tts_interface = None
    tts_message_cache = {}  # Cache dla inteligentnej deduplikacji wiadomości TTS
    tts_cache_timeout = 300  # 5 minut - czas po którym wiadomość może być powtórzona
    
    if args.tts:
        print("🎤 Inicjalizacja inteligentnego TTS dla odczytu logów...")
        try:
            if VoiceInterface:
                # Użyj trybu tts_only=True aby uniknąć interaktywnej selekcji urządzeń
                tts_interface = VoiceInterface(language='en', tts_only=True)
                print("✅ TTS zainicjalizowane - logi będą odczytywane głosowo (z deduplikacją)")
                print("🧠 Inteligentna deduplikacja: powtórzenia będą pomijane przez 5 minut")
            else:
                print("❌ TTS niedostępne - moduł głosowy nie załadowany")
                print("🔧 Uruchom 'make install' aby zainstalować zależności")
                args.tts = False  # Wyłącz TTS jeśli nie dostępne
        except Exception as e:
            print(f"❌ Błąd inicjalizacji TTS: {e}")
            args.tts = False
    
    def fetch_and_display_logs(since_timestamp=None):
        try:
            # Przygotuj parametry zapytania
            params = {
                'limit': args.limit
            }
            
            if args.level != 'all':
                params['level'] = args.level
                
            if args.service:
                params['service'] = args.service
                
            # Dla trybu watch z TTS, nie używaj since API (nie obsługiwane), filtruj po pobraniu
            if time_filter_seconds:
                params['since_seconds'] = time_filter_seconds
            
            # DEBUG: Wyloguj parametry zapytania
            if args.watch and args.tts and since_timestamp:
                print(f"🕒 Szukam nowych logów od: {since_timestamp} (filtrowanie po stronie klienta)")
            
            # Pobierz logi z serwera
            response = requests.get(f"{args.server}/api/logs", params=params, timeout=10)
            response.raise_for_status()
            
            logs_data = response.json()
            all_logs = logs_data.get('logs', [])
            
            # Filtruj logi po stronie klienta dla trybu watch + TTS
            if since_timestamp and args.watch and args.tts:
                logs = []
                for log in all_logs:
                    log_timestamp = log.get('timestamp', '')
                    if log_timestamp > since_timestamp:
                        logs.append(log)
                print(f"🔍 Odfiltrowano {len(logs)} nowych logów z {len(all_logs)} wszystkich")
            else:
                logs = all_logs
            
            if not logs:
                if not args.watch:
                    print("📭 Brak logów spełniających kryteria")
                return len(logs), None
            
            # Zapamiętaj timestamp najnowszego logu dla następnej iteracji
            latest_timestamp = None
            if logs and args.watch and args.tts:
                # Znajdź najnowszy timestamp ze wszystkich logów (nie tylko nowych)
                for log in all_logs:
                    log_timestamp = log.get('timestamp')
                    if log_timestamp and (not latest_timestamp or log_timestamp > latest_timestamp):
                        latest_timestamp = log_timestamp
            
            # Wyświetl logi w wybranym formacie
            if args.format == 'json':
                print(json.dumps(logs, indent=2, ensure_ascii=False))
                # TTS dla formatu JSON - odczytaj podstawowe info
                if args.tts and tts_interface:
                    summary = f"Znaleziono {len(logs)} wpisów logów poziom {args.level}"
                    if args.service:
                        summary += f" dla serwisu {args.service}"
                    tts_interface.tts.speak(summary)
            elif args.format == 'ndjson':
                # NDJSON: każdy log jako osobna linia JSON (newline-delimited)
                for log in logs:
                    print(json.dumps(log, ensure_ascii=False, separators=(',', ':')))
                # TTS dla formatu NDJSON - odczytaj każdy log osobno
                if args.tts and tts_interface:
                    for log in logs:
                        tts_text = prepare_log_for_tts(log)
                        if should_speak_message(tts_text, tts_message_cache, tts_cache_timeout):
                            tts_interface.tts.speak(tts_text)
                            time.sleep(0.5)
            else:
                for log in logs:
                    formatted_log = format_log_entry(log, args.format)
                    print(formatted_log)
                    
                    # TTS - odczytaj logi głosowo z inteligentną deduplikacją
                    if args.tts and tts_interface:
                        try:
                            # Przygotuj tekst do odczytu TTS
                            tts_text = prepare_log_for_tts(log)
                            if tts_text:
                                # Sprawdź czy nie jest duplikatem
                                if should_speak_message(tts_text, tts_message_cache, tts_cache_timeout):
                                    print(f"🗣️  TTS: {tts_text[:50]}{'...' if len(tts_text) > 50 else ''}")
                                    tts_interface.tts.speak(tts_text)
                                    # Krótka pauza między logami
                                    import time
                                    time.sleep(0.5)
                                else:
                                    print(f"🔇 TTS: Pomijam duplikat (już odczytane w ciągu ostatnich 5 min)")
                        except Exception as e:
                            print(f"❌ Błąd TTS: {e}")
            
            return len(logs), latest_timestamp
            
        except requests.exceptions.RequestException as e:
            if not args.watch:
                print(f"❌ Błąd połączenia z serwerem: {str(e)}")
            return 0, None
        except Exception as e:
            if not args.watch:
                print(f"❌ Błąd podczas pobierania logów: {str(e)}")
            return 0, None
    
    try:
        if args.watch:
            # Tryb ciągłego monitorowania z inteligentnym śledzeniem nowych logów
            last_count = 0
            last_timestamp = None
            first_run = True
            
            while True:
                # Wyczyść ekran (opcjonalnie)
                if hasattr(os, 'system'):
                    os.system('clear' if os.name == 'posix' else 'cls')
                
                print(f"📖 Mova Log Reader - Poziom: {args.level} | Tryb: WATCH")
                print(f"⏰ Ostatnia aktualizacja: {datetime.now().strftime('%H:%M:%S')}")
                if args.service:
                    print(f"🏷️  Serwis: {args.service}")
                if args.last:
                    print(f"⏳ Ostatnie: {args.last}")
                print("-" * 80)
                
                # Specjalna logika dla TTS - przy pierwszym uruchomieniu pomijamy stare logi
                if args.tts and first_run:
                    print("🎤 TTS Watch Mode: Pomijam stare logi, czekam na nowe...")
                    # Ustaw timestamp na teraz żeby następne wywołania czytały tylko nowe logi
                    last_timestamp = datetime.now().isoformat()
                    first_run = False
                    current_count = 0
                else:
                    current_count, new_timestamp = fetch_and_display_logs(since_timestamp=last_timestamp if not first_run else None)
                    if new_timestamp:
                        last_timestamp = new_timestamp
                    if first_run:
                        first_run = False
                
                if current_count != last_count:
                    print(f"\n📊 Znaleziono {current_count} logów")
                    last_count = current_count
                
                print(f"\n🔄 Następna aktualizacja za {args.interval}s... (Ctrl+C aby zatrzymać)")
                time.sleep(args.interval)
        else:
            # Jednorazowe pobranie
            count, _ = fetch_and_display_logs()
            print(f"\n📊 Wyświetlono {count} logów")
            
    except KeyboardInterrupt:
        print(f"\n👋 Zatrzymano czytanie logów")

def prepare_log_for_tts(log_entry):
    """
    Przygotuj wpis logu do odczytu przez TTS - wyciągnij najważniejsze informacje
    """
    try:
        # Podstawowe pola z logu
        level = log_entry.get('level', 'info').upper()
        message = log_entry.get('message', '').strip()
        service = log_entry.get('service', '')
        timestamp = log_entry.get('timestamp', '')
        
        # Skróć i oczyść wiadomość dla TTS
        if len(message) > 200:
            message = message[:200] + "..."
        
        # Usuń znaki specjalne i formatowanie które mogą przeszkadzać TTS
        message = message.replace('\n', ' ').replace('\t', ' ')
        message = ' '.join(message.split())  # Normalize whitespace
        
        # Buduj tekst TTS
        tts_parts = []
        
        # Dodaj poziom logu
        if level in ['ERROR', 'CRITICAL']:
            tts_parts.append(f"Alert {level}")
        elif level == 'WARNING':
            tts_parts.append("Warning")
        elif level == 'INFO':
            tts_parts.append("Info")
        else:
            tts_parts.append(f"Log {level}")
        
        # Dodaj serwis jeśli dostępny
        if service:
            tts_parts.append(f"from {service}")
        
        # Dodaj główną wiadomość
        if message:
            tts_parts.append(f": {message}")
        
        return ' '.join(tts_parts)
        
    except Exception as e:
        # Fallback - podstawowa wiadomość
        return f"Log entry: {log_entry.get('message', 'No message')}"

def should_speak_message(tts_text, message_cache, cache_timeout):
    """
    Sprawdź czy wiadomość powinna być odczytana przez TTS (inteligentna deduplikacja)
    """
    try:
        import hashlib
        
        # Utwórz hash wiadomości dla identyfikacji duplikatów
        message_hash = hashlib.md5(tts_text.encode('utf-8')).hexdigest()
        current_time = time.time()
        
        # Sprawdź czy wiadomość była już odczytana niedawno
        if message_hash in message_cache:
            last_spoken_time = message_cache[message_hash]
            if current_time - last_spoken_time < cache_timeout:
                # Wiadomość została odczytana w ciągu cache_timeout sekund
                return False
        
        # Oznacz wiadomość jako odczytaną
        message_cache[message_hash] = current_time
        
        # Wyczyść stare wpisy z cache (starsze niż cache_timeout)
        expired_hashes = [h for h, t in message_cache.items() if current_time - t > cache_timeout]
        for hash_to_remove in expired_hashes:
            del message_cache[hash_to_remove]
        
        return True
        
    except Exception as e:
        # W przypadku błędu, pozwól na odczytanie wiadomości
        print(f"⚠️ Błąd deduplikacji TTS: {e}")
        return True
        
if __name__ == '__main__':
    main()
