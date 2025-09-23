"""
MeroHub Automation Module
Author: MERO (Telegram: @QP4RM)

Advanced GitHub automation, bot interactions, and intelligent response systems.
Provides automated workflows, smart notifications, and AI-powered communication.
"""

import json
import time
import asyncio
import threading
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import re
import hashlib
import hmac
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
import schedule
from .exceptions import AutomationError, ValidationError, WebhookError
from .utils import Logger, DataProcessor, ConfigManager


@dataclass
class AutomationRule:
    """Automation rule configuration."""
    
    name: str
    trigger: str
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    enabled: bool = True
    priority: int = 0
    cooldown_minutes: int = 0
    last_executed: Optional[datetime] = None


@dataclass
class NotificationConfig:
    """Notification configuration."""
    
    webhook_url: str
    events: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    format_template: str = "default"
    retry_attempts: int = 3
    retry_delay: int = 5


@dataclass
class BotResponse:
    """Bot response configuration."""
    
    trigger_pattern: str
    response_template: str
    response_type: str = "comment"
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    enabled: bool = True


class GitHubBot:
    """Intelligent GitHub bot with automation capabilities."""
    
    def __init__(self, core):
        self.core = core
        self.logger = Logger("GitHubBot")
        self.data_processor = DataProcessor()
        
        # Bot state
        self.is_running = False
        self.rules = {}
        self.event_queue = Queue()
        self.worker_thread = None
        
        # Response templates
        self.response_templates = {
            'welcome_new_contributor': {
                'pattern': r'first.*contribution',
                'template': '👋 Welcome to the project! Thank you for your first contribution. Please make sure to read our contributing guidelines.'
            },
            'issue_needs_more_info': {
                'pattern': r'bug.*report.*incomplete',
                'template': 'Hi! It looks like this bug report might need more information. Could you please provide steps to reproduce the issue?'
            },
            'pr_needs_tests': {
                'pattern': r'pull.*request.*no.*tests',
                'template': '🧪 This PR looks great! Could you add some tests to ensure the changes work as expected?'
            },
            'stale_issue_reminder': {
                'pattern': r'issue.*stale',
                'template': '📅 This issue has been inactive for a while. Is this still relevant? Please update if needed.'
            }
        }
        
        # Metrics
        self.metrics = {
            'events_processed': 0,
            'rules_executed': 0,
            'responses_sent': 0,
            'errors_encountered': 0,
            'start_time': None
        }
    
    def add_automation_rule(self, rule: AutomationRule):
        """Add an automation rule to the bot."""
        
        self.rules[rule.name] = rule
        self.logger.info(f"Added automation rule: {rule.name}")
    
    def remove_automation_rule(self, rule_name: str):
        """Remove an automation rule."""
        
        if rule_name in self.rules:
            del self.rules[rule_name]
            self.logger.info(f"Removed automation rule: {rule_name}")
    
    def start(self):
        """Start the bot processing loop."""
        
        if self.is_running:
            self.logger.warning("Bot is already running")
            return
        
        self.is_running = True
        self.metrics['start_time'] = datetime.now()
        
        # Start worker thread
        self.worker_thread = threading.Thread(target=self._process_events, daemon=True)
        self.worker_thread.start()
        
        self.logger.info("GitHub Bot started")
    
    def stop(self):
        """Stop the bot processing loop."""
        
        self.is_running = False
        
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        
        self.logger.info("GitHub Bot stopped")
    
    def process_webhook_event(self, event_type: str, payload: Dict[str, Any]):
        """Process a webhook event."""
        
        try:
            event = {
                'type': event_type,
                'payload': payload,
                'timestamp': datetime.now().isoformat(),
                'processed': False
            }
            
            self.event_queue.put(event)
            self.logger.info(f"Queued webhook event: {event_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to process webhook event: {e}")
            self.metrics['errors_encountered'] += 1
    
    def _process_events(self):
        """Process events from the queue."""
        
        while self.is_running:
            try:
                # Get event from queue with timeout
                try:
                    event = self.event_queue.get(timeout=1)
                except Empty:
                    continue
                
                self._handle_event(event)
                self.metrics['events_processed'] += 1
                
            except Exception as e:
                self.logger.error(f"Error processing event: {e}")
                self.metrics['errors_encountered'] += 1
    
    def _handle_event(self, event: Dict[str, Any]):
        """Handle a specific event."""
        
        event_type = event['type']
        payload = event['payload']
        
        self.logger.debug(f"Handling event: {event_type}")
        
        # Apply automation rules
        for rule_name, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            # Check if rule applies to this event type
            if rule.trigger != event_type and rule.trigger != '*':
                continue
            
            # Check cooldown
            if rule.last_executed and rule.cooldown_minutes > 0:
                time_since_last = datetime.now() - rule.last_executed
                if time_since_last.total_seconds() < (rule.cooldown_minutes * 60):
                    continue
            
            # Check conditions
            if self._check_rule_conditions(rule, event):
                self._execute_rule_actions(rule, event)
                rule.last_executed = datetime.now()
                self.metrics['rules_executed'] += 1
    
    def _check_rule_conditions(self, rule: AutomationRule, event: Dict[str, Any]) -> bool:
        """Check if rule conditions are met."""
        
        if not rule.conditions:
            return True  # No conditions means always execute
        
        payload = event['payload']
        
        for condition in rule.conditions:
            condition_type = condition.get('type')
            
            if condition_type == 'field_equals':
                field_path = condition.get('field', '').split('.')
                value = payload
                
                # Navigate to nested field
                for field in field_path:
                    if isinstance(value, dict) and field in value:
                        value = value[field]
                    else:
                        value = None
                        break
                
                if value != condition.get('value'):
                    return False
            
            elif condition_type == 'field_contains':
                field_path = condition.get('field', '').split('.')
                value = payload
                
                for field in field_path:
                    if isinstance(value, dict) and field in value:
                        value = value[field]
                    else:
                        value = None
                        break
                
                if not value or condition.get('value', '') not in str(value):
                    return False
            
            elif condition_type == 'regex_match':
                field_path = condition.get('field', '').split('.')
                value = payload
                
                for field in field_path:
                    if isinstance(value, dict) and field in value:
                        value = value[field]
                    else:
                        value = None
                        break
                
                if not value or not re.search(condition.get('pattern', ''), str(value)):
                    return False
            
            elif condition_type == 'user_not_member':
                user_login = payload.get('sender', {}).get('login')
                if user_login:
                    # Check if user is a member/collaborator
                    # This would require additional API calls in practice
                    pass
        
        return True
    
    def _execute_rule_actions(self, rule: AutomationRule, event: Dict[str, Any]):
        """Execute rule actions."""
        
        payload = event['payload']
        
        for action in rule.actions:
            action_type = action.get('type')
            
            try:
                if action_type == 'add_label':
                    self._action_add_label(action, payload)
                elif action_type == 'create_comment':
                    self._action_create_comment(action, payload)
                elif action_type == 'assign_user':
                    self._action_assign_user(action, payload)
                elif action_type == 'close_issue':
                    self._action_close_issue(action, payload)
                elif action_type == 'request_review':
                    self._action_request_review(action, payload)
                elif action_type == 'send_notification':
                    self._action_send_notification(action, payload)
                
            except Exception as e:
                self.logger.error(f"Failed to execute action {action_type}: {e}")
    
    def _action_add_label(self, action: Dict[str, Any], payload: Dict[str, Any]):
        """Add label to issue or PR."""
        
        repo = payload.get('repository', {})
        issue = payload.get('issue') or payload.get('pull_request')
        
        if repo and issue:
            owner = repo['owner']['login']
            repo_name = repo['name']
            issue_number = issue['number']
            labels = action.get('labels', [])
            
            self.core.post_json(
                f'/repos/{owner}/{repo_name}/issues/{issue_number}/labels',
                json_data={'labels': labels}
            )
            
            self.logger.info(f"Added labels {labels} to #{issue_number}")
    
    def _action_create_comment(self, action: Dict[str, Any], payload: Dict[str, Any]):
        """Create a comment on issue or PR."""
        
        repo = payload.get('repository', {})
        issue = payload.get('issue') or payload.get('pull_request')
        
        if repo and issue:
            owner = repo['owner']['login']
            repo_name = repo['name']
            issue_number = issue['number']
            
            # Process comment template
            comment_body = self._process_template(action.get('message', ''), payload)
            
            self.core.post_json(
                f'/repos/{owner}/{repo_name}/issues/{issue_number}/comments',
                json_data={'body': comment_body}
            )
            
            self.logger.info(f"Created comment on #{issue_number}")
            self.metrics['responses_sent'] += 1
    
    def _action_assign_user(self, action: Dict[str, Any], payload: Dict[str, Any]):
        """Assign user to issue or PR."""
        
        repo = payload.get('repository', {})
        issue = payload.get('issue') or payload.get('pull_request')
        
        if repo and issue:
            owner = repo['owner']['login']
            repo_name = repo['name']
            issue_number = issue['number']
            assignees = action.get('assignees', [])
            
            self.core.post_json(
                f'/repos/{owner}/{repo_name}/issues/{issue_number}/assignees',
                json_data={'assignees': assignees}
            )
            
            self.logger.info(f"Assigned {assignees} to #{issue_number}")
    
    def _action_close_issue(self, action: Dict[str, Any], payload: Dict[str, Any]):
        """Close issue or PR."""
        
        repo = payload.get('repository', {})
        issue = payload.get('issue')
        
        if repo and issue:
            owner = repo['owner']['login']
            repo_name = repo['name']
            issue_number = issue['number']
            
            # Add closing comment if specified
            if action.get('comment'):
                comment_body = self._process_template(action['comment'], payload)
                self.core.post_json(
                    f'/repos/{owner}/{repo_name}/issues/{issue_number}/comments',
                    json_data={'body': comment_body}
                )
            
            # Close the issue
            self.core.post_json(
                f'/repos/{owner}/{repo_name}/issues/{issue_number}',
                json_data={'state': 'closed'}
            )
            
            self.logger.info(f"Closed issue #{issue_number}")
    
    def _action_request_review(self, action: Dict[str, Any], payload: Dict[str, Any]):
        """Request review for PR."""
        
        repo = payload.get('repository', {})
        pr = payload.get('pull_request')
        
        if repo and pr:
            owner = repo['owner']['login']
            repo_name = repo['name']
            pr_number = pr['number']
            reviewers = action.get('reviewers', [])
            team_reviewers = action.get('team_reviewers', [])
            
            request_data = {}
            if reviewers:
                request_data['reviewers'] = reviewers
            if team_reviewers:
                request_data['team_reviewers'] = team_reviewers
            
            if request_data:
                self.core.post_json(
                    f'/repos/{owner}/{repo_name}/pulls/{pr_number}/requested_reviewers',
                    json_data=request_data
                )
                
                self.logger.info(f"Requested review for PR #{pr_number}")
    
    def _action_send_notification(self, action: Dict[str, Any], payload: Dict[str, Any]):
        """Send external notification."""
        
        webhook_url = action.get('webhook_url')
        if webhook_url:
            notification_data = {
                'event': payload.get('action'),
                'repository': payload.get('repository', {}).get('full_name'),
                'timestamp': datetime.now().isoformat(),
                'details': self._extract_notification_details(payload)
            }
            
            # Send notification (simplified)
            import requests
            try:
                requests.post(webhook_url, json=notification_data, timeout=10)
                self.logger.info("Sent external notification")
            except Exception as e:
                self.logger.error(f"Failed to send notification: {e}")
    
    def _process_template(self, template: str, payload: Dict[str, Any]) -> str:
        """Process template with payload data."""
        
        # Simple template processing - replace {field.path} with actual values
        import re
        
        def replace_placeholder(match):
            field_path = match.group(1).split('.')
            value = payload
            
            for field in field_path:
                if isinstance(value, dict) and field in value:
                    value = value[field]
                else:
                    return match.group(0)  # Return original if path not found
            
            return str(value)
        
        # Replace {field.path} patterns
        processed = re.sub(r'\{([^}]+)\}', replace_placeholder, template)
        
        # Add some context-aware improvements
        sender = payload.get('sender', {}).get('login', 'User')
        processed = processed.replace('@sender', f'@{sender}')
        
        return processed
    
    def _extract_notification_details(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant details for notifications."""
        
        details = {}
        
        if 'issue' in payload:
            issue = payload['issue']
            details['issue'] = {
                'number': issue.get('number'),
                'title': issue.get('title'),
                'author': issue.get('user', {}).get('login'),
                'url': issue.get('html_url')
            }
        
        if 'pull_request' in payload:
            pr = payload['pull_request']
            details['pull_request'] = {
                'number': pr.get('number'),
                'title': pr.get('title'),
                'author': pr.get('user', {}).get('login'),
                'url': pr.get('html_url')
            }
        
        if 'sender' in payload:
            details['sender'] = payload['sender'].get('login')
        
        return details
    
    def create_welcome_bot(self, repository: str) -> AutomationRule:
        """Create a welcome bot rule for new contributors."""
        
        rule = AutomationRule(
            name=f"welcome_bot_{repository}",
            trigger="pull_request",
            conditions=[
                {
                    'type': 'field_equals',
                    'field': 'action',
                    'value': 'opened'
                },
                {
                    'type': 'user_not_member',
                    'field': 'sender.login'
                }
            ],
            actions=[
                {
                    'type': 'create_comment',
                    'message': '👋 Welcome @{sender.login}! Thank you for your contribution to {repository.name}. Our maintainers will review your changes soon.'
                },
                {
                    'type': 'add_label',
                    'labels': ['first-time-contributor']
                }
            ]
        )
        
        self.add_automation_rule(rule)
        return rule
    
    def create_stale_issue_bot(self, repository: str, days_threshold: int = 30) -> AutomationRule:
        """Create a bot to handle stale issues."""
        
        rule = AutomationRule(
            name=f"stale_issue_bot_{repository}",
            trigger="schedule",  # This would be triggered by a scheduler
            conditions=[],
            actions=[
                {
                    'type': 'add_label',
                    'labels': ['stale']
                },
                {
                    'type': 'create_comment',
                    'message': f'📅 This issue has been inactive for {days_threshold} days. Is this still relevant? Please update if needed, otherwise it will be closed in 7 days.'
                }
            ]
        )
        
        self.add_automation_rule(rule)
        return rule
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get bot metrics."""
        
        metrics = self.metrics.copy()
        
        if metrics['start_time']:
            uptime = datetime.now() - metrics['start_time']
            metrics['uptime_hours'] = uptime.total_seconds() / 3600
        
        metrics['active_rules'] = len([r for r in self.rules.values() if r.enabled])
        metrics['total_rules'] = len(self.rules)
        
        return metrics


class AutomatedInteractions:
    """Automated interaction management system."""
    
    def __init__(self, core):
        self.core = core
        self.logger = Logger("AutomatedInteractions")
        self.data_processor = DataProcessor()
        
        self.notification_configs = {}
        self.scheduled_tasks = []
        self.is_running = False
        self._scheduler_thread = None
    
    def setup_smart_notifications(self, webhook_url: str, 
                                events: Optional[List[str]] = None) -> bool:
        """Set up smart notification system."""
        
        if not webhook_url:
            raise ValidationError("Webhook URL is required", field="webhook_url")
        
        config = NotificationConfig(
            webhook_url=webhook_url,
            events=events or [
                'issues.opened', 'issues.closed',
                'pull_request.opened', 'pull_request.closed', 'pull_request.merged',
                'push', 'release.published'
            ]
        )
        
        self.notification_configs['default'] = config
        
        self.logger.info(f"Set up smart notifications for {len(config.events)} event types")
        return True
    
    def add_notification_filter(self, config_name: str, 
                               filters: Dict[str, Any]):
        """Add filters to notification configuration."""
        
        if config_name in self.notification_configs:
            self.notification_configs[config_name].filters.update(filters)
            self.logger.info(f"Added filters to {config_name} notifications")
    
    def schedule_task(self, task_name: str, 
                     func: Callable, 
                     schedule_type: str,
                     **kwargs):
        """Schedule automated task."""
        
        if schedule_type == "daily":
            schedule.every().day.at(kwargs.get('time', '09:00')).do(func).tag(task_name)
        elif schedule_type == "weekly":
            schedule.every().week.do(func).tag(task_name)
        elif schedule_type == "hourly":
            schedule.every().hour.do(func).tag(task_name)
        elif schedule_type == "interval":
            minutes = kwargs.get('minutes', 60)
            schedule.every(minutes).minutes.do(func).tag(task_name)
        
        self.scheduled_tasks.append(task_name)
        self.logger.info(f"Scheduled task: {task_name} ({schedule_type})")
    
    def start_scheduler(self):
        """Start the task scheduler."""
        
        if self.is_running:
            return
        
        self.is_running = True
        self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()
        
        self.logger.info("Task scheduler started")
    
    def stop_scheduler(self):
        """Stop the task scheduler."""
        
        self.is_running = False
        schedule.clear()
        
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            self._scheduler_thread.join(timeout=5)
        
        self.logger.info("Task scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop."""
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop(self):
        """Stop all automated interactions."""
        self.stop_scheduler()


class SmartResponder:
    """Intelligent response system for GitHub interactions."""
    
    def __init__(self, core):
        self.core = core
        self.logger = Logger("SmartResponder")
        self.data_processor = DataProcessor()
        
        self.response_configs = {}
        self.is_running = False
        self.response_history = deque(maxlen=1000)  # Keep last 1000 responses
        
        # Default intelligent responses
        self.default_responses = {
            'bug_report_incomplete': {
                'triggers': ['bug', 'issue', 'problem', 'error'],
                'missing_info_indicators': ['no steps', 'version', 'reproduce'],
                'response': '🐛 Thanks for the bug report! To help us investigate, could you please provide:\n\n- Steps to reproduce\n- Expected vs actual behavior\n- Your environment details\n\nThis will help us resolve the issue faster!'
            },
            'feature_request_needs_discussion': {
                'triggers': ['feature', 'enhancement', 'request'],
                'discussion_indicators': ['should', 'could', 'maybe', 'what if'],
                'response': '💡 Interesting feature idea! Let\'s discuss this further:\n\n- What specific problem would this solve?\n- How do you envision this working?\n- Are there alternative approaches?\n\nCommunity input welcome!'
            },
            'pr_needs_description': {
                'triggers': ['pull request', 'pr'],
                'missing_desc_indicators': ['no description', 'empty', 'brief'],
                'response': '📝 Thanks for the PR! Could you add a description explaining:\n\n- What changes you made\n- Why these changes are needed\n- Any testing you\'ve done\n\nThis helps reviewers understand your contribution better!'
            }
        }
    
    def start_automated_responses(self, config: Dict[str, Any]) -> bool:
        """Start automated response system."""
        
        self.response_configs.update(config)
        self.is_running = True
        
        self.logger.info("Smart responder started")
        return True
    
    def stop(self):
        """Stop automated responses."""
        
        self.is_running = False
        self.logger.info("Smart responder stopped")
    
    def analyze_and_respond(self, event_type: str, payload: Dict[str, Any]) -> Optional[str]:
        """Analyze event and generate intelligent response."""
        
        if not self.is_running:
            return None
        
        try:
            response = None
            
            if event_type == 'issues' and payload.get('action') == 'opened':
                response = self._analyze_new_issue(payload)
            elif event_type == 'pull_request' and payload.get('action') == 'opened':
                response = self._analyze_new_pr(payload)
            elif event_type == 'issue_comment':
                response = self._analyze_comment(payload)
            
            if response:
                self._record_response(event_type, payload, response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error analyzing event for response: {e}")
            return None
    
    def _analyze_new_issue(self, payload: Dict[str, Any]) -> Optional[str]:
        """Analyze new issue and suggest response."""
        
        issue = payload.get('issue', {})
        title = issue.get('title', '').lower()
        body = issue.get('body', '').lower()
        
        # Check for bug report
        if any(trigger in title or trigger in body for trigger in self.default_responses['bug_report_incomplete']['triggers']):
            # Check if information is missing
            if any(indicator in body for indicator in self.default_responses['bug_report_incomplete']['missing_info_indicators']):
                return None  # Has enough info
            elif len(body) < 100:  # Very short description
                return self.default_responses['bug_report_incomplete']['response']
        
        # Check for feature request
        if any(trigger in title or trigger in body for trigger in self.default_responses['feature_request_needs_discussion']['triggers']):
            if len(body) < 200:  # Brief feature request
                return self.default_responses['feature_request_needs_discussion']['response']
        
        # Check for first-time contributor
        author = issue.get('user', {}).get('login')
        if author and self._is_first_time_contributor(payload.get('repository', {}), author):
            return f"👋 Welcome to the project, @{author}! Thanks for opening your first issue. Our maintainers will take a look soon."
        
        return None
    
    def _analyze_new_pr(self, payload: Dict[str, Any]) -> Optional[str]:
        """Analyze new pull request and suggest response."""
        
        pr = payload.get('pull_request', {})
        title = pr.get('title', '')
        body = pr.get('body', '') or ''
        
        # Check for missing description
        if len(body) < 50:
            return self.default_responses['pr_needs_description']['response']
        
        # Check for first-time contributor
        author = pr.get('user', {}).get('login')
        if author and self._is_first_time_contributor(payload.get('repository', {}), author):
            return f"🎉 Welcome @{author}! Thanks for your first contribution. Our maintainers will review your changes soon."
        
        # Check for large PR
        additions = pr.get('additions', 0)
        deletions = pr.get('deletions', 0)
        if additions + deletions > 500:
            return f"📏 This is quite a large PR ({additions + deletions} lines changed). Consider breaking it into smaller, focused PRs for easier review."
        
        return None
    
    def _analyze_comment(self, payload: Dict[str, Any]) -> Optional[str]:
        """Analyze comment and suggest response."""
        
        comment = payload.get('comment', {})
        body = comment.get('body', '').lower()
        author = comment.get('user', {}).get('login')
        
        # Check for questions that might need help
        question_indicators = ['how to', 'help', 'question', 'confused', 'not working']
        if any(indicator in body for indicator in question_indicators):
            return f"🤔 Hi @{author}! It looks like you have a question. Our community is here to help! You might also want to check our documentation or search through existing issues for similar questions."
        
        # Check for appreciation
        thanks_indicators = ['thank', 'thanks', 'appreciate', 'great work', 'awesome']
        if any(indicator in body for indicator in thanks_indicators):
            return f"😊 Thank you @{author}! We appreciate your kind words and engagement with the project."
        
        return None
    
    def _is_first_time_contributor(self, repository: Dict[str, Any], username: str) -> bool:
        """Check if user is a first-time contributor."""
        
        try:
            # This is a simplified check - in practice, you'd want to check
            # the user's contribution history to this repository
            repo_full_name = repository.get('full_name', '')
            
            # Check recent contributors
            contributors = self.core.paginate(f'/repos/{repo_full_name}/contributors', max_pages=1)
            contributor_logins = [c.get('login') for c in contributors]
            
            return username not in contributor_logins
            
        except Exception:
            return False  # Default to False if check fails
    
    def _record_response(self, event_type: str, payload: Dict[str, Any], response: str):
        """Record response for analytics."""
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'repository': payload.get('repository', {}).get('full_name'),
            'response_length': len(response),
            'response_hash': hashlib.md5(response.encode()).hexdigest()[:8]
        }
        
        self.response_history.append(record)
    
    def get_response_analytics(self) -> Dict[str, Any]:
        """Get analytics about responses."""
        
        if not self.response_history:
            return {'total_responses': 0}
        
        # Analyze response patterns
        event_types = defaultdict(int)
        repositories = defaultdict(int)
        
        for record in self.response_history:
            event_types[record['event_type']] += 1
            repositories[record['repository']] += 1
        
        return {
            'total_responses': len(self.response_history),
            'responses_by_event_type': dict(event_types),
            'responses_by_repository': dict(repositories),
            'average_response_length': sum(r['response_length'] for r in self.response_history) / len(self.response_history),
            'active_since': min(r['timestamp'] for r in self.response_history),
            'most_recent': max(r['timestamp'] for r in self.response_history)
        }
    
    def add_custom_response(self, name: str, 
                          trigger_patterns: List[str],
                          response_template: str,
                          conditions: Optional[List[Dict[str, Any]]] = None):
        """Add custom response pattern."""
        
        response_config = BotResponse(
            trigger_pattern='|'.join(trigger_patterns),
            response_template=response_template,
            conditions=conditions or []
        )
        
        self.response_configs[name] = response_config
        self.logger.info(f"Added custom response: {name}")
    
    def remove_custom_response(self, name: str):
        """Remove custom response pattern."""
        
        if name in self.response_configs:
            del self.response_configs[name]
            self.logger.info(f"Removed custom response: {name}")


class WebhookHandler:
    """GitHub webhook handler with security and processing."""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key
        self.logger = Logger("WebhookHandler")
        self.event_processors = {}
    
    def register_processor(self, event_type: str, processor: Callable):
        """Register event processor for specific event type."""
        
        self.event_processors[event_type] = processor
        self.logger.info(f"Registered processor for {event_type} events")
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature."""
        
        if not self.secret_key:
            self.logger.warning("No secret key configured for webhook verification")
            return True  # Allow if no secret configured
        
        if not signature.startswith('sha256='):
            return False
        
        expected_signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        expected_signature = f"sha256={expected_signature}"
        
        return hmac.compare_digest(expected_signature, signature)
    
    def process_webhook(self, headers: Dict[str, str], payload: bytes) -> Dict[str, Any]:
        """Process incoming webhook."""
        
        try:
            # Verify signature if configured
            signature = headers.get('X-Hub-Signature-256', '')
            if self.secret_key and not self.verify_signature(payload, signature):
                raise WebhookError("Invalid webhook signature")
            
            # Parse payload
            try:
                payload_data = json.loads(payload.decode('utf-8'))
            except json.JSONDecodeError as e:
                raise WebhookError(f"Invalid JSON payload: {e}")
            
            # Get event type
            event_type = headers.get('X-GitHub-Event', 'unknown')
            
            # Process event
            result = {
                'event_type': event_type,
                'processed': False,
                'timestamp': datetime.now().isoformat()
            }
            
            if event_type in self.event_processors:
                try:
                    self.event_processors[event_type](payload_data)
                    result['processed'] = True
                except Exception as e:
                    result['error'] = str(e)
                    self.logger.error(f"Error processing {event_type} event: {e}")
            else:
                self.logger.warning(f"No processor registered for {event_type} events")
            
            return result
            
        except Exception as e:
            raise WebhookError(f"Webhook processing failed: {e}")


__all__ = [
    'GitHubBot',
    'AutomatedInteractions',
    'SmartResponder',
    'WebhookHandler',
    'AutomationRule',
    'NotificationConfig',
    'BotResponse'
]