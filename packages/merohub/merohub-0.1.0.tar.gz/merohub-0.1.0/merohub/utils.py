"""
MeroHub Utility Classes and Functions
Author: MERO (Telegram: @QP4RM)

Comprehensive utility classes providing logging, configuration management,
security features, data processing, and helper functions for the MeroHub library.
"""

import os
import json
import yaml
import logging
import hashlib
import base64
import secrets
import time
import gzip
import csv
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Callable, Tuple
from pathlib import Path
import threading
import queue
import pickle
from functools import wraps, lru_cache
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import requests
from dataclasses import dataclass, asdict
import urllib.parse
import re
import platform
import psutil


@dataclass
class SystemInfo:
    """System information container."""
    platform: str
    architecture: str
    python_version: str
    cpu_count: int
    memory_total: int
    memory_available: int
    disk_usage: Dict[str, int]
    network_interfaces: List[str]
    timestamp: str


class Logger:
    """Advanced logging system for MeroHub with multiple output formats and filtering."""
    
    def __init__(self, name: str = "MeroHub", 
                 level: str = "INFO",
                 enable_file_logging: bool = True,
                 log_directory: str = "logs",
                 max_file_size: int = 10*1024*1024,  # 10MB
                 backup_count: int = 5,
                 enable_json_format: bool = False,
                 enable_metrics: bool = True):
        
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = self._create_formatter(enable_json_format)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if enable_file_logging:
            self._setup_file_logging(log_directory, max_file_size, backup_count, enable_json_format)
        
        # Metrics
        if enable_metrics:
            self.metrics = {
                'total_logs': 0,
                'levels': {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0},
                'start_time': datetime.now().isoformat(),
                'recent_logs': []
            }
        else:
            self.metrics = None
    
    def _create_formatter(self, json_format: bool = False) -> logging.Formatter:
        """Create appropriate formatter based on format preference."""
        if json_format:
            return JsonFormatter()
        else:
            return logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
    
    def _setup_file_logging(self, log_directory: str, max_file_size: int, 
                          backup_count: int, json_format: bool):
        """Setup rotating file logging."""
        from logging.handlers import RotatingFileHandler
        
        # Create log directory
        Path(log_directory).mkdir(exist_ok=True)
        
        # File handler
        log_file = Path(log_directory) / f"{self.name.lower()}.log"
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_file_size, backupCount=backup_count
        )
        
        file_formatter = self._create_formatter(json_format)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def _log_with_metrics(self, level: str, message: str, *args, **kwargs):
        """Log message and update metrics if enabled."""
        if self.metrics:
            self.metrics['total_logs'] += 1
            self.metrics['levels'][level] += 1
            self.metrics['recent_logs'].append({
                'timestamp': datetime.now().isoformat(),
                'level': level,
                'message': message % args if args else message
            })
            
            # Keep only recent 100 logs
            if len(self.metrics['recent_logs']) > 100:
                self.metrics['recent_logs'] = self.metrics['recent_logs'][-50:]
    
    def debug(self, message: str, *args, **kwargs):
        self._log_with_metrics('DEBUG', message, *args, **kwargs)
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        self._log_with_metrics('INFO', message, *args, **kwargs)
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        self._log_with_metrics('WARNING', message, *args, **kwargs)
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        self._log_with_metrics('ERROR', message, *args, **kwargs)
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        self._log_with_metrics('CRITICAL', message, *args, **kwargs)
        self.logger.critical(message, *args, **kwargs)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get logging metrics."""
        if not self.metrics:
            return {}
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset logging metrics."""
        if self.metrics:
            self.metrics = {
                'total_logs': 0,
                'levels': {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0},
                'start_time': datetime.now().isoformat(),
                'recent_logs': []
            }


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'module': record.module,
            'filename': record.filename
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class ConfigManager:
    """Advanced configuration management with multiple sources and validation."""
    
    def __init__(self, config_file: Optional[str] = None,
                 environment_prefix: str = "MEROHUB_",
                 enable_encryption: bool = False,
                 encryption_key: Optional[str] = None):
        
        self.config_file = config_file or "merohub_config.yaml"
        self.environment_prefix = environment_prefix
        self.enable_encryption = enable_encryption
        self.encryption_key = encryption_key
        
        self._config_data = {}
        self._watchers = []
        self._last_modified = None
        
        # Load configuration
        self.reload()
        
        # Setup file watcher
        if os.path.exists(self.config_file):
            self._setup_file_watcher()
    
    def reload(self):
        """Reload configuration from all sources."""
        self._config_data.clear()
        
        # Load from file
        if os.path.exists(self.config_file):
            self._load_from_file()
        
        # Override with environment variables
        self._load_from_environment()
        
        # Validate configuration
        self._validate_config()
    
    def _load_from_file(self):
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                if self.config_file.endswith('.json'):
                    file_config = json.load(f)
                elif self.config_file.endswith(('.yaml', '.yml')):
                    file_config = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {self.config_file}")
            
            if self.enable_encryption and file_config.get('encrypted'):
                file_config = self._decrypt_config(file_config)
            
            self._config_data.update(file_config)
            self._last_modified = os.path.getmtime(self.config_file)
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to load config file: {e}")
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        for key, value in os.environ.items():
            if key.startswith(self.environment_prefix):
                config_key = key[len(self.environment_prefix):].lower()
                
                # Try to parse as JSON, otherwise use as string
                try:
                    parsed_value = json.loads(value)
                except json.JSONDecodeError:
                    parsed_value = value
                
                self._config_data[config_key] = parsed_value
    
    def _validate_config(self):
        """Validate configuration values."""
        required_keys = ['github_token']  # Add more as needed
        
        for key in required_keys:
            if key not in self._config_data:
                logging.getLogger(__name__).warning(f"Required config key missing: {key}")
    
    def _setup_file_watcher(self):
        """Setup file watcher for automatic reload."""
        def watch_file():
            while True:
                try:
                    if os.path.exists(self.config_file):
                        current_modified = os.path.getmtime(self.config_file)
                        if self._last_modified and current_modified > self._last_modified:
                            self.reload()
                            for callback in self._watchers:
                                callback(self._config_data)
                    time.sleep(1)
                except Exception as e:
                    logging.getLogger(__name__).error(f"File watcher error: {e}")
        
        watcher_thread = threading.Thread(target=watch_file, daemon=True)
        watcher_thread.start()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config_data.get(key, default)
    
    def set(self, key: str, value: Any, persist: bool = True):
        """Set configuration value."""
        self._config_data[key] = value
        
        if persist:
            self.save()
    
    def update(self, config_dict: Dict[str, Any], persist: bool = True):
        """Update multiple configuration values."""
        self._config_data.update(config_dict)
        
        if persist:
            self.save()
    
    def save(self):
        """Save current configuration to file."""
        try:
            config_to_save = self._config_data.copy()
            
            if self.enable_encryption:
                config_to_save = self._encrypt_config(config_to_save)
            
            with open(self.config_file, 'w') as f:
                if self.config_file.endswith('.json'):
                    json.dump(config_to_save, f, indent=2)
                elif self.config_file.endswith(('.yaml', '.yml')):
                    yaml.dump(config_to_save, f, default_flow_style=False)
            
            self._last_modified = os.path.getmtime(self.config_file)
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to save config: {e}")
    
    def add_watcher(self, callback: Callable[[Dict[str, Any]], None]):
        """Add configuration change watcher."""
        self._watchers.append(callback)
    
    def remove_watcher(self, callback: Callable[[Dict[str, Any]], None]):
        """Remove configuration change watcher."""
        if callback in self._watchers:
            self._watchers.remove(callback)
    
    def _encrypt_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive configuration data."""
        if not self.encryption_key:
            return config
        
        # Implementation would use Fernet encryption
        # Simplified for this example
        return {'encrypted': True, 'data': 'encrypted_data_placeholder'}
    
    def _decrypt_config(self, encrypted_config: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt configuration data."""
        # Implementation would decrypt using Fernet
        # Simplified for this example
        return {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return self._config_data.copy()
    
    def keys(self) -> List[str]:
        """Get all configuration keys."""
        return list(self._config_data.keys())
    
    def has_key(self, key: str) -> bool:
        """Check if configuration key exists."""
        return key in self._config_data


class SecurityManager:
    """Security utilities for token management and data protection."""
    
    def __init__(self, config: Optional[ConfigManager] = None):
        self.config = config
        self.logger = Logger("SecurityManager")
        self._token_cache = {}
        self._access_log = []
        
        # Initialize encryption
        self._setup_encryption()
    
    def _setup_encryption(self):
        """Setup encryption capabilities."""
        try:
            # Generate or load encryption key
            key_file = "security.key"
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    self.encryption_key = f.read()
            else:
                self.encryption_key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(self.encryption_key)
                # Set secure file permissions
                os.chmod(key_file, 0o600)
            
            self.fernet = Fernet(self.encryption_key)
            
        except Exception as e:
            self.logger.error(f"Failed to setup encryption: {e}")
            self.fernet = None
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate GitHub token format and characteristics."""
        validation_result = {
            'valid': False,
            'token_type': 'unknown',
            'permissions': [],
            'expires': None,
            'warnings': []
        }
        
        if not token or not isinstance(token, str):
            validation_result['warnings'].append("Token is empty or not a string")
            return validation_result
        
        # Detect token type
        if token.startswith('ghp_'):
            validation_result['token_type'] = 'personal_access_token'
        elif token.startswith('github_pat_'):
            validation_result['token_type'] = 'fine_grained_personal_access_token'
        elif token.startswith('gho_'):
            validation_result['token_type'] = 'oauth_token'
        elif token.startswith('ghu_'):
            validation_result['token_type'] = 'user_token'
        elif token.startswith('ghs_'):
            validation_result['token_type'] = 'server_token'
        elif token.startswith('ghr_'):
            validation_result['token_type'] = 'refresh_token'
        else:
            validation_result['warnings'].append("Unknown token format")
            return validation_result
        
        # Basic format validation
        if len(token) < 20:
            validation_result['warnings'].append("Token appears too short")
        
        if len(token) > 255:
            validation_result['warnings'].append("Token appears too long")
        
        # Check for common issues
        if ' ' in token:
            validation_result['warnings'].append("Token contains spaces")
        
        if not all(c.isalnum() or c == '_' for c in token):
            validation_result['warnings'].append("Token contains unusual characters")
        
        validation_result['valid'] = len(validation_result['warnings']) == 0
        
        # Log validation attempt
        self._log_access('token_validation', {
            'token_type': validation_result['token_type'],
            'valid': validation_result['valid'],
            'warnings_count': len(validation_result['warnings'])
        })
        
        return validation_result
    
    def encrypt_sensitive_data(self, data: Union[str, bytes]) -> Optional[str]:
        """Encrypt sensitive data."""
        if not self.fernet:
            self.logger.warning("Encryption not available")
            return None
        
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            encrypted_data = self.fernet.encrypt(data)
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            return None
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> Optional[str]:
        """Decrypt sensitive data."""
        if not self.fernet:
            self.logger.warning("Encryption not available")
            return None
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            return None
    
    def generate_secure_password(self, length: int = 32, 
                                include_symbols: bool = True) -> str:
        """Generate cryptographically secure password."""
        import string
        
        characters = string.ascii_letters + string.digits
        if include_symbols:
            characters += "!@#$%^&*()_+-="
        
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    def hash_data(self, data: Union[str, bytes], 
                  algorithm: str = 'sha256') -> str:
        """Hash data using specified algorithm."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if algorithm == 'sha256':
            return hashlib.sha256(data).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(data).hexdigest()
        elif algorithm == 'md5':
            return hashlib.md5(data).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    def verify_hash(self, data: Union[str, bytes], 
                   expected_hash: str, 
                   algorithm: str = 'sha256') -> bool:
        """Verify data against hash."""
        computed_hash = self.hash_data(data, algorithm)
        return computed_hash == expected_hash
    
    def _log_access(self, action: str, details: Dict[str, Any]):
        """Log security-related access."""
        access_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details,
            'ip_address': self._get_client_ip()
        }
        
        self._access_log.append(access_entry)
        
        # Keep only recent 1000 entries
        if len(self._access_log) > 1000:
            self._access_log = self._access_log[-500:]
    
    def _get_client_ip(self) -> str:
        """Get client IP address (simplified)."""
        return "127.0.0.1"  # Placeholder
    
    def get_access_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent access log entries."""
        return self._access_log[-limit:]
    
    def clear_access_log(self):
        """Clear access log."""
        self._access_log.clear()
    
    def audit_security(self) -> Dict[str, Any]:
        """Perform security audit."""
        audit_result = {
            'timestamp': datetime.now().isoformat(),
            'encryption_available': self.fernet is not None,
            'access_log_entries': len(self._access_log),
            'recommendations': []
        }
        
        # Check for security recommendations
        if not self.fernet:
            audit_result['recommendations'].append("Enable encryption for sensitive data")
        
        if len(self._access_log) == 0:
            audit_result['recommendations'].append("Enable access logging")
        
        return audit_result


class DataProcessor:
    """Advanced data processing utilities for GitHub data."""
    
    def __init__(self, enable_caching: bool = True, 
                 cache_size: int = 1000,
                 compression_enabled: bool = True):
        
        self.enable_caching = enable_caching
        self.cache_size = cache_size
        self.compression_enabled = compression_enabled
        self.logger = Logger("DataProcessor")
        
        # Initialize cache
        if enable_caching:
            self.cache = {}
            self.cache_hits = 0
            self.cache_misses = 0
    
    @lru_cache(maxsize=128)
    def normalize_data(self, data: Dict[str, Any], 
                      schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Normalize data according to schema."""
        if not schema:
            return data
        
        normalized = {}
        
        for key, expected_type in schema.items():
            if key in data:
                value = data[key]
                
                if expected_type == 'datetime' and isinstance(value, str):
                    try:
                        normalized[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except ValueError:
                        normalized[key] = value
                elif expected_type == 'int' and not isinstance(value, int):
                    try:
                        normalized[key] = int(value)
                    except (ValueError, TypeError):
                        normalized[key] = value
                elif expected_type == 'float' and not isinstance(value, float):
                    try:
                        normalized[key] = float(value)
                    except (ValueError, TypeError):
                        normalized[key] = value
                else:
                    normalized[key] = value
            else:
                normalized[key] = None
        
        return normalized
    
    def aggregate_data(self, data_list: List[Dict[str, Any]], 
                      group_by: str,
                      aggregations: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Aggregate data by specified field."""
        groups = {}
        
        for item in data_list:
            group_key = item.get(group_by)
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(item)
        
        results = {}
        for group_key, group_items in groups.items():
            group_result = {'count': len(group_items)}
            
            for field, aggregation_type in aggregations.items():
                values = [item.get(field) for item in group_items if item.get(field) is not None]
                
                if values:
                    if aggregation_type == 'sum':
                        group_result[f"{field}_sum"] = sum(values)
                    elif aggregation_type == 'avg':
                        group_result[f"{field}_avg"] = sum(values) / len(values)
                    elif aggregation_type == 'min':
                        group_result[f"{field}_min"] = min(values)
                    elif aggregation_type == 'max':
                        group_result[f"{field}_max"] = max(values)
                    elif aggregation_type == 'count':
                        group_result[f"{field}_count"] = len(values)
            
            results[group_key] = group_result
        
        return results
    
    def filter_data(self, data_list: List[Dict[str, Any]], 
                   filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter data based on criteria."""
        filtered_data = []
        
        for item in data_list:
            include_item = True
            
            for field, criteria in filters.items():
                item_value = item.get(field)
                
                if isinstance(criteria, dict):
                    # Range or comparison filters
                    if 'min' in criteria and item_value < criteria['min']:
                        include_item = False
                        break
                    if 'max' in criteria and item_value > criteria['max']:
                        include_item = False
                        break
                    if 'equals' in criteria and item_value != criteria['equals']:
                        include_item = False
                        break
                    if 'contains' in criteria and criteria['contains'] not in str(item_value):
                        include_item = False
                        break
                elif isinstance(criteria, list):
                    # Value must be in list
                    if item_value not in criteria:
                        include_item = False
                        break
                else:
                    # Direct comparison
                    if item_value != criteria:
                        include_item = False
                        break
            
            if include_item:
                filtered_data.append(item)
        
        return filtered_data
    
    def sort_data(self, data_list: List[Dict[str, Any]], 
                 sort_key: str, 
                 reverse: bool = False) -> List[Dict[str, Any]]:
        """Sort data by specified key."""
        return sorted(data_list, key=lambda x: x.get(sort_key, 0), reverse=reverse)
    
    def export_data(self, data: Any, format: str = "json") -> str:
        """Export data in specified format."""
        if format.lower() == "json":
            return json.dumps(data, indent=2, default=str)
        elif format.lower() == "csv":
            if isinstance(data, list) and data and isinstance(data[0], dict):
                import io
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
                return output.getvalue()
            else:
                raise ValueError("CSV export requires list of dictionaries")
        elif format.lower() == "yaml":
            return yaml.dump(data, default_flow_style=False)
        elif format.lower() == "xml":
            return self._dict_to_xml(data)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_data(self, data_string: str, format: str = "json") -> Any:
        """Import data from string in specified format."""
        if format.lower() == "json":
            return json.loads(data_string)
        elif format.lower() == "yaml":
            return yaml.safe_load(data_string)
        elif format.lower() == "csv":
            import io
            reader = csv.DictReader(io.StringIO(data_string))
            return list(reader)
        else:
            raise ValueError(f"Unsupported import format: {format}")
    
    def _dict_to_xml(self, data: Dict[str, Any], root_name: str = "data") -> str:
        """Convert dictionary to XML (simplified)."""
        def dict_to_xml_recursive(d, tag):
            xml_str = f"<{tag}>"
            for key, value in d.items():
                if isinstance(value, dict):
                    xml_str += dict_to_xml_recursive(value, key)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            xml_str += dict_to_xml_recursive(item, key)
                        else:
                            xml_str += f"<{key}>{item}</{key}>"
                else:
                    xml_str += f"<{key}>{value}</{key}>"
            xml_str += f"</{tag}>"
            return xml_str
        
        return dict_to_xml_recursive(data, root_name)
    
    def compress_data(self, data: Union[str, bytes]) -> bytes:
        """Compress data using gzip."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        return gzip.compress(data)
    
    def decompress_data(self, compressed_data: bytes) -> str:
        """Decompress gzip data."""
        decompressed = gzip.decompress(compressed_data)
        return decompressed.decode('utf-8')
    
    def get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    def get_system_info(self) -> SystemInfo:
        """Get comprehensive system information."""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return SystemInfo(
                platform=platform.system(),
                architecture=platform.architecture()[0],
                python_version=platform.python_version(),
                cpu_count=psutil.cpu_count(),
                memory_total=memory.total,
                memory_available=memory.available,
                disk_usage={
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free
                },
                network_interfaces=[iface for iface in psutil.net_if_addrs().keys()],
                timestamp=self.get_timestamp()
            )
        except ImportError:
            # Fallback if psutil not available
            return SystemInfo(
                platform=platform.system(),
                architecture=platform.architecture()[0],
                python_version=platform.python_version(),
                cpu_count=os.cpu_count() or 1,
                memory_total=0,
                memory_available=0,
                disk_usage={'total': 0, 'used': 0, 'free': 0},
                network_interfaces=[],
                timestamp=self.get_timestamp()
            )


def retry_on_exception(max_retries: int = 3, 
                      delay: float = 1.0,
                      backoff_factor: float = 2.0,
                      exceptions: Tuple = (Exception,)):
    """Decorator for retrying functions on exception."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        raise e
                    
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
            
        return wrapper
    return decorator


def rate_limit(calls: int, period: int):
    """Decorator for rate limiting function calls."""
    def decorator(func):
        func._calls = []
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Remove old calls outside the period
            func._calls = [call_time for call_time in func._calls if now - call_time < period]
            
            # Check if we've exceeded the rate limit
            if len(func._calls) >= calls:
                sleep_time = period - (now - func._calls[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    func._calls = func._calls[1:]  # Remove the oldest call
            
            # Record this call
            func._calls.append(now)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def timed_cache(seconds: int):
    """Decorator for caching function results with expiration."""
    def decorator(func):
        func._cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = str(args) + str(sorted(kwargs.items()))
            current_time = time.time()
            
            # Check if we have a cached result that hasn't expired
            if cache_key in func._cache:
                result, timestamp = func._cache[cache_key]
                if current_time - timestamp < seconds:
                    return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            func._cache[cache_key] = (result, current_time)
            
            # Clean up expired entries
            expired_keys = [
                key for key, (_, timestamp) in func._cache.items()
                if current_time - timestamp >= seconds
            ]
            for key in expired_keys:
                del func._cache[key]
            
            return result
        
        return wrapper
    return decorator


__all__ = [
    'Logger',
    'JsonFormatter',
    'ConfigManager',
    'SecurityManager',
    'DataProcessor',
    'SystemInfo',
    'retry_on_exception',
    'rate_limit',
    'timed_cache'
]