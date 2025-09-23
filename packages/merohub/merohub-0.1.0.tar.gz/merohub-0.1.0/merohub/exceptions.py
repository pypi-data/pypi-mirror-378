"""
MeroHub Exception Classes
Author: MERO (Telegram: @QP4RM)

Custom exception classes for comprehensive error handling across the MeroHub library.
Provides detailed error information and debugging capabilities for all GitHub operations.
"""

import traceback
import json
from typing import Optional, Dict, Any, List, Union
from datetime import datetime


class MeroHubError(Exception):
    """Base exception class for all MeroHub related errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None,
                 original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "MEROHUB_ERROR"
        self.details = details or {}
        self.original_exception = original_exception
        self.timestamp = datetime.now().isoformat()
        self.traceback = traceback.format_exc() if original_exception else None
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'details': self.details,
            'timestamp': self.timestamp,
            'traceback': self.traceback
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    def __str__(self) -> str:
        base_msg = f"[{self.error_code}] {self.message}"
        if self.details:
            base_msg += f" | Details: {self.details}"
        return base_msg


class AuthenticationError(MeroHubError):
    """Raised when GitHub authentication fails or token is invalid."""
    
    def __init__(self, message: str = "GitHub authentication failed",
                 token_status: Optional[str] = None,
                 permissions: Optional[List[str]] = None,
                 **kwargs):
        super().__init__(message, error_code="AUTH_ERROR", **kwargs)
        self.details.update({
            'token_status': token_status,
            'required_permissions': permissions or [],
            'suggestion': 'Check your GitHub token and permissions'
        })


class APIError(MeroHubError):
    """Raised when GitHub API returns an error response."""
    
    def __init__(self, message: str, status_code: Optional[int] = None,
                 response_data: Optional[Dict[str, Any]] = None,
                 endpoint: Optional[str] = None,
                 method: Optional[str] = None,
                 **kwargs):
        super().__init__(message, error_code="API_ERROR", **kwargs)
        self.status_code = status_code
        self.response_data = response_data or {}
        self.details.update({
            'status_code': status_code,
            'endpoint': endpoint,
            'method': method,
            'response_data': self.response_data,
            'rate_limit_remaining': self.response_data.get('rate_limit_remaining'),
            'rate_limit_reset': self.response_data.get('rate_limit_reset')
        })
    
    def is_rate_limited(self) -> bool:
        return self.status_code == 403 and 'rate limit' in self.message.lower()
    
    def is_not_found(self) -> bool:
        return self.status_code == 404
    
    def is_forbidden(self) -> bool:
        return self.status_code == 403
    
    def is_unauthorized(self) -> bool:
        return self.status_code == 401


class ValidationError(MeroHubError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None,
                 value: Optional[Any] = None,
                 expected_type: Optional[str] = None,
                 validation_rules: Optional[List[str]] = None,
                 **kwargs):
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        self.details.update({
            'field': field,
            'value': str(value) if value is not None else None,
            'expected_type': expected_type,
            'validation_rules': validation_rules or []
        })


class NetworkError(MeroHubError):
    """Raised when network-related errors occur."""
    
    def __init__(self, message: str, network_info: Optional[Dict[str, Any]] = None,
                 retry_count: int = 0, max_retries: int = 3,
                 **kwargs):
        super().__init__(message, error_code="NETWORK_ERROR", **kwargs)
        self.details.update({
            'network_info': network_info or {},
            'retry_count': retry_count,
            'max_retries': max_retries,
            'suggestion': 'Check your internet connection and retry'
        })


class RepositoryError(MeroHubError):
    """Raised when repository operations fail."""
    
    def __init__(self, message: str, repository: Optional[str] = None,
                 operation: Optional[str] = None,
                 **kwargs):
        super().__init__(message, error_code="REPO_ERROR", **kwargs)
        self.details.update({
            'repository': repository,
            'operation': operation
        })


class SearchError(MeroHubError):
    """Raised when search operations fail."""
    
    def __init__(self, message: str, query: Optional[str] = None,
                 search_type: Optional[str] = None,
                 filters: Optional[Dict[str, Any]] = None,
                 **kwargs):
        super().__init__(message, error_code="SEARCH_ERROR", **kwargs)
        self.details.update({
            'query': query,
            'search_type': search_type,
            'filters': filters or {}
        })


class UserError(MeroHubError):
    """Raised when user operations fail."""
    
    def __init__(self, message: str, username: Optional[str] = None,
                 operation: Optional[str] = None,
                 **kwargs):
        super().__init__(message, error_code="USER_ERROR", **kwargs)
        self.details.update({
            'username': username,
            'operation': operation
        })


class IssueError(MeroHubError):
    """Raised when issue operations fail."""
    
    def __init__(self, message: str, issue_number: Optional[int] = None,
                 repository: Optional[str] = None,
                 operation: Optional[str] = None,
                 **kwargs):
        super().__init__(message, error_code="ISSUE_ERROR", **kwargs)
        self.details.update({
            'issue_number': issue_number,
            'repository': repository,
            'operation': operation
        })


class PullRequestError(MeroHubError):
    """Raised when pull request operations fail."""
    
    def __init__(self, message: str, pr_number: Optional[int] = None,
                 repository: Optional[str] = None,
                 operation: Optional[str] = None,
                 **kwargs):
        super().__init__(message, error_code="PR_ERROR", **kwargs)
        self.details.update({
            'pr_number': pr_number,
            'repository': repository,
            'operation': operation
        })


class GitOperationError(MeroHubError):
    """Raised when Git operations fail."""
    
    def __init__(self, message: str, git_command: Optional[str] = None,
                 repository_path: Optional[str] = None,
                 branch: Optional[str] = None,
                 **kwargs):
        super().__init__(message, error_code="GIT_ERROR", **kwargs)
        self.details.update({
            'git_command': git_command,
            'repository_path': repository_path,
            'branch': branch
        })


class AIAnalysisError(MeroHubError):
    """Raised when AI analysis operations fail."""
    
    def __init__(self, message: str, analysis_type: Optional[str] = None,
                 model_info: Optional[Dict[str, Any]] = None,
                 data_size: Optional[int] = None,
                 **kwargs):
        super().__init__(message, error_code="AI_ERROR", **kwargs)
        self.details.update({
            'analysis_type': analysis_type,
            'model_info': model_info or {},
            'data_size': data_size
        })


class AutomationError(MeroHubError):
    """Raised when automation operations fail."""
    
    def __init__(self, message: str, automation_type: Optional[str] = None,
                 trigger: Optional[str] = None,
                 action: Optional[str] = None,
                 **kwargs):
        super().__init__(message, error_code="AUTOMATION_ERROR", **kwargs)
        self.details.update({
            'automation_type': automation_type,
            'trigger': trigger,
            'action': action
        })


class ConfigurationError(MeroHubError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_key: Optional[str] = None,
                 config_file: Optional[str] = None,
                 **kwargs):
        super().__init__(message, error_code="CONFIG_ERROR", **kwargs)
        self.details.update({
            'config_key': config_key,
            'config_file': config_file,
            'suggestion': 'Check your configuration file and required settings'
        })


class SecurityError(MeroHubError):
    """Raised when security violations are detected."""
    
    def __init__(self, message: str, security_type: Optional[str] = None,
                 threat_level: str = "MEDIUM",
                 recommended_action: Optional[str] = None,
                 **kwargs):
        super().__init__(message, error_code="SECURITY_ERROR", **kwargs)
        self.details.update({
            'security_type': security_type,
            'threat_level': threat_level,
            'recommended_action': recommended_action or 'Review security settings'
        })


class RateLimitError(APIError):
    """Raised when GitHub API rate limit is exceeded."""
    
    def __init__(self, message: str = "GitHub API rate limit exceeded",
                 reset_time: Optional[int] = None,
                 remaining: int = 0,
                 limit: Optional[int] = None,
                 **kwargs):
        super().__init__(message, status_code=403, **kwargs)
        self.error_code = "RATE_LIMIT_ERROR"
        self.details.update({
            'reset_time': reset_time,
            'remaining': remaining,
            'limit': limit,
            'suggestion': f'Wait until {datetime.fromtimestamp(reset_time)} to retry' if reset_time else 'Wait before retrying'
        })


class DataProcessingError(MeroHubError):
    """Raised when data processing operations fail."""
    
    def __init__(self, message: str, data_type: Optional[str] = None,
                 processing_stage: Optional[str] = None,
                 data_size: Optional[int] = None,
                 **kwargs):
        super().__init__(message, error_code="DATA_ERROR", **kwargs)
        self.details.update({
            'data_type': data_type,
            'processing_stage': processing_stage,
            'data_size': data_size
        })


class WebhookError(MeroHubError):
    """Raised when webhook operations fail."""
    
    def __init__(self, message: str, webhook_url: Optional[str] = None,
                 event_type: Optional[str] = None,
                 payload_size: Optional[int] = None,
                 **kwargs):
        super().__init__(message, error_code="WEBHOOK_ERROR", **kwargs)
        self.details.update({
            'webhook_url': webhook_url,
            'event_type': event_type,
            'payload_size': payload_size
        })


class ExportImportError(MeroHubError):
    """Raised when data export/import operations fail."""
    
    def __init__(self, message: str, operation: str = "unknown",
                 file_format: Optional[str] = None,
                 file_path: Optional[str] = None,
                 **kwargs):
        super().__init__(message, error_code="EXPORT_IMPORT_ERROR", **kwargs)
        self.details.update({
            'operation': operation,
            'file_format': file_format,
            'file_path': file_path
        })


class ErrorHandler:
    """Centralized error handler for the MeroHub library."""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.error_stats = {
            'total_errors': 0,
            'error_types': {},
            'recent_errors': []
        }
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> MeroHubError:
        """Convert generic exceptions to MeroHub-specific errors."""
        
        if isinstance(error, MeroHubError):
            merohub_error = error
        else:
            merohub_error = MeroHubError(
                message=str(error),
                original_exception=error,
                details=context or {}
            )
        
        self._log_error(merohub_error)
        self._update_stats(merohub_error)
        
        return merohub_error
    
    def _log_error(self, error: MeroHubError):
        """Log the error with appropriate level."""
        if self.logger:
            if isinstance(error, (SecurityError, AuthenticationError)):
                self.logger.error(f"SECURITY ISSUE: {error}")
            elif isinstance(error, RateLimitError):
                self.logger.warning(f"RATE LIMIT: {error}")
            elif isinstance(error, ValidationError):
                self.logger.warning(f"VALIDATION: {error}")
            else:
                self.logger.error(f"ERROR: {error}")
    
    def _update_stats(self, error: MeroHubError):
        """Update error statistics."""
        self.error_stats['total_errors'] += 1
        error_type = error.__class__.__name__
        
        if error_type not in self.error_stats['error_types']:
            self.error_stats['error_types'][error_type] = 0
        self.error_stats['error_types'][error_type] += 1
        
        self.error_stats['recent_errors'].append({
            'timestamp': error.timestamp,
            'type': error_type,
            'message': error.message,
            'error_code': error.error_code
        })
        
        if len(self.error_stats['recent_errors']) > 100:
            self.error_stats['recent_errors'] = self.error_stats['recent_errors'][-50:]
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get current error statistics."""
        return self.error_stats.copy()
    
    def clear_stats(self):
        """Clear error statistics."""
        self.error_stats = {
            'total_errors': 0,
            'error_types': {},
            'recent_errors': []
        }


def create_error_from_response(response, endpoint: str = None, method: str = None) -> APIError:
    """Create appropriate error from HTTP response."""
    
    try:
        error_data = response.json() if hasattr(response, 'json') else {}
    except:
        error_data = {}
    
    status_code = getattr(response, 'status_code', None)
    message = error_data.get('message', f"HTTP {status_code} error")
    
    if status_code == 401:
        return AuthenticationError(
            message=message,
            token_status="invalid",
            original_exception=None
        )
    elif status_code == 403:
        if 'rate limit' in message.lower():
            return RateLimitError(
                message=message,
                reset_time=response.headers.get('X-RateLimit-Reset'),
                remaining=int(response.headers.get('X-RateLimit-Remaining', 0)),
                limit=int(response.headers.get('X-RateLimit-Limit', 5000))
            )
        else:
            return APIError(
                message=message,
                status_code=status_code,
                response_data=error_data,
                endpoint=endpoint,
                method=method
            )
    elif status_code == 404:
        return APIError(
            message=f"Resource not found: {message}",
            status_code=status_code,
            response_data=error_data,
            endpoint=endpoint,
            method=method
        )
    else:
        return APIError(
            message=message,
            status_code=status_code,
            response_data=error_data,
            endpoint=endpoint,
            method=method
        )


def validate_github_token(token: str) -> bool:
    """Validate GitHub token format."""
    if not token:
        raise ValidationError("GitHub token cannot be empty", field="token")
    
    if not isinstance(token, str):
        raise ValidationError("GitHub token must be a string", field="token", expected_type="str")
    
    if len(token) < 20:
        raise ValidationError("GitHub token appears to be too short", field="token")
    
    if not token.startswith(('ghp_', 'github_pat_', 'gho_', 'ghu_', 'ghs_', 'ghr_')):
        raise ValidationError("GitHub token format appears invalid", field="token")
    
    return True


def validate_repository_name(name: str) -> bool:
    """Validate repository name format."""
    if not name:
        raise ValidationError("Repository name cannot be empty", field="name")
    
    if not isinstance(name, str):
        raise ValidationError("Repository name must be a string", field="name", expected_type="str")
    
    if len(name) > 100:
        raise ValidationError("Repository name too long (max 100 characters)", field="name")
    
    import re
    if not re.match(r'^[a-zA-Z0-9._-]+$', name):
        raise ValidationError("Repository name contains invalid characters", field="name")
    
    return True


def validate_username(username: str) -> bool:
    """Validate GitHub username format."""
    if not username:
        raise ValidationError("Username cannot be empty", field="username")
    
    if not isinstance(username, str):
        raise ValidationError("Username must be a string", field="username", expected_type="str")
    
    if len(username) > 39:
        raise ValidationError("Username too long (max 39 characters)", field="username")
    
    import re
    if not re.match(r'^[a-zA-Z0-9-]+$', username):
        raise ValidationError("Username contains invalid characters", field="username")
    
    return True


__all__ = [
    'MeroHubError',
    'AuthenticationError',
    'APIError',
    'ValidationError',
    'NetworkError',
    'RepositoryError',
    'SearchError',
    'UserError',
    'IssueError',
    'PullRequestError',
    'GitOperationError',
    'AIAnalysisError',
    'AutomationError',
    'ConfigurationError',
    'SecurityError',
    'RateLimitError',
    'DataProcessingError',
    'WebhookError',
    'ExportImportError',
    'ErrorHandler',
    'create_error_from_response',
    'validate_github_token',
    'validate_repository_name',
    'validate_username'
]