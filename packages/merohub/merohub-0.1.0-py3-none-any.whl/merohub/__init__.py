"""
MEROHUB - Advanced comprehensive GitHub integration library with AI capabilities
Author: MERO (Telegram: @QP4RM)
Version: 1.0.0

A powerful Python library for complete GitHub integration with advanced AI capabilities,
neural networks, and automated GitHub communication features.

Supports all platforms: Android, Linux, Windows, iPhone, 32-bit and 64-bit systems.
"""

import sys
import os
import platform
import logging
from typing import Dict, Any, Optional, List, Union
import warnings
from .core import GitHubCore, GitHubAuth, GitHubConfig
from .repository import RepositoryManager, RepoAnalyzer, RepoStats
from .search import GitHubSearch, AdvancedSearch, SearchAnalytics
from .user import UserManager, UserAnalyzer, ProfileManager
from .issues import IssueManager, PullRequestManager, ProjectManager
from .git_ops import GitOperations, VersionControl, BranchManager
from .ai_analysis import AIAnalyzer, NeuralNetworkAnalyzer, MLPredictor
from .automation import GitHubBot, AutomatedInteractions, SmartResponder
from .utils import Logger, ConfigManager, SecurityManager, DataProcessor
from .exceptions import MeroHubError, AuthenticationError, APIError, ValidationError

__version__ = "1.0.0"
__author__ = "MERO"
__email__ = "QP4RM@telegram.com"
__license__ = "MIT"
__description__ = "Advanced comprehensive GitHub integration library with AI capabilities"

logger = logging.getLogger(__name__)

def get_system_info() -> Dict[str, Any]:
    return {
        'platform': platform.system(),
        'architecture': platform.architecture()[0],
        'python_version': sys.version,
        'merohub_version': __version__,
        'supported_platforms': ['Windows', 'Linux', 'Darwin', 'Android', 'iOS'],
        'supported_architectures': ['32bit', '64bit', 'ARM64', 'x86_64']
    }

def check_compatibility():
    system_info = get_system_info()
    python_major, python_minor = sys.version_info[:2]
    
    if python_major < 3 or (python_major == 3 and python_minor < 8):
        raise RuntimeError("MeroHub requires Python 3.8 or higher")
    
    if system_info['platform'] not in ['Windows', 'Linux', 'Darwin']:
        warnings.warn(f"Platform {system_info['platform']} may have limited support")
    
    return True

def configure_logging(level: str = "INFO", 
                     format_string: Optional[str] = None,
                     enable_file_logging: bool = False,
                     log_file_path: str = "merohub.log"):
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout),
            *([logging.FileHandler(log_file_path)] if enable_file_logging else [])
        ]
    )
    
    logger.info(f"MeroHub v{__version__} initialized successfully")
    logger.info(f"System: {get_system_info()}")

class MeroHub:
    def __init__(self, 
                 token: Optional[str] = None,
                 base_url: str = "https://api.github.com",
                 timeout: int = 30,
                 retries: int = 3,
                 enable_ai: bool = True,
                 enable_automation: bool = False,
                 config_path: Optional[str] = None):
        
        check_compatibility()
        
        self.config = GitHubConfig(
            token=token,
            base_url=base_url,
            timeout=timeout,
            retries=retries,
            config_path=config_path
        )
        
        self.auth = GitHubAuth(self.config)
        self.core = GitHubCore(self.config, self.auth)
        
        self.repositories = RepositoryManager(self.core)
        self.search = GitHubSearch(self.core)
        self.users = UserManager(self.core)
        self.issues = IssueManager(self.core)
        self.pull_requests = PullRequestManager(self.core)
        self.git_ops = GitOperations(self.core)
        
        if enable_ai:
            self.ai = AIAnalyzer(self.core)
            self.ml = MLPredictor(self.core)
            self.neural = NeuralNetworkAnalyzer(self.core)
        
        if enable_automation:
            self.bot = GitHubBot(self.core)
            self.automation = AutomatedInteractions(self.core)
            self.responder = SmartResponder(self.core)
        
        self.logger = Logger("MeroHub")
        self.security = SecurityManager(self.config)
        self.data_processor = DataProcessor()
        
        self.logger.info("MeroHub instance initialized successfully")
    
    def authenticate(self, token: Optional[str] = None) -> bool:
        if token:
            self.config.update_token(token)
        
        return self.auth.authenticate()
    
    def get_rate_limit(self) -> Dict[str, Any]:
        return self.core.get_rate_limit()
    
    def get_user_info(self, username: Optional[str] = None) -> Dict[str, Any]:
        return self.users.get_user(username or self.auth.get_authenticated_user())
    
    def search_repositories(self, query: str, 
                          language: Optional[str] = None,
                          sort: str = "updated",
                          order: str = "desc",
                          per_page: int = 30) -> List[Dict[str, Any]]:
        
        return self.search.search_repositories(
            query=query,
            language=language,
            sort=sort,
            order=order,
            per_page=per_page
        )
    
    def analyze_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        repo_data = self.repositories.get_repository(owner, repo)
        
        analysis = {
            'basic_info': repo_data,
            'statistics': self.repositories.get_repository_stats(owner, repo),
            'contributors': self.repositories.get_contributors(owner, repo),
            'languages': self.repositories.get_languages(owner, repo),
            'topics': repo_data.get('topics', []),
            'license': repo_data.get('license', {}),
        }
        
        if hasattr(self, 'ai'):
            analysis['ai_insights'] = self.ai.analyze_repository(owner, repo)
            analysis['ml_predictions'] = self.ml.predict_repository_metrics(owner, repo)
            analysis['neural_analysis'] = self.neural.deep_analysis(owner, repo)
        
        return analysis
    
    def create_repository(self, name: str, 
                         description: str = "",
                         private: bool = False,
                         auto_init: bool = True,
                         gitignore_template: Optional[str] = None,
                         license_template: Optional[str] = None) -> Dict[str, Any]:
        
        return self.repositories.create_repository(
            name=name,
            description=description,
            private=private,
            auto_init=auto_init,
            gitignore_template=gitignore_template,
            license_template=license_template
        )
    
    def fork_repository(self, owner: str, repo: str, 
                       organization: Optional[str] = None) -> Dict[str, Any]:
        return self.repositories.fork_repository(owner, repo, organization)
    
    def star_repository(self, owner: str, repo: str) -> bool:
        return self.repositories.star_repository(owner, repo)
    
    def unstar_repository(self, owner: str, repo: str) -> bool:
        return self.repositories.unstar_repository(owner, repo)
    
    def watch_repository(self, owner: str, repo: str) -> bool:
        return self.repositories.watch_repository(owner, repo)
    
    def unwatch_repository(self, owner: str, repo: str) -> bool:
        return self.repositories.unwatch_repository(owner, repo)
    
    def create_issue(self, owner: str, repo: str, title: str,
                    body: str = "", labels: Optional[List[str]] = None,
                    assignees: Optional[List[str]] = None) -> Dict[str, Any]:
        
        return self.issues.create_issue(
            owner=owner,
            repo=repo,
            title=title,
            body=body,
            labels=labels,
            assignees=assignees
        )
    
    def create_pull_request(self, owner: str, repo: str, title: str,
                           head: str, base: str = "main",
                           body: str = "", draft: bool = False) -> Dict[str, Any]:
        
        return self.pull_requests.create_pull_request(
            owner=owner,
            repo=repo,
            title=title,
            head=head,
            base=base,
            body=body,
            draft=draft
        )
    
    def get_trending_repositories(self, language: Optional[str] = None,
                                 since: str = "daily") -> List[Dict[str, Any]]:
        return self.search.get_trending_repositories(language, since)
    
    def get_repository_insights(self, owner: str, repo: str) -> Dict[str, Any]:
        insights = self.repositories.get_repository_insights(owner, repo)
        
        if hasattr(self, 'ai'):
            insights['ai_recommendations'] = self.ai.generate_recommendations(owner, repo)
            insights['predictive_analysis'] = self.ml.predict_future_trends(owner, repo)
        
        return insights
    
    def batch_analyze_repositories(self, repositories: List[tuple]) -> Dict[str, Any]:
        results = {}
        
        for owner, repo in repositories:
            try:
                results[f"{owner}/{repo}"] = self.analyze_repository(owner, repo)
            except Exception as e:
                results[f"{owner}/{repo}"] = {"error": str(e)}
        
        if hasattr(self, 'ai'):
            results['batch_insights'] = self.ai.compare_repositories(repositories)
        
        return results
    
    def enable_smart_notifications(self, webhook_url: str,
                                  events: Optional[List[str]] = None) -> bool:
        if not hasattr(self, 'automation'):
            raise MeroHubError("Automation features not enabled")
        
        return self.automation.setup_smart_notifications(webhook_url, events)
    
    def start_automated_responses(self, config: Dict[str, Any]) -> bool:
        if not hasattr(self, 'responder'):
            raise MeroHubError("Automation features not enabled")
        
        return self.responder.start_automated_responses(config)
    
    def export_data(self, format: str = "json", 
                   include_ai_insights: bool = True) -> str:
        data = {
            'version': __version__,
            'timestamp': self.data_processor.get_timestamp(),
            'user_info': self.get_user_info(),
            'rate_limit': self.get_rate_limit(),
        }
        
        if include_ai_insights and hasattr(self, 'ai'):
            data['ai_summary'] = self.ai.generate_user_summary()
        
        return self.data_processor.export_data(data, format)
    
    def import_data(self, data: str, format: str = "json") -> bool:
        imported_data = self.data_processor.import_data(data, format)
        
        if imported_data.get('version') != __version__:
            self.logger.warning("Data was exported from a different version")
        
        return True
    
    def health_check(self) -> Dict[str, Any]:
        health = {
            'status': 'healthy',
            'version': __version__,
            'system_info': get_system_info(),
            'authentication': self.auth.is_authenticated(),
            'rate_limit': self.get_rate_limit(),
            'timestamp': self.data_processor.get_timestamp()
        }
        
        try:
            test_request = self.core.make_request('GET', '/user')
            health['api_connectivity'] = True
        except Exception as e:
            health['api_connectivity'] = False
            health['api_error'] = str(e)
            health['status'] = 'unhealthy'
        
        return health
    
    def close(self):
        self.logger.info("Shutting down MeroHub instance")
        
        if hasattr(self, 'automation'):
            self.automation.stop()
        
        if hasattr(self, 'responder'):
            self.responder.stop()
        
        self.core.close()
        self.logger.info("MeroHub instance closed successfully")

def quick_start(token: str) -> MeroHub:
    configure_logging()
    hub = MeroHub(token=token, enable_ai=True, enable_automation=True)
    
    if not hub.authenticate():
        raise AuthenticationError("Failed to authenticate with GitHub")
    
    logger.info("Quick start completed successfully")
    return hub

__all__ = [
    'MeroHub',
    'GitHubCore',
    'GitHubAuth',
    'GitHubConfig',
    'RepositoryManager',
    'GitHubSearch',
    'UserManager',
    'IssueManager',
    'PullRequestManager',
    'GitOperations',
    'AIAnalyzer',
    'NeuralNetworkAnalyzer',
    'MLPredictor',
    'GitHubBot',
    'AutomatedInteractions',
    'SmartResponder',
    'Logger',
    'ConfigManager',
    'SecurityManager',
    'DataProcessor',
    'MeroHubError',
    'AuthenticationError',
    'APIError',
    'ValidationError',
    'quick_start',
    'configure_logging',
    'get_system_info',
    'check_compatibility'
]