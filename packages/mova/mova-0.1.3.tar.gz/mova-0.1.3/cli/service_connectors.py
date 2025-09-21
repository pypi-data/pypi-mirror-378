#!/usr/bin/env python3

"""
Mova Service Connectors - integracje z różnymi usługami systemowymi
"""

import subprocess
import json
import os
import socket
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import psutil
except ImportError:
    psutil = None
    print("⚠️ psutil nie jest zainstalowane. Instaluj: pip install psutil")

try:
    import docker
except ImportError:
    docker = None
    print("⚠️ docker nie jest zainstalowany. Instaluj: pip install docker")


class ServiceConnector(ABC):
    """Abstrakcyjna klasa bazowa dla konektorów usług"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__.replace('Connector', '').lower()
    
    @abstractmethod
    def is_available(self) -> bool:
        """Sprawdź czy usługa jest dostępna"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Pobierz status usługi"""
        pass
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Pobierz szczegółowe informacje o usłudze"""
        pass
    
    @abstractmethod
    def start_monitoring(self) -> bool:
        """Rozpocznij monitoring usługi"""
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> bool:
        """Zatrzymaj monitoring usługi"""
        pass


class DockerConnector(ServiceConnector):
    """Konektor do Docker"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        self._init_docker_client()
    
    def _init_docker_client(self):
        """Inicjalizuj klienta Docker"""
        try:
            socket_path = self.config.get('socket_path', '/var/run/docker.sock')
            if os.path.exists(socket_path):
                self.client = docker.from_env()
            else:
                print(f"⚠️ Socket Docker nie znaleziony: {socket_path}")
        except Exception as e:
            print(f"⚠️ Błąd inicjalizacji Docker: {e}")
    
    def is_available(self) -> bool:
        """Sprawdź czy Docker jest dostępny"""
        try:
            if self.client:
                self.client.ping()
                return True
        except Exception:
            pass
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Pobierz status Docker"""
        if not self.is_available():
            return {
                'available': False,
                'error': 'Docker niedostępny',
                'containers': 0,
                'images': 0
            }
        
        try:
            containers = self.client.containers.list(all=True)
            images = self.client.images.list()
            running_containers = [c for c in containers if c.status == 'running']
            
            return {
                'available': True,
                'containers': len(containers),
                'running_containers': len(running_containers),
                'images': len(images),
                'version': self.client.version()['Version']
            }
        except Exception as e:
            return {
                'available': False,
                'error': str(e),
                'containers': 0,
                'images': 0
            }
    
    def get_info(self) -> Dict[str, Any]:
        """Pobierz szczegółowe informacje o Docker"""
        if not self.is_available():
            return {'error': 'Docker niedostępny'}
        
        try:
            info = self.client.info()
            containers = self.client.containers.list(all=True)
            images = self.client.images.list()
            
            # Szczegóły kontenerów
            container_details = []
            for container in containers:
                container_details.append({
                    'id': container.short_id,
                    'name': container.name,
                    'image': container.image.tags[0] if container.image.tags else 'unknown',
                    'status': container.status,
                    'created': container.attrs['Created'],
                    'ports': container.ports if hasattr(container, 'ports') else {}
                })
            
            # Szczegóły obrazów
            image_details = []
            for image in images:
                image_details.append({
                    'id': image.short_id,
                    'tags': image.tags,
                    'size': image.attrs.get('Size', 0),
                    'created': image.attrs.get('Created', '')
                })
            
            return {
                'docker_info': {
                    'version': info.get('ServerVersion', 'unknown'),
                    'containers': info.get('Containers', 0),
                    'images': info.get('Images', 0),
                    'memory_total': info.get('MemTotal', 0),
                    'cpus': info.get('NCPU', 0)
                },
                'containers': container_details,
                'images': image_details,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def start_monitoring(self) -> bool:
        """Rozpocznij monitoring Docker"""
        if not self.is_available():
            return False
        
        # Tu można dodać monitoring events
        # self.client.events() dla continuous monitoring
        return True
    
    def stop_monitoring(self) -> bool:
        """Zatrzymaj monitoring Docker"""
        return True
    
    def get_container_logs(self, container_id: str, lines: int = 100) -> str:
        """Pobierz logi kontenera"""
        if not self.is_available():
            return "Docker niedostępny"
        
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=lines, timestamps=True)
            return logs.decode('utf-8')
        except Exception as e:
            return f"Błąd pobierania logów: {e}"


class SystemdConnector(ServiceConnector):
    """Konektor do systemd"""
    
    def is_available(self) -> bool:
        """Sprawdź czy systemd jest dostępny"""
        try:
            result = subprocess.run(['systemctl', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Pobierz status systemd"""
        if not self.is_available():
            return {'available': False, 'error': 'systemd niedostępny'}
        
        try:
            # Pobierz listę wszystkich usług
            result = subprocess.run(['systemctl', 'list-units', '--type=service', '--no-pager', '--no-legend'],
                                  capture_output=True, text=True, timeout=10)
            
            services = []
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 4:
                            services.append({
                                'name': parts[0],
                                'load': parts[1],
                                'active': parts[2],
                                'sub': parts[3]
                            })
            
            return {
                'available': True,
                'total_services': len(services),
                'active_services': len([s for s in services if s.get('active') == 'active']),
                'failed_services': len([s for s in services if s.get('active') == 'failed'])
            }
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
    def get_info(self) -> Dict[str, Any]:
        """Pobierz szczegółowe informacje o systemd"""
        if not self.is_available():
            return {'error': 'systemd niedostępny'}
        
        try:
            # Monitorowane usługi z konfiguracji
            monitor_services = self.config.get('monitor_services', [])
            service_details = []
            
            for service_name in monitor_services:
                try:
                    # Status usługi
                    status_result = subprocess.run(['systemctl', 'status', service_name, '--no-pager'],
                                                 capture_output=True, text=True, timeout=5)
                    
                    # Czy aktywna
                    active_result = subprocess.run(['systemctl', 'is-active', service_name],
                                                 capture_output=True, text=True, timeout=5)
                    
                    # Czy włączona
                    enabled_result = subprocess.run(['systemctl', 'is-enabled', service_name],
                                                  capture_output=True, text=True, timeout=5)
                    
                    service_details.append({
                        'name': service_name,
                        'active': active_result.stdout.strip(),
                        'enabled': enabled_result.stdout.strip(),
                        'status_output': status_result.stdout
                    })
                except Exception as e:
                    service_details.append({
                        'name': service_name,
                        'error': str(e)
                    })
            
            return {
                'monitored_services': service_details,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def start_monitoring(self) -> bool:
        """Rozpocznij monitoring systemd"""
        return self.is_available()
    
    def stop_monitoring(self) -> bool:
        """Zatrzymaj monitoring systemd"""
        return True


class SystemConnector(ServiceConnector):
    """Konektor do informacji systemowych"""
    
    def is_available(self) -> bool:
        """System info zawsze dostępne"""
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Pobierz status systemu"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'available': True,
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
    def get_info(self) -> Dict[str, Any]:
        """Pobierz szczegółowe informacje systemowe"""
        try:
            # Informacje o systemie
            uname = os.uname()
            cpu_info = {
                'count': psutil.cpu_count(),
                'count_logical': psutil.cpu_count(logical=True),
                'percent': psutil.cpu_percent(interval=1, percpu=True),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            }
            
            memory_info = psutil.virtual_memory()._asdict()
            disk_info = psutil.disk_usage('/')._asdict()
            
            # Procesy
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Top 10 procesów według CPU
            top_cpu_processes = sorted(processes, 
                                     key=lambda x: x.get('cpu_percent', 0), 
                                     reverse=True)[:10]
            
            return {
                'system': {
                    'sysname': uname.sysname,
                    'nodename': uname.nodename,
                    'release': uname.release,
                    'version': uname.version,
                    'machine': uname.machine
                },
                'cpu': cpu_info,
                'memory': memory_info,
                'disk': disk_info,
                'top_processes': top_cpu_processes,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def start_monitoring(self) -> bool:
        """Rozpocznij monitoring systemu"""
        return True
    
    def stop_monitoring(self) -> bool:
        """Zatrzymaj monitoring systemu"""
        return True


class ServiceManager:
    """Menedżer wszystkich konektorów usług"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.connectors = {}
        self._init_connectors()
    
    def _init_connectors(self):
        """Inicjalizuj wszystkie konektory"""
        # Docker
        docker_config = self.config_manager.get_service_config('docker')
        self.connectors['docker'] = DockerConnector(docker_config)
        
        # systemd
        systemd_config = self.config_manager.get_service_config('systemd')
        self.connectors['systemd'] = SystemdConnector(systemd_config)
        
        # System info
        self.connectors['system'] = SystemConnector({})
    
    def get_available_services(self) -> List[Dict[str, Any]]:
        """Pobierz listę dostępnych usług"""
        services = []
        
        for name, connector in self.connectors.items():
            is_enabled = self.config_manager.is_service_enabled(name)
            is_available = connector.is_available()
            
            services.append({
                'name': name,
                'enabled': is_enabled,
                'available': is_available,
                'status': connector.get_status() if is_available else {'available': False}
            })
        
        return services
    
    def get_service_info(self, service_name: str) -> Dict[str, Any]:
        """Pobierz szczegółowe informacje o usłudze"""
        if service_name not in self.connectors:
            return {'error': f'Nieznana usługa: {service_name}'}
        
        connector = self.connectors[service_name]
        if not connector.is_available():
            return {'error': f'Usługa {service_name} niedostępna'}
        
        return connector.get_info()
    
    def enable_service(self, service_name: str) -> bool:
        """Włącz monitorowanie usługi"""
        if service_name not in self.connectors:
            return False
        
        connector = self.connectors[service_name]
        if not connector.is_available():
            return False
        
        if connector.start_monitoring():
            self.config_manager.set_service_enabled(service_name, True)
            return True
        
        return False
    
    def disable_service(self, service_name: str) -> bool:
        """Wyłącz monitorowanie usługi"""
        if service_name not in self.connectors:
            return False
        
        connector = self.connectors[service_name]
        if connector.stop_monitoring():
            self.config_manager.set_service_enabled(service_name, False)
            return True
        
        return False
    
    def get_enabled_services_status(self) -> Dict[str, Any]:
        """Pobierz status wszystkich włączonych usług"""
        enabled_services = self.config_manager.get_enabled_services()
        status = {}
        
        for service_name in enabled_services:
            if service_name in self.connectors:
                connector = self.connectors[service_name]
                status[service_name] = connector.get_status()
        
        return status
