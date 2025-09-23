"""
MeroHub Advanced GitHub Search Module
Author: MERO (Telegram: @QP4RM)

Comprehensive search functionality for GitHub repositories, users, code, issues,
and pull requests with advanced filtering, analytics, and trending analysis.
"""

import re
import time
import json
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from urllib.parse import quote, urlencode
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict, Counter
import statistics
from .exceptions import SearchError, ValidationError, APIError
from .utils import Logger, DataProcessor, retry_on_exception, timed_cache


@dataclass 
class SearchQuery:
    """Structured search query container."""
    
    query: str
    sort: str = "updated"
    order: str = "desc"
    per_page: int = 30
    page: int = 1
    language: Optional[str] = None
    user: Optional[str] = None
    org: Optional[str] = None
    repo: Optional[str] = None
    size: Optional[str] = None
    followers: Optional[str] = None
    forks: Optional[str] = None
    stars: Optional[str] = None
    created: Optional[str] = None
    pushed: Optional[str] = None
    topic: Optional[str] = None
    license: Optional[str] = None
    is_public: Optional[bool] = None
    is_private: Optional[bool] = None
    is_fork: Optional[bool] = None
    is_archived: Optional[bool] = None
    has_issues: Optional[bool] = None
    has_projects: Optional[bool] = None
    has_wiki: Optional[bool] = None
    custom_filters: Dict[str, Any] = field(default_factory=dict)
    
    def to_github_query(self) -> str:
        """Convert to GitHub search query string."""
        query_parts = [self.query] if self.query else []
        
        # Add filters
        if self.language:
            query_parts.append(f"language:{self.language}")
        if self.user:
            query_parts.append(f"user:{self.user}")
        if self.org:
            query_parts.append(f"org:{self.org}")
        if self.repo:
            query_parts.append(f"repo:{self.repo}")
        if self.size:
            query_parts.append(f"size:{self.size}")
        if self.followers:
            query_parts.append(f"followers:{self.followers}")
        if self.forks:
            query_parts.append(f"forks:{self.forks}")
        if self.stars:
            query_parts.append(f"stars:{self.stars}")
        if self.created:
            query_parts.append(f"created:{self.created}")
        if self.pushed:
            query_parts.append(f"pushed:{self.pushed}")
        if self.topic:
            query_parts.append(f"topic:{self.topic}")
        if self.license:
            query_parts.append(f"license:{self.license}")
        
        # Boolean filters
        if self.is_public is not None:
            query_parts.append("is:public" if self.is_public else "is:private")
        if self.is_fork is not None:
            query_parts.append("fork:true" if self.is_fork else "fork:false")
        if self.is_archived is not None:
            query_parts.append("archived:true" if self.is_archived else "archived:false")
        if self.has_issues is not None:
            query_parts.append("has:issues" if self.has_issues else "-has:issues")
        if self.has_projects is not None:
            query_parts.append("has:projects" if self.has_projects else "-has:projects")
        if self.has_wiki is not None:
            query_parts.append("has:wiki" if self.has_wiki else "-has:wiki")
        
        # Custom filters
        for key, value in self.custom_filters.items():
            query_parts.append(f"{key}:{value}")
        
        return " ".join(query_parts)


@dataclass
class SearchResult:
    """Search result container with metadata."""
    
    items: List[Dict[str, Any]]
    total_count: int
    incomplete_results: bool
    search_metadata: Dict[str, Any]
    query_info: Dict[str, Any]
    performance_metrics: Dict[str, Any]


class GitHubSearch:
    """Core GitHub search functionality."""
    
    def __init__(self, core):
        self.core = core
        self.logger = Logger("GitHubSearch")
        self.data_processor = DataProcessor()
        self.search_cache = {}
        self.search_stats = {
            'total_searches': 0,
            'cache_hits': 0,
            'search_types': defaultdict(int),
            'popular_queries': Counter(),
            'average_response_time': 0.0
        }
    
    @retry_on_exception(max_retries=3, delay=1.0)
    @timed_cache(seconds=180)  # Cache searches for 3 minutes
    def search_repositories(self, query: Union[str, SearchQuery],
                          sort: str = "updated",
                          order: str = "desc", 
                          per_page: int = 30,
                          max_pages: int = 10,
                          **kwargs) -> SearchResult:
        """Search GitHub repositories with comprehensive filtering."""
        
        start_time = time.time()
        self.logger.info(f"Searching repositories: {query}")
        
        # Convert to SearchQuery if needed
        if isinstance(query, str):
            search_query = SearchQuery(
                query=query,
                sort=sort,
                order=order,
                per_page=per_page,
                **kwargs
            )
        else:
            search_query = query
        
        try:
            # Build search parameters
            github_query = search_query.to_github_query()
            params = {
                'q': github_query,
                'sort': search_query.sort,
                'order': search_query.order,
                'per_page': min(search_query.per_page, 100)
            }
            
            # Perform paginated search
            all_items = []
            total_count = 0
            incomplete_results = False
            
            for page in range(1, max_pages + 1):
                params['page'] = page
                
                try:
                    response = self.core.get('/search/repositories', params=params)
                    data = response.json()
                    
                    if page == 1:
                        total_count = data.get('total_count', 0)
                        incomplete_results = data.get('incomplete_results', False)
                    
                    items = data.get('items', [])
                    if not items:
                        break
                    
                    all_items.extend(items)
                    
                    # Stop if we have all results
                    if len(all_items) >= total_count:
                        break
                        
                except APIError as e:
                    if e.status_code == 422:  # Validation failed
                        self.logger.warning(f"Search validation failed: {e}")
                        break
                    elif e.is_rate_limited():
                        self.logger.warning("Search rate limited, waiting...")
                        time.sleep(60)
                        continue
                    else:
                        raise
            
            # Performance metrics
            end_time = time.time()
            performance_metrics = {
                'query_time': end_time - start_time,
                'pages_fetched': min(page, max_pages),
                'items_returned': len(all_items),
                'api_calls': min(page, max_pages)
            }
            
            # Update statistics
            self._update_search_stats('repositories', github_query, performance_metrics['query_time'])
            
            result = SearchResult(
                items=all_items,
                total_count=total_count,
                incomplete_results=incomplete_results,
                search_metadata={
                    'search_type': 'repositories',
                    'original_query': query,
                    'github_query': github_query,
                    'timestamp': datetime.now().isoformat()
                },
                query_info=search_query.__dict__,
                performance_metrics=performance_metrics
            )
            
            self.logger.info(f"Repository search completed: {len(all_items)} results")
            return result
            
        except Exception as e:
            raise SearchError(f"Repository search failed: {e}",
                            query=str(query), search_type="repositories")
    
    @timed_cache(seconds=300)
    def search_users(self, query: str,
                    sort: str = "followers",
                    order: str = "desc",
                    per_page: int = 30,
                    max_pages: int = 5) -> SearchResult:
        """Search GitHub users."""
        
        start_time = time.time()
        self.logger.info(f"Searching users: {query}")
        
        try:
            params = {
                'q': query,
                'sort': sort,
                'order': order,
                'per_page': min(per_page, 100)
            }
            
            all_items = []
            total_count = 0
            incomplete_results = False
            
            for page in range(1, max_pages + 1):
                params['page'] = page
                
                response = self.core.get('/search/users', params=params)
                data = response.json()
                
                if page == 1:
                    total_count = data.get('total_count', 0)
                    incomplete_results = data.get('incomplete_results', False)
                
                items = data.get('items', [])
                if not items:
                    break
                
                all_items.extend(items)
            
            # Performance metrics
            end_time = time.time()
            performance_metrics = {
                'query_time': end_time - start_time,
                'pages_fetched': min(page, max_pages),
                'items_returned': len(all_items),
                'api_calls': min(page, max_pages)
            }
            
            self._update_search_stats('users', query, performance_metrics['query_time'])
            
            return SearchResult(
                items=all_items,
                total_count=total_count,
                incomplete_results=incomplete_results,
                search_metadata={
                    'search_type': 'users',
                    'query': query,
                    'timestamp': datetime.now().isoformat()
                },
                query_info={'query': query, 'sort': sort, 'order': order},
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            raise SearchError(f"User search failed: {e}",
                            query=query, search_type="users")
    
    @timed_cache(seconds=180)
    def search_code(self, query: str,
                   sort: str = "indexed",
                   order: str = "desc",
                   per_page: int = 30,
                   max_pages: int = 5) -> SearchResult:
        """Search code in GitHub repositories."""
        
        start_time = time.time()
        self.logger.info(f"Searching code: {query}")
        
        try:
            params = {
                'q': query,
                'sort': sort,
                'order': order,
                'per_page': min(per_page, 100)
            }
            
            all_items = []
            total_count = 0
            incomplete_results = False
            
            for page in range(1, max_pages + 1):
                params['page'] = page
                
                response = self.core.get('/search/code', params=params)
                data = response.json()
                
                if page == 1:
                    total_count = data.get('total_count', 0)
                    incomplete_results = data.get('incomplete_results', False)
                
                items = data.get('items', [])
                if not items:
                    break
                
                all_items.extend(items)
            
            # Performance metrics
            end_time = time.time()
            performance_metrics = {
                'query_time': end_time - start_time,
                'pages_fetched': min(page, max_pages),
                'items_returned': len(all_items),
                'api_calls': min(page, max_pages)
            }
            
            self._update_search_stats('code', query, performance_metrics['query_time'])
            
            return SearchResult(
                items=all_items,
                total_count=total_count,
                incomplete_results=incomplete_results,
                search_metadata={
                    'search_type': 'code',
                    'query': query,
                    'timestamp': datetime.now().isoformat()
                },
                query_info={'query': query, 'sort': sort, 'order': order},
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            raise SearchError(f"Code search failed: {e}",
                            query=query, search_type="code")
    
    @timed_cache(seconds=300)
    def search_issues(self, query: str,
                     sort: str = "updated",
                     order: str = "desc",
                     per_page: int = 30,
                     max_pages: int = 5) -> SearchResult:
        """Search GitHub issues and pull requests."""
        
        start_time = time.time()
        self.logger.info(f"Searching issues: {query}")
        
        try:
            params = {
                'q': query,
                'sort': sort,
                'order': order,
                'per_page': min(per_page, 100)
            }
            
            all_items = []
            total_count = 0
            incomplete_results = False
            
            for page in range(1, max_pages + 1):
                params['page'] = page
                
                response = self.core.get('/search/issues', params=params)
                data = response.json()
                
                if page == 1:
                    total_count = data.get('total_count', 0)
                    incomplete_results = data.get('incomplete_results', False)
                
                items = data.get('items', [])
                if not items:
                    break
                
                all_items.extend(items)
            
            # Performance metrics
            end_time = time.time()
            performance_metrics = {
                'query_time': end_time - start_time,
                'pages_fetched': min(page, max_pages),
                'items_returned': len(all_items),
                'api_calls': min(page, max_pages)
            }
            
            self._update_search_stats('issues', query, performance_metrics['query_time'])
            
            return SearchResult(
                items=all_items,
                total_count=total_count,
                incomplete_results=incomplete_results,
                search_metadata={
                    'search_type': 'issues',
                    'query': query,
                    'timestamp': datetime.now().isoformat()
                },
                query_info={'query': query, 'sort': sort, 'order': order},
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            raise SearchError(f"Issues search failed: {e}",
                            query=query, search_type="issues")
    
    @timed_cache(seconds=600)  # Cache for 10 minutes
    def search_commits(self, query: str,
                      sort: str = "author-date",
                      order: str = "desc",
                      per_page: int = 30,
                      max_pages: int = 3) -> SearchResult:
        """Search GitHub commits."""
        
        start_time = time.time()
        self.logger.info(f"Searching commits: {query}")
        
        try:
            params = {
                'q': query,
                'sort': sort,
                'order': order,
                'per_page': min(per_page, 100)
            }
            
            all_items = []
            total_count = 0
            incomplete_results = False
            
            for page in range(1, max_pages + 1):
                params['page'] = page
                
                response = self.core.get('/search/commits', params=params)
                data = response.json()
                
                if page == 1:
                    total_count = data.get('total_count', 0)
                    incomplete_results = data.get('incomplete_results', False)
                
                items = data.get('items', [])
                if not items:
                    break
                
                all_items.extend(items)
            
            # Performance metrics
            end_time = time.time()
            performance_metrics = {
                'query_time': end_time - start_time,
                'pages_fetched': min(page, max_pages),
                'items_returned': len(all_items),
                'api_calls': min(page, max_pages)
            }
            
            self._update_search_stats('commits', query, performance_metrics['query_time'])
            
            return SearchResult(
                items=all_items,
                total_count=total_count,
                incomplete_results=incomplete_results,
                search_metadata={
                    'search_type': 'commits',
                    'query': query,
                    'timestamp': datetime.now().isoformat()
                },
                query_info={'query': query, 'sort': sort, 'order': order},
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            raise SearchError(f"Commits search failed: {e}",
                            query=query, search_type="commits")
    
    def _update_search_stats(self, search_type: str, query: str, response_time: float):
        """Update search statistics."""
        self.search_stats['total_searches'] += 1
        self.search_stats['search_types'][search_type] += 1
        self.search_stats['popular_queries'][query[:100]] += 1  # Limit query length
        
        # Update average response time
        total_time = (self.search_stats['average_response_time'] * 
                     (self.search_stats['total_searches'] - 1) + response_time)
        self.search_stats['average_response_time'] = total_time / self.search_stats['total_searches']
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search usage statistics."""
        return {
            'total_searches': self.search_stats['total_searches'],
            'cache_hits': self.search_stats['cache_hits'],
            'search_types': dict(self.search_stats['search_types']),
            'popular_queries': self.search_stats['popular_queries'].most_common(10),
            'average_response_time': self.search_stats['average_response_time']
        }


class AdvancedSearch:
    """Advanced search functionality with filtering and analytics."""
    
    def __init__(self, core):
        self.core = core
        self.basic_search = GitHubSearch(core)
        self.logger = Logger("AdvancedSearch")
        self.data_processor = DataProcessor()
    
    def smart_repository_search(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligent repository search with multiple criteria."""
        
        self.logger.info("Performing smart repository search")
        
        # Build query from criteria
        query_builder = self._build_smart_query(criteria)
        
        # Perform search
        search_result = self.basic_search.search_repositories(
            query_builder['query'],
            sort=criteria.get('sort', 'stars'),
            order=criteria.get('order', 'desc'),
            per_page=criteria.get('per_page', 50),
            max_pages=criteria.get('max_pages', 5)
        )
        
        # Post-process results
        processed_results = self._post_process_results(search_result.items, criteria)
        
        # Generate insights
        insights = self._generate_search_insights(processed_results, criteria)
        
        return {
            'results': processed_results,
            'total_found': search_result.total_count,
            'query_used': query_builder['query'],
            'filters_applied': query_builder['filters'],
            'insights': insights,
            'search_metadata': search_result.search_metadata,
            'performance': search_result.performance_metrics
        }
    
    def _build_smart_query(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Build intelligent search query from criteria."""
        
        query_parts = []
        applied_filters = []
        
        # Basic search terms
        if criteria.get('keywords'):
            keywords = criteria['keywords']
            if isinstance(keywords, list):
                query_parts.extend(keywords)
            else:
                query_parts.append(str(keywords))
            applied_filters.append(f"keywords: {keywords}")
        
        # Language filter
        if criteria.get('language'):
            query_parts.append(f"language:{criteria['language']}")
            applied_filters.append(f"language: {criteria['language']}")
        
        # Stars filter
        if criteria.get('min_stars'):
            query_parts.append(f"stars:>={criteria['min_stars']}")
            applied_filters.append(f"min_stars: {criteria['min_stars']}")
        if criteria.get('max_stars'):
            query_parts.append(f"stars:<={criteria['max_stars']}")
            applied_filters.append(f"max_stars: {criteria['max_stars']}")
        
        # Forks filter
        if criteria.get('min_forks'):
            query_parts.append(f"forks:>={criteria['min_forks']}")
            applied_filters.append(f"min_forks: {criteria['min_forks']}")
        
        # Size filter (in KB)
        if criteria.get('min_size'):
            query_parts.append(f"size:>={criteria['min_size']}")
            applied_filters.append(f"min_size: {criteria['min_size']}")
        if criteria.get('max_size'):
            query_parts.append(f"size:<={criteria['max_size']}")
            applied_filters.append(f"max_size: {criteria['max_size']}")
        
        # Date filters
        if criteria.get('created_after'):
            query_parts.append(f"created:>={criteria['created_after']}")
            applied_filters.append(f"created_after: {criteria['created_after']}")
        if criteria.get('updated_after'):
            query_parts.append(f"pushed:>={criteria['updated_after']}")
            applied_filters.append(f"updated_after: {criteria['updated_after']}")
        
        # Topic filter
        if criteria.get('topics'):
            topics = criteria['topics']
            if isinstance(topics, list):
                for topic in topics:
                    query_parts.append(f"topic:{topic}")
            else:
                query_parts.append(f"topic:{topics}")
            applied_filters.append(f"topics: {topics}")
        
        # License filter
        if criteria.get('license'):
            query_parts.append(f"license:{criteria['license']}")
            applied_filters.append(f"license: {criteria['license']}")
        
        # Boolean filters
        if criteria.get('has_issues') is not None:
            if criteria['has_issues']:
                query_parts.append("has:issues")
            else:
                query_parts.append("-has:issues")
            applied_filters.append(f"has_issues: {criteria['has_issues']}")
        
        if criteria.get('has_wiki') is not None:
            if criteria['has_wiki']:
                query_parts.append("has:wiki")
            else:
                query_parts.append("-has:wiki")
            applied_filters.append(f"has_wiki: {criteria['has_wiki']}")
        
        if criteria.get('is_fork') is not None:
            query_parts.append("fork:true" if criteria['is_fork'] else "fork:false")
            applied_filters.append(f"is_fork: {criteria['is_fork']}")
        
        if criteria.get('is_archived') is not None:
            query_parts.append("archived:true" if criteria['is_archived'] else "archived:false")
            applied_filters.append(f"is_archived: {criteria['is_archived']}")
        
        # User or organization filter
        if criteria.get('user'):
            query_parts.append(f"user:{criteria['user']}")
            applied_filters.append(f"user: {criteria['user']}")
        if criteria.get('org'):
            query_parts.append(f"org:{criteria['org']}")
            applied_filters.append(f"org: {criteria['org']}")
        
        query = " ".join(query_parts) if query_parts else "*"
        
        return {
            'query': query,
            'filters': applied_filters
        }
    
    def _post_process_results(self, results: List[Dict[str, Any]], 
                            criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Post-process search results with additional filtering and enrichment."""
        
        processed = []
        
        for repo in results:
            # Add calculated fields
            repo_data = repo.copy()
            
            # Calculate popularity score
            stars = repo_data.get('stargazers_count', 0)
            forks = repo_data.get('forks_count', 0)
            watchers = repo_data.get('watchers_count', 0)
            
            import math
            popularity_score = (
                math.log10(stars + 1) * 3 +
                math.log10(forks + 1) * 2 +
                math.log10(watchers + 1) * 1
            ) * 10
            
            repo_data['popularity_score'] = round(popularity_score, 2)
            
            # Calculate freshness score
            if repo_data.get('pushed_at'):
                pushed_date = datetime.fromisoformat(repo_data['pushed_at'].replace('Z', '+00:00'))
                days_since_update = (datetime.now(pushed_date.tzinfo) - pushed_date).days
                freshness_score = max(0, 100 - (days_since_update / 30) * 10)
                repo_data['freshness_score'] = round(freshness_score, 2)
            else:
                repo_data['freshness_score'] = 0
            
            # Calculate activity score
            open_issues = repo_data.get('open_issues_count', 0)
            activity_score = min(100, open_issues * 2 + forks * 5 + stars * 0.1)
            repo_data['activity_score'] = round(activity_score, 2)
            
            # Add language percentage if available
            if repo_data.get('language'):
                repo_data['primary_language'] = repo_data['language']
            
            # Apply additional custom filters
            if self._passes_custom_filters(repo_data, criteria):
                processed.append(repo_data)
        
        # Apply custom sorting
        if criteria.get('custom_sort'):
            processed = self._apply_custom_sorting(processed, criteria['custom_sort'])
        
        # Limit results if specified
        if criteria.get('limit'):
            processed = processed[:criteria['limit']]
        
        return processed
    
    def _passes_custom_filters(self, repo: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Apply custom filtering logic."""
        
        # Minimum popularity score filter
        if criteria.get('min_popularity_score'):
            if repo.get('popularity_score', 0) < criteria['min_popularity_score']:
                return False
        
        # Minimum freshness score filter
        if criteria.get('min_freshness_score'):
            if repo.get('freshness_score', 0) < criteria['min_freshness_score']:
                return False
        
        # Language exclusions
        if criteria.get('exclude_languages'):
            if repo.get('language') in criteria['exclude_languages']:
                return False
        
        # Keyword exclusions in name or description
        if criteria.get('exclude_keywords'):
            name = repo.get('name', '').lower()
            desc = repo.get('description', '').lower() if repo.get('description') else ''
            
            for keyword in criteria['exclude_keywords']:
                if keyword.lower() in name or keyword.lower() in desc:
                    return False
        
        return True
    
    def _apply_custom_sorting(self, repos: List[Dict[str, Any]], 
                            sort_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply custom sorting to repositories."""
        
        sort_key = sort_config.get('key', 'stargazers_count')
        sort_order = sort_config.get('order', 'desc')
        secondary_key = sort_config.get('secondary_key')
        
        def get_sort_value(repo):
            value = repo.get(sort_key, 0)
            if secondary_key:
                secondary_value = repo.get(secondary_key, 0)
                return (value, secondary_value)
            return value
        
        reverse = sort_order.lower() == 'desc'
        return sorted(repos, key=get_sort_value, reverse=reverse)
    
    def _generate_search_insights(self, results: List[Dict[str, Any]], 
                                criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from search results."""
        
        if not results:
            return {'message': 'No results found'}
        
        insights = {}
        
        # Language distribution
        languages = [repo.get('language') for repo in results if repo.get('language')]
        if languages:
            lang_counter = Counter(languages)
            insights['top_languages'] = lang_counter.most_common(5)
        
        # License distribution  
        licenses = [repo.get('license', {}).get('name') for repo in results 
                   if repo.get('license', {}).get('name')]
        if licenses:
            license_counter = Counter(licenses)
            insights['top_licenses'] = license_counter.most_common(5)
        
        # Statistics
        stars = [repo.get('stargazers_count', 0) for repo in results]
        forks = [repo.get('forks_count', 0) for repo in results]
        sizes = [repo.get('size', 0) for repo in results]
        
        insights['statistics'] = {
            'total_repositories': len(results),
            'stars': {
                'total': sum(stars),
                'average': statistics.mean(stars) if stars else 0,
                'median': statistics.median(stars) if stars else 0,
                'max': max(stars) if stars else 0
            },
            'forks': {
                'total': sum(forks),
                'average': statistics.mean(forks) if forks else 0,
                'median': statistics.median(forks) if forks else 0,
                'max': max(forks) if forks else 0
            },
            'sizes': {
                'average_mb': statistics.mean(sizes) / 1024 if sizes else 0,
                'median_mb': statistics.median(sizes) / 1024 if sizes else 0,
                'total_gb': sum(sizes) / (1024 * 1024) if sizes else 0
            }
        }
        
        # Quality insights
        quality_scores = []
        for repo in results:
            score = 0
            if repo.get('description'):
                score += 20
            if repo.get('license'):
                score += 20  
            if repo.get('has_issues'):
                score += 15
            if repo.get('has_wiki'):
                score += 15
            if repo.get('stargazers_count', 0) > 100:
                score += 30
                
            quality_scores.append(score)
        
        if quality_scores:
            insights['quality_analysis'] = {
                'average_quality_score': statistics.mean(quality_scores),
                'high_quality_repos': len([s for s in quality_scores if s >= 80]),
                'medium_quality_repos': len([s for s in quality_scores if 50 <= s < 80]),
                'low_quality_repos': len([s for s in quality_scores if s < 50])
            }
        
        # Trending analysis
        recent_repos = []
        for repo in results:
            if repo.get('created_at'):
                created_date = datetime.fromisoformat(repo['created_at'].replace('Z', '+00:00'))
                if (datetime.now(created_date.tzinfo) - created_date).days <= 365:  # Last year
                    recent_repos.append(repo)
        
        insights['trends'] = {
            'recent_repositories': len(recent_repos),
            'percentage_recent': (len(recent_repos) / len(results)) * 100 if results else 0
        }
        
        return insights
    
    @timed_cache(seconds=1800)  # Cache for 30 minutes
    def get_trending_repositories(self, language: Optional[str] = None,
                                since: str = "daily") -> List[Dict[str, Any]]:
        """Get trending repositories (simulated since GitHub doesn't have trending API)."""
        
        self.logger.info(f"Getting trending repositories: {language}, {since}")
        
        # Calculate date range based on 'since' parameter
        if since == "daily":
            date_filter = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        elif since == "weekly":
            date_filter = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        elif since == "monthly":
            date_filter = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        else:
            date_filter = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Build search criteria for trending repos
        criteria = {
            'keywords': [],
            'created_after': date_filter,
            'min_stars': 50,  # Minimum stars to be considered trending
            'sort': 'stars',
            'order': 'desc',
            'per_page': 50,
            'max_pages': 2
        }
        
        if language:
            criteria['language'] = language
        
        # Use smart search
        trending_data = self.smart_repository_search(criteria)
        
        # Calculate trending score for each repo
        for repo in trending_data['results']:
            trending_score = self._calculate_trending_score(repo, since)
            repo['trending_score'] = trending_score
        
        # Sort by trending score
        trending_repos = sorted(trending_data['results'], 
                              key=lambda x: x.get('trending_score', 0), 
                              reverse=True)
        
        return trending_repos[:30]  # Return top 30
    
    def _calculate_trending_score(self, repo: Dict[str, Any], timeframe: str) -> float:
        """Calculate trending score for a repository."""
        
        # Base score from stars and forks
        stars = repo.get('stargazers_count', 0)
        forks = repo.get('forks_count', 0)
        watchers = repo.get('watchers_count', 0)
        
        base_score = stars * 1.0 + forks * 2.0 + watchers * 0.5
        
        # Time decay factor
        created_at = repo.get('created_at')
        if created_at:
            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            days_old = (datetime.now(created_date.tzinfo) - created_date).days
            
            # Newer repos get higher trending scores
            if timeframe == "daily":
                time_factor = max(0.1, 1.0 - (days_old / 30))  # Decay over 30 days
            elif timeframe == "weekly": 
                time_factor = max(0.1, 1.0 - (days_old / 90))  # Decay over 90 days
            else:  # monthly
                time_factor = max(0.1, 1.0 - (days_old / 365))  # Decay over 1 year
        else:
            time_factor = 0.1
        
        # Activity factor
        activity_factor = 1.0
        if repo.get('open_issues_count', 0) > 10:
            activity_factor += 0.2
        if repo.get('has_issues') and repo.get('has_wiki'):
            activity_factor += 0.1
        
        # Language bonus (popular languages get slight boost)
        popular_languages = {'JavaScript', 'Python', 'TypeScript', 'Java', 'Go', 'Rust'}
        language_factor = 1.1 if repo.get('language') in popular_languages else 1.0
        
        trending_score = base_score * time_factor * activity_factor * language_factor
        
        return round(trending_score, 2)


class SearchAnalytics:
    """Analytics and insights for search operations."""
    
    def __init__(self, core):
        self.core = core
        self.search = AdvancedSearch(core)
        self.logger = Logger("SearchAnalytics")
        self.data_processor = DataProcessor()
    
    def analyze_search_landscape(self, topic: str, 
                                timeframe_days: int = 365) -> Dict[str, Any]:
        """Analyze the GitHub landscape for a specific topic."""
        
        self.logger.info(f"Analyzing search landscape for: {topic}")
        
        # Define search date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=timeframe_days)
        
        # Multiple search perspectives
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                'repositories': executor.submit(
                    self._analyze_repositories_landscape, topic, start_date, end_date
                ),
                'users': executor.submit(
                    self._analyze_users_landscape, topic
                ),
                'code_patterns': executor.submit(
                    self._analyze_code_landscape, topic
                ),
                'issues_trends': executor.submit(
                    self._analyze_issues_landscape, topic, start_date, end_date
                ),
                'language_distribution': executor.submit(
                    self._analyze_language_distribution, topic
                )
            }
            
            landscape_data = {}
            for key, future in futures.items():
                try:
                    landscape_data[key] = future.result(timeout=60)
                except Exception as e:
                    self.logger.error(f"Failed to analyze {key}: {e}")
                    landscape_data[key] = {'error': str(e)}
        
        # Generate comprehensive insights
        insights = self._generate_landscape_insights(landscape_data, topic)
        
        return {
            'topic': topic,
            'timeframe_days': timeframe_days,
            'analysis_date': datetime.now().isoformat(),
            'landscape_data': landscape_data,
            'insights': insights,
            'recommendations': self._generate_landscape_recommendations(landscape_data, topic)
        }
    
    def _analyze_repositories_landscape(self, topic: str, start_date: datetime, 
                                      end_date: datetime) -> Dict[str, Any]:
        """Analyze repository landscape for a topic."""
        
        criteria = {
            'keywords': [topic],
            'created_after': start_date.strftime('%Y-%m-%d'),
            'sort': 'stars',
            'order': 'desc',
            'per_page': 100,
            'max_pages': 3
        }
        
        search_results = self.search.smart_repository_search(criteria)
        repos = search_results['results']
        
        # Analyze trends
        monthly_creation = defaultdict(int)
        language_trends = defaultdict(int)
        star_distribution = []
        
        for repo in repos:
            # Monthly creation trend
            if repo.get('created_at'):
                created_date = datetime.fromisoformat(repo['created_at'].replace('Z', '+00:00'))
                month_key = created_date.strftime('%Y-%m')
                monthly_creation[month_key] += 1
            
            # Language distribution
            if repo.get('language'):
                language_trends[repo['language']] += 1
            
            # Star distribution
            star_distribution.append(repo.get('stargazers_count', 0))
        
        return {
            'total_repositories': len(repos),
            'monthly_creation_trend': dict(monthly_creation),
            'top_languages': dict(Counter(language_trends).most_common(10)),
            'star_statistics': {
                'total': sum(star_distribution),
                'average': statistics.mean(star_distribution) if star_distribution else 0,
                'median': statistics.median(star_distribution) if star_distribution else 0,
                'top_repos': sorted(repos, key=lambda x: x.get('stargazers_count', 0), 
                                  reverse=True)[:10]
            }
        }
    
    def _analyze_users_landscape(self, topic: str) -> Dict[str, Any]:
        """Analyze user landscape for a topic."""
        
        search_result = self.search.basic_search.search_users(
            query=topic,
            sort='followers',
            order='desc',
            per_page=100,
            max_pages=2
        )
        
        users = search_result.items
        follower_counts = [user.get('followers', 0) for user in users]
        repo_counts = [user.get('public_repos', 0) for user in users]
        
        return {
            'total_users': len(users),
            'top_influencers': sorted(users, key=lambda x: x.get('followers', 0), 
                                    reverse=True)[:10],
            'follower_statistics': {
                'total': sum(follower_counts),
                'average': statistics.mean(follower_counts) if follower_counts else 0,
                'median': statistics.median(follower_counts) if follower_counts else 0
            },
            'repository_statistics': {
                'average_repos_per_user': statistics.mean(repo_counts) if repo_counts else 0,
                'total_public_repos': sum(repo_counts)
            }
        }
    
    def _analyze_code_landscape(self, topic: str) -> Dict[str, Any]:
        """Analyze code patterns for a topic."""
        
        search_result = self.search.basic_search.search_code(
            query=topic,
            sort='indexed',
            order='desc',
            per_page=100,
            max_pages=2
        )
        
        code_files = search_result.items
        
        # Analyze file types and repositories
        file_extensions = defaultdict(int)
        repositories = defaultdict(int)
        
        for code_file in code_files:
            if code_file.get('name'):
                ext = code_file['name'].split('.')[-1] if '.' in code_file['name'] else 'unknown'
                file_extensions[ext] += 1
            
            if code_file.get('repository'):
                repo_full_name = code_file['repository'].get('full_name')
                if repo_full_name:
                    repositories[repo_full_name] += 1
        
        return {
            'total_code_files': len(code_files),
            'file_type_distribution': dict(Counter(file_extensions).most_common(10)),
            'most_active_repositories': dict(Counter(repositories).most_common(10))
        }
    
    def _analyze_issues_landscape(self, topic: str, start_date: datetime, 
                                end_date: datetime) -> Dict[str, Any]:
        """Analyze issues and discussions for a topic."""
        
        # Search for issues
        query = f"{topic} created:>={start_date.strftime('%Y-%m-%d')}"
        search_result = self.search.basic_search.search_issues(
            query=query,
            sort='updated',
            order='desc',
            per_page=100,
            max_pages=2
        )
        
        issues = search_result.items
        
        # Analyze issue patterns
        state_distribution = defaultdict(int)
        label_frequency = defaultdict(int)
        monthly_creation = defaultdict(int)
        
        for issue in issues:
            # State distribution
            state_distribution[issue.get('state', 'unknown')] += 1
            
            # Label analysis
            for label in issue.get('labels', []):
                label_frequency[label.get('name', '')] += 1
            
            # Monthly creation trend
            if issue.get('created_at'):
                created_date = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
                month_key = created_date.strftime('%Y-%m')
                monthly_creation[month_key] += 1
        
        return {
            'total_issues': len(issues),
            'state_distribution': dict(state_distribution),
            'common_labels': dict(Counter(label_frequency).most_common(10)),
            'monthly_trend': dict(monthly_creation)
        }
    
    def _analyze_language_distribution(self, topic: str) -> Dict[str, Any]:
        """Analyze programming language distribution for a topic."""
        
        # Get repositories for different popular languages
        languages = ['JavaScript', 'Python', 'TypeScript', 'Java', 'Go', 'Rust', 'C++', 'C#']
        
        language_analysis = {}
        
        with ThreadPoolExecutor(max_workers=len(languages)) as executor:
            future_to_lang = {}
            
            for language in languages:
                criteria = {
                    'keywords': [topic],
                    'language': language,
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': 30,
                    'max_pages': 1
                }
                future = executor.submit(self.search.smart_repository_search, criteria)
                future_to_lang[future] = language
            
            for future in as_completed(future_to_lang):
                language = future_to_lang[future]
                try:
                    result = future.result(timeout=30)
                    repos = result['results']
                    
                    total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
                    total_forks = sum(repo.get('forks_count', 0) for repo in repos)
                    
                    language_analysis[language] = {
                        'repository_count': len(repos),
                        'total_stars': total_stars,
                        'total_forks': total_forks,
                        'average_stars': total_stars / len(repos) if repos else 0,
                        'top_repos': repos[:5]  # Top 5 repos
                    }
                except Exception as e:
                    self.logger.error(f"Failed to analyze {language}: {e}")
                    language_analysis[language] = {'error': str(e)}
        
        return language_analysis
    
    def _generate_landscape_insights(self, data: Dict[str, Any], topic: str) -> List[str]:
        """Generate insights from landscape analysis."""
        
        insights = []
        
        # Repository insights
        repo_data = data.get('repositories', {})
        if repo_data and not repo_data.get('error'):
            total_repos = repo_data.get('total_repositories', 0)
            insights.append(f"📊 Found {total_repos:,} repositories related to {topic}")
            
            if repo_data.get('top_languages'):
                top_lang = list(repo_data['top_languages'].keys())[0]
                insights.append(f"🔥 {top_lang} is the most popular language for {topic}")
        
        # User insights
        user_data = data.get('users', {})
        if user_data and not user_data.get('error'):
            total_users = user_data.get('total_users', 0)
            insights.append(f"👥 {total_users:,} developers are actively working with {topic}")
        
        # Language distribution insights
        lang_data = data.get('language_distribution', {})
        if lang_data:
            # Find most active language by repository count
            most_active = max(
                [(lang, info.get('repository_count', 0)) for lang, info in lang_data.items()
                 if isinstance(info, dict) and not info.get('error')],
                key=lambda x: x[1],
                default=(None, 0)
            )
            
            if most_active[0]:
                insights.append(f"🚀 {most_active[0]} has the most active {topic} ecosystem")
        
        # Issues insights
        issues_data = data.get('issues_trends', {})
        if issues_data and not issues_data.get('error'):
            total_issues = issues_data.get('total_issues', 0)
            if total_issues > 100:
                insights.append(f"💬 Very active community with {total_issues:,} recent discussions")
            elif total_issues > 10:
                insights.append(f"💬 Moderate community activity with {total_issues} recent discussions")
        
        return insights
    
    def _generate_landscape_recommendations(self, data: Dict[str, Any], 
                                          topic: str) -> List[str]:
        """Generate actionable recommendations from landscape analysis."""
        
        recommendations = []
        
        # Language recommendations
        lang_data = data.get('language_distribution', {})
        if lang_data:
            # Find languages with high activity
            active_languages = []
            for lang, info in lang_data.items():
                if (isinstance(info, dict) and not info.get('error') and 
                    info.get('repository_count', 0) > 10):
                    active_languages.append((lang, info['repository_count']))
            
            if active_languages:
                top_3_langs = sorted(active_languages, key=lambda x: x[1], reverse=True)[:3]
                lang_list = ", ".join([lang for lang, _ in top_3_langs])
                recommendations.append(f"🎯 Focus on {lang_list} for maximum community reach")
        
        # Repository recommendations
        repo_data = data.get('repositories', {})
        if repo_data and not repo_data.get('error'):
            if repo_data.get('star_statistics', {}).get('average', 0) > 100:
                recommendations.append("⭐ High-quality ecosystem - contribute to existing projects")
            else:
                recommendations.append("🚀 Emerging field - opportunity for innovative projects")
        
        # Community recommendations
        user_data = data.get('users', {})
        if user_data and not user_data.get('error'):
            avg_followers = user_data.get('follower_statistics', {}).get('average', 0)
            if avg_followers > 1000:
                recommendations.append("🌟 Connect with established influencers in the community")
            else:
                recommendations.append("🤝 Great opportunity to become a thought leader")
        
        return recommendations


__all__ = [
    'GitHubSearch',
    'AdvancedSearch', 
    'SearchAnalytics',
    'SearchQuery',
    'SearchResult'
]