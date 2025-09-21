#!/usr/bin/env python3
"""
Mova Security Manager - Access Control Layer (ACL) and CORS Management

This module provides comprehensive security controls for Mova instances including:
- Access Control Lists (ACL) for inter-instance communication
- CORS policies for web-based interactions
- Instance routing and security protocols
- Authentication and authorization mechanisms
"""

import json
import os
import ipaddress
import re
from typing import Dict, List, Optional, Set, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum


class SecurityLevel(Enum):
    """Security levels for Mova instances"""
    OPEN = "open"           # No restrictions
    RESTRICTED = "restricted"  # Basic restrictions
    SECURE = "secure"       # High security
    ISOLATED = "isolated"   # Maximum isolation


class AccessAction(Enum):
    """Access control actions"""
    ALLOW = "allow"
    DENY = "deny"
    LOG = "log"
    CHALLENGE = "challenge"  # Require authentication


@dataclass
class ACLRule:
    """Access Control List rule"""
    id: str
    name: str
    source_pattern: str  # IP, domain, or instance pattern
    target_resource: str  # Resource or endpoint pattern
    action: AccessAction
    priority: int = 100
    expires_at: Optional[str] = None
    created_at: str = None
    description: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class CORSPolicy:
    """CORS policy configuration"""
    id: str
    name: str
    allowed_origins: List[str]
    allowed_methods: List[str]
    allowed_headers: List[str]
    allow_credentials: bool = False
    max_age: int = 3600
    expose_headers: List[str] = None
    created_at: str = None
    description: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.expose_headers is None:
            self.expose_headers = []


@dataclass
class InstanceProfile:
    """Security profile for a Mova instance"""
    instance_id: str
    instance_type: str  # frontend, backend, firmware, mobile, etc.
    security_level: SecurityLevel
    trusted_instances: Set[str]
    blocked_instances: Set[str]
    acl_rules: List[str]  # ACL rule IDs
    cors_policies: List[str]  # CORS policy IDs
    api_keys: Dict[str, str]
    rate_limits: Dict[str, int]
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class SecurityManager:
    """Main security manager for Mova instances"""
    
    def __init__(self, config_dir: str = None):
        """Initialize security manager"""
        if config_dir is None:
            config_dir = os.path.join(os.path.expanduser("~"), ".mova", "security")
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.acl_file = self.config_dir / "acl_rules.json"
        self.cors_file = self.config_dir / "cors_policies.json"
        self.instances_file = self.config_dir / "instances.json"
        self.audit_file = self.config_dir / "security_audit.log"
        
        # Load existing configurations
        self.acl_rules: Dict[str, ACLRule] = self._load_acl_rules()
        self.cors_policies: Dict[str, CORSPolicy] = self._load_cors_policies()
        self.instances: Dict[str, InstanceProfile] = self._load_instances()
    
    def _load_acl_rules(self) -> Dict[str, ACLRule]:
        """Load ACL rules from configuration file"""
        if not self.acl_file.exists():
            return {}
        
        try:
            with open(self.acl_file, 'r') as f:
                data = json.load(f)
            
            rules = {}
            for rule_id, rule_data in data.items():
                rules[rule_id] = ACLRule(**rule_data)
            
            return rules
        except Exception as e:
            print(f"❌ Error loading ACL rules: {e}")
            return {}
    
    def _load_cors_policies(self) -> Dict[str, CORSPolicy]:
        """Load CORS policies from configuration file"""
        if not self.cors_file.exists():
            return {}
        
        try:
            with open(self.cors_file, 'r') as f:
                data = json.load(f)
            
            policies = {}
            for policy_id, policy_data in data.items():
                policies[policy_id] = CORSPolicy(**policy_data)
            
            return policies
        except Exception as e:
            print(f"❌ Error loading CORS policies: {e}")
            return {}
    
    def _load_instances(self) -> Dict[str, InstanceProfile]:
        """Load instance profiles from configuration file"""
        if not self.instances_file.exists():
            return {}
        
        try:
            with open(self.instances_file, 'r') as f:
                data = json.load(f)
            
            instances = {}
            for instance_id, instance_data in data.items():
                # Convert sets back from lists
                if 'trusted_instances' in instance_data:
                    instance_data['trusted_instances'] = set(instance_data['trusted_instances'])
                if 'blocked_instances' in instance_data:
                    instance_data['blocked_instances'] = set(instance_data['blocked_instances'])
                
                instance_data['security_level'] = SecurityLevel(instance_data['security_level'])
                instances[instance_id] = InstanceProfile(**instance_data)
            
            return instances
        except Exception as e:
            print(f"❌ Error loading instances: {e}")
            return {}
    
    def _save_acl_rules(self):
        """Save ACL rules to configuration file"""
        try:
            data = {}
            for rule_id, rule in self.acl_rules.items():
                rule_data = asdict(rule)
                rule_data['action'] = rule.action.value
                data[rule_id] = rule_data
            
            with open(self.acl_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving ACL rules: {e}")
    
    def _save_cors_policies(self):
        """Save CORS policies to configuration file"""
        try:
            data = {}
            for policy_id, policy in self.cors_policies.items():
                data[policy_id] = asdict(policy)
            
            with open(self.cors_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving CORS policies: {e}")
    
    def _save_instances(self):
        """Save instance profiles to configuration file"""
        try:
            data = {}
            for instance_id, instance in self.instances.items():
                instance_data = asdict(instance)
                # Convert sets to lists for JSON serialization
                instance_data['trusted_instances'] = list(instance.trusted_instances)
                instance_data['blocked_instances'] = list(instance.blocked_instances)
                instance_data['security_level'] = instance.security_level.value
                data[instance_id] = instance_data
            
            with open(self.instances_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving instances: {e}")
    
    def _audit_log(self, action: str, details: str, source: str = "system"):
        """Log security-related actions for audit purposes"""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = f"[{timestamp}] {source}: {action} - {details}\n"
            
            with open(self.audit_file, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"❌ Error writing audit log: {e}")
    
    # ACL Management Methods
    
    def add_acl_rule(self, rule: ACLRule) -> bool:
        """Add a new ACL rule"""
        try:
            self.acl_rules[rule.id] = rule
            self._save_acl_rules()
            self._audit_log("ACL_RULE_ADDED", f"Rule {rule.id}: {rule.name}")
            return True
        except Exception as e:
            print(f"❌ Error adding ACL rule: {e}")
            return False
    
    def remove_acl_rule(self, rule_id: str) -> bool:
        """Remove an ACL rule"""
        try:
            if rule_id in self.acl_rules:
                rule = self.acl_rules.pop(rule_id)
                self._save_acl_rules()
                self._audit_log("ACL_RULE_REMOVED", f"Rule {rule_id}: {rule.name}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error removing ACL rule: {e}")
            return False
    
    def list_acl_rules(self) -> List[ACLRule]:
        """List all ACL rules"""
        return list(self.acl_rules.values())
    
    def get_acl_rule(self, rule_id: str) -> Optional[ACLRule]:
        """Get specific ACL rule by ID"""
        return self.acl_rules.get(rule_id)
    
    # CORS Management Methods
    
    def add_cors_policy(self, policy: CORSPolicy) -> bool:
        """Add a new CORS policy"""
        try:
            self.cors_policies[policy.id] = policy
            self._save_cors_policies()
            self._audit_log("CORS_POLICY_ADDED", f"Policy {policy.id}: {policy.name}")
            return True
        except Exception as e:
            print(f"❌ Error adding CORS policy: {e}")
            return False
    
    def remove_cors_policy(self, policy_id: str) -> bool:
        """Remove a CORS policy"""
        try:
            if policy_id in self.cors_policies:
                policy = self.cors_policies.pop(policy_id)
                self._save_cors_policies()
                self._audit_log("CORS_POLICY_REMOVED", f"Policy {policy_id}: {policy.name}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error removing CORS policy: {e}")
            return False
    
    def list_cors_policies(self) -> List[CORSPolicy]:
        """List all CORS policies"""
        return list(self.cors_policies.values())
    
    def get_cors_policy(self, policy_id: str) -> Optional[CORSPolicy]:
        """Get specific CORS policy by ID"""
        return self.cors_policies.get(policy_id)
    
    # Instance Management Methods
    
    def register_instance(self, instance: InstanceProfile) -> bool:
        """Register a new Mova instance"""
        try:
            self.instances[instance.instance_id] = instance
            self._save_instances()
            self._audit_log("INSTANCE_REGISTERED", 
                          f"Instance {instance.instance_id} ({instance.instance_type})")
            return True
        except Exception as e:
            print(f"❌ Error registering instance: {e}")
            return False
    
    def unregister_instance(self, instance_id: str) -> bool:
        """Unregister a Mova instance"""
        try:
            if instance_id in self.instances:
                instance = self.instances.pop(instance_id)
                self._save_instances()
                self._audit_log("INSTANCE_UNREGISTERED", f"Instance {instance_id}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error unregistering instance: {e}")
            return False
    
    def list_instances(self) -> List[InstanceProfile]:
        """List all registered instances"""
        return list(self.instances.values())
    
    def get_instance(self, instance_id: str) -> Optional[InstanceProfile]:
        """Get specific instance by ID"""
        return self.instances.get(instance_id)
    
    # Security Validation Methods
    
    def validate_access(self, source: str, target_resource: str, 
                       source_instance: str = None) -> tuple[bool, str]:
        """Validate access based on ACL rules"""
        try:
            # Get applicable rules sorted by priority
            applicable_rules = []
            for rule in self.acl_rules.values():
                if self._matches_pattern(source, rule.source_pattern):
                    if self._matches_pattern(target_resource, rule.target_resource):
                        # Check if rule has expired
                        if rule.expires_at:
                            expires = datetime.fromisoformat(rule.expires_at)
                            if datetime.now() > expires:
                                continue
                        applicable_rules.append(rule)
            
            # Sort by priority (lower number = higher priority)
            applicable_rules.sort(key=lambda r: r.priority)
            
            # Apply first matching rule
            for rule in applicable_rules:
                if rule.action == AccessAction.ALLOW:
                    self._audit_log("ACCESS_ALLOWED", 
                                  f"Source: {source}, Resource: {target_resource}, Rule: {rule.name}")
                    return True, f"Access allowed by rule: {rule.name}"
                elif rule.action == AccessAction.DENY:
                    self._audit_log("ACCESS_DENIED", 
                                  f"Source: {source}, Resource: {target_resource}, Rule: {rule.name}")
                    return False, f"Access denied by rule: {rule.name}"
                elif rule.action == AccessAction.LOG:
                    self._audit_log("ACCESS_LOGGED", 
                                  f"Source: {source}, Resource: {target_resource}, Rule: {rule.name}")
                    continue  # Continue to next rule
                elif rule.action == AccessAction.CHALLENGE:
                    self._audit_log("ACCESS_CHALLENGE", 
                                  f"Source: {source}, Resource: {target_resource}, Rule: {rule.name}")
                    return False, f"Authentication required by rule: {rule.name}"
            
            # Default policy - check instance security level
            if source_instance and source_instance in self.instances:
                instance = self.instances[source_instance]
                if instance.security_level == SecurityLevel.ISOLATED:
                    return False, "Instance is in isolated mode"
                elif instance.security_level == SecurityLevel.SECURE:
                    return False, "Secure instance requires explicit ACL rules"
            
            # Default allow for open systems
            return True, "Default allow policy"
            
        except Exception as e:
            self._audit_log("ACCESS_ERROR", f"Error validating access: {e}")
            return False, f"Access validation error: {e}"
    
    def _matches_pattern(self, value: str, pattern: str) -> bool:
        """Check if value matches pattern (supports wildcards and regex)"""
        try:
            # Handle IP address patterns
            if self._is_ip_pattern(pattern):
                return self._matches_ip_pattern(value, pattern)
            
            # Handle wildcard patterns
            if '*' in pattern or '?' in pattern:
                import fnmatch
                return fnmatch.fnmatch(value, pattern)
            
            # Handle regex patterns (enclosed in slashes)
            if pattern.startswith('/') and pattern.endswith('/'):
                regex = re.compile(pattern[1:-1])
                return bool(regex.match(value))
            
            # Exact match
            return value == pattern
            
        except Exception:
            return False
    
    def _is_ip_pattern(self, pattern: str) -> bool:
        """Check if pattern is an IP address or CIDR block"""
        try:
            ipaddress.ip_network(pattern, strict=False)
            return True
        except ValueError:
            return False
    
    def _matches_ip_pattern(self, ip: str, pattern: str) -> bool:
        """Check if IP matches IP pattern or CIDR block"""
        try:
            ip_addr = ipaddress.ip_address(ip)
            network = ipaddress.ip_network(pattern, strict=False)
            return ip_addr in network
        except ValueError:
            return False
    
    def get_cors_headers(self, origin: str, instance_id: str = None) -> Dict[str, str]:
        """Get CORS headers for a given origin and instance"""
        headers = {}
        
        try:
            # Find applicable CORS policies
            applicable_policies = []
            
            if instance_id and instance_id in self.instances:
                instance = self.instances[instance_id]
                for policy_id in instance.cors_policies:
                    if policy_id in self.cors_policies:
                        policy = self.cors_policies[policy_id]
                        if self._origin_matches_policy(origin, policy):
                            applicable_policies.append(policy)
            
            # If no instance-specific policies, check global policies
            if not applicable_policies:
                for policy in self.cors_policies.values():
                    if self._origin_matches_policy(origin, policy):
                        applicable_policies.append(policy)
            
            # Merge policies (most permissive wins)
            if applicable_policies:
                allowed_origins = set()
                allowed_methods = set()
                allowed_headers = set()
                expose_headers = set()
                allow_credentials = False
                max_age = 3600
                
                for policy in applicable_policies:
                    allowed_origins.update(policy.allowed_origins)
                    allowed_methods.update(policy.allowed_methods)
                    allowed_headers.update(policy.allowed_headers)
                    expose_headers.update(policy.expose_headers)
                    allow_credentials = allow_credentials or policy.allow_credentials
                    max_age = max(max_age, policy.max_age)
                
                headers['Access-Control-Allow-Origin'] = origin if origin in allowed_origins or '*' in allowed_origins else 'null'
                headers['Access-Control-Allow-Methods'] = ', '.join(allowed_methods)
                headers['Access-Control-Allow-Headers'] = ', '.join(allowed_headers)
                
                if expose_headers:
                    headers['Access-Control-Expose-Headers'] = ', '.join(expose_headers)
                
                if allow_credentials:
                    headers['Access-Control-Allow-Credentials'] = 'true'
                
                headers['Access-Control-Max-Age'] = str(max_age)
            
            return headers
            
        except Exception as e:
            self._audit_log("CORS_ERROR", f"Error generating CORS headers: {e}")
            return {}
    
    def _origin_matches_policy(self, origin: str, policy: CORSPolicy) -> bool:
        """Check if origin matches CORS policy"""
        for allowed_origin in policy.allowed_origins:
            if self._matches_pattern(origin, allowed_origin):
                return True
        return False
    
    def get_security_status(self) -> Dict[str, any]:
        """Get overall security status"""
        status = {
            'acl_rules_count': len(self.acl_rules),
            'cors_policies_count': len(self.cors_policies),
            'instances_count': len(self.instances),
            'security_levels': {},
            'expired_rules': 0,
            'last_audit_entries': []
        }
        
        # Count instances by security level
        for instance in self.instances.values():
            level = instance.security_level.value
            status['security_levels'][level] = status['security_levels'].get(level, 0) + 1
        
        # Count expired rules
        now = datetime.now()
        for rule in self.acl_rules.values():
            if rule.expires_at:
                expires = datetime.fromisoformat(rule.expires_at)
                if now > expires:
                    status['expired_rules'] += 1
        
        # Get last few audit entries
        try:
            if self.audit_file.exists():
                with open(self.audit_file, 'r') as f:
                    lines = f.readlines()
                    status['last_audit_entries'] = lines[-5:] if lines else []
        except Exception:
            pass
        
        return status


# Default security configurations
DEFAULT_SECURITY_PROFILES = {
    'development': {
        'security_level': SecurityLevel.OPEN,
        'default_acl_rules': [
            {
                'id': 'dev_allow_all',
                'name': 'Development - Allow All',
                'source_pattern': '*',
                'target_resource': '*',
                'action': AccessAction.LOG,
                'priority': 1000,
                'description': 'Development environment - log all access'
            }
        ],
        'default_cors_policy': {
            'id': 'dev_cors',
            'name': 'Development CORS',
            'allowed_origins': ['*'],
            'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'allowed_headers': ['*'],
            'allow_credentials': True,
            'description': 'Permissive CORS for development'
        }
    },
    'production': {
        'security_level': SecurityLevel.SECURE,
        'default_acl_rules': [
            {
                'id': 'prod_deny_default',
                'name': 'Production - Deny by Default',
                'source_pattern': '*',
                'target_resource': '*',
                'action': AccessAction.DENY,
                'priority': 1000,
                'description': 'Production environment - deny by default'
            }
        ],
        'default_cors_policy': {
            'id': 'prod_cors',
            'name': 'Production CORS',
            'allowed_origins': [],  # Must be explicitly configured
            'allowed_methods': ['GET', 'POST'],
            'allowed_headers': ['Content-Type', 'Authorization'],
            'allow_credentials': False,
            'description': 'Restrictive CORS for production'
        }
    }
}
