"""
MeroHub Git Operations Module
Author: MERO (Telegram: @QP4RM)

Comprehensive Git operations, version control, and branch management
functionality for local and remote GitHub repositories.
"""

import os
import json
import shutil
import tempfile
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import threading
from dataclasses import dataclass, field
import git
from git import Repo, InvalidGitRepositoryError, GitCommandError
from .exceptions import GitOperationError, ValidationError, RepositoryError
from .utils import Logger, DataProcessor, retry_on_exception


@dataclass
class GitConfig:
    """Git configuration container."""
    
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    default_branch: str = "main"
    auto_crlf: bool = False
    core_editor: str = "nano"
    merge_tool: Optional[str] = None
    diff_tool: Optional[str] = None
    push_default: str = "simple"
    pull_rebase: bool = False


@dataclass
class BranchInfo:
    """Branch information container."""
    
    name: str
    commit_sha: str
    is_current: bool = False
    is_remote: bool = False
    upstream_branch: Optional[str] = None
    last_commit_date: Optional[datetime] = None
    last_commit_message: Optional[str] = None
    commits_ahead: int = 0
    commits_behind: int = 0


@dataclass
class CommitInfo:
    """Commit information container."""
    
    sha: str
    message: str
    author_name: str
    author_email: str
    author_date: datetime
    committer_name: str
    committer_email: str
    committer_date: datetime
    parents: List[str] = field(default_factory=list)
    files_changed: List[str] = field(default_factory=list)
    insertions: int = 0
    deletions: int = 0


class GitOperations:
    """Core Git operations functionality."""
    
    def __init__(self, core):
        self.core = core
        self.logger = Logger("GitOperations")
        self.data_processor = DataProcessor()
        self._git_config = GitConfig()
        
    def clone_repository(self, url: str, 
                        local_path: Optional[str] = None,
                        branch: Optional[str] = None,
                        depth: Optional[int] = None,
                        recursive: bool = False) -> Repo:
        """Clone a Git repository."""
        
        if not url:
            raise ValidationError("Repository URL is required", field="url")
        
        if not local_path:
            # Extract repo name from URL
            repo_name = url.split('/')[-1].replace('.git', '')
            local_path = f"./{repo_name}"
        
        clone_kwargs = {}
        if branch:
            clone_kwargs['branch'] = branch
        if depth:
            clone_kwargs['depth'] = depth
        if recursive:
            clone_kwargs['recursive'] = True
        
        try:
            self.logger.info(f"Cloning repository: {url} to {local_path}")
            
            # Ensure parent directory exists
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            
            repo = Repo.clone_from(url, local_path, **clone_kwargs)
            
            self.logger.info(f"Repository cloned successfully to {local_path}")
            return repo
            
        except Exception as e:
            raise GitOperationError(f"Failed to clone repository: {e}",
                                   git_command="clone",
                                   repository_path=local_path)
    
    def init_repository(self, path: str, bare: bool = False) -> Repo:
        """Initialize a new Git repository."""
        
        if not path:
            raise ValidationError("Path is required", field="path")
        
        try:
            self.logger.info(f"Initializing Git repository at: {path}")
            
            # Create directory if it doesn't exist
            Path(path).mkdir(parents=True, exist_ok=True)
            
            repo = Repo.init(path, bare=bare)
            
            # Configure repository
            self._configure_repository(repo)
            
            self.logger.info(f"Repository initialized at {path}")
            return repo
            
        except Exception as e:
            raise GitOperationError(f"Failed to initialize repository: {e}",
                                   git_command="init",
                                   repository_path=path)
    
    def open_repository(self, path: str) -> Repo:
        """Open an existing Git repository."""
        
        if not path or not os.path.exists(path):
            raise ValidationError("Invalid repository path", field="path")
        
        try:
            repo = Repo(path)
            
            if repo.bare:
                self.logger.info(f"Opened bare repository: {path}")
            else:
                self.logger.info(f"Opened repository: {path}")
            
            return repo
            
        except InvalidGitRepositoryError:
            raise GitOperationError(f"Not a valid Git repository: {path}",
                                   repository_path=path)
        except Exception as e:
            raise GitOperationError(f"Failed to open repository: {e}",
                                   repository_path=path)
    
    def get_repository_status(self, repo: Repo) -> Dict[str, Any]:
        """Get comprehensive repository status."""
        
        try:
            status = {
                'working_directory': repo.working_dir,
                'bare_repository': repo.bare,
                'current_branch': None,
                'dirty': False,
                'untracked_files': [],
                'modified_files': [],
                'staged_files': [],
                'deleted_files': [],
                'renamed_files': [],
                'conflicts': [],
                'head_commit': None,
                'total_commits': 0,
                'remotes': []
            }
            
            if not repo.bare:
                # Current branch
                try:
                    status['current_branch'] = repo.active_branch.name
                except:
                    status['current_branch'] = 'HEAD (detached)'
                
                # Check if working directory is dirty
                status['dirty'] = repo.is_dirty()
                
                # File status
                status['untracked_files'] = list(repo.untracked_files)
                
                # Get changed files
                if repo.head.is_valid():
                    for item in repo.index.diff(None):  # Working tree vs index
                        if item.change_type == 'M':
                            status['modified_files'].append(item.a_path)
                        elif item.change_type == 'D':
                            status['deleted_files'].append(item.a_path)
                        elif item.change_type == 'R':
                            status['renamed_files'].append({
                                'old_path': item.a_path,
                                'new_path': item.b_path
                            })
                    
                    # Staged files
                    for item in repo.index.diff('HEAD'):  # Index vs HEAD
                        if item.change_type in ['A', 'M', 'D']:
                            status['staged_files'].append(item.a_path or item.b_path)
                
                # Check for conflicts
                try:
                    status['conflicts'] = list(repo.index.unmerged_blobs().keys())
                except:
                    pass
            
            # Head commit
            if repo.head.is_valid():
                head = repo.head.commit
                status['head_commit'] = {
                    'sha': head.hexsha,
                    'message': head.message.strip(),
                    'author': f"{head.author.name} <{head.author.email}>",
                    'date': head.committed_datetime.isoformat()
                }
                
                # Count total commits
                try:
                    status['total_commits'] = sum(1 for _ in repo.iter_commits())
                except:
                    status['total_commits'] = 0
            
            # Remotes
            for remote in repo.remotes:
                status['remotes'].append({
                    'name': remote.name,
                    'url': list(remote.urls)[0] if remote.urls else None
                })
            
            return status
            
        except Exception as e:
            raise GitOperationError(f"Failed to get repository status: {e}",
                                   repository_path=repo.working_dir)
    
    def add_files(self, repo: Repo, files: Union[str, List[str]]) -> bool:
        """Add files to the staging area."""
        
        if isinstance(files, str):
            files = [files]
        
        try:
            self.logger.info(f"Adding files to staging: {files}")
            
            for file in files:
                repo.index.add([file])
            
            self.logger.info("Files added successfully")
            return True
            
        except Exception as e:
            raise GitOperationError(f"Failed to add files: {e}",
                                   git_command="add",
                                   repository_path=repo.working_dir)
    
    def commit_changes(self, repo: Repo, 
                      message: str,
                      author: Optional[Tuple[str, str]] = None,
                      committer: Optional[Tuple[str, str]] = None,
                      amend: bool = False) -> str:
        """Commit staged changes."""
        
        if not message or len(message.strip()) == 0:
            raise ValidationError("Commit message is required", field="message")
        
        try:
            self.logger.info(f"Committing changes: {message}")
            
            commit_kwargs = {'message': message.strip()}
            
            if author:
                commit_kwargs['author'] = git.Actor(author[0], author[1])
            if committer:
                commit_kwargs['committer'] = git.Actor(committer[0], committer[1])
            if amend:
                commit_kwargs['amend'] = True
            
            commit = repo.index.commit(**commit_kwargs)
            
            self.logger.info(f"Commit created: {commit.hexsha[:8]}")
            return commit.hexsha
            
        except Exception as e:
            raise GitOperationError(f"Failed to commit changes: {e}",
                                   git_command="commit",
                                   repository_path=repo.working_dir)
    
    def push_changes(self, repo: Repo,
                    remote_name: str = "origin",
                    branch_name: Optional[str] = None,
                    force: bool = False,
                    set_upstream: bool = False) -> bool:
        """Push changes to remote repository."""
        
        try:
            if remote_name not in [r.name for r in repo.remotes]:
                raise ValidationError(f"Remote '{remote_name}' not found")
            
            remote = repo.remote(remote_name)
            
            if not branch_name:
                if repo.head.is_detached:
                    raise GitOperationError("Cannot push from detached HEAD without specifying branch")
                branch_name = repo.active_branch.name
            
            push_kwargs = {}
            if force:
                push_kwargs['force'] = True
            if set_upstream:
                push_kwargs['set_upstream'] = True
            
            self.logger.info(f"Pushing to {remote_name}/{branch_name}")
            
            push_info = remote.push(f"refs/heads/{branch_name}", **push_kwargs)
            
            # Check push results
            for info in push_info:
                if info.flags & info.ERROR:
                    raise GitOperationError(f"Push failed: {info.summary}")
                elif info.flags & info.REJECTED:
                    raise GitOperationError(f"Push rejected: {info.summary}")
            
            self.logger.info("Push completed successfully")
            return True
            
        except Exception as e:
            raise GitOperationError(f"Failed to push changes: {e}",
                                   git_command="push",
                                   repository_path=repo.working_dir)
    
    def pull_changes(self, repo: Repo,
                    remote_name: str = "origin",
                    branch_name: Optional[str] = None,
                    rebase: bool = False) -> bool:
        """Pull changes from remote repository."""
        
        try:
            if remote_name not in [r.name for r in repo.remotes]:
                raise ValidationError(f"Remote '{remote_name}' not found")
            
            remote = repo.remote(remote_name)
            
            if not branch_name:
                if repo.head.is_detached:
                    raise GitOperationError("Cannot pull to detached HEAD without specifying branch")
                branch_name = repo.active_branch.name
            
            self.logger.info(f"Pulling from {remote_name}/{branch_name}")
            
            if rebase:
                # Fetch and rebase
                remote.fetch()
                repo.git.rebase(f"{remote_name}/{branch_name}")
            else:
                # Regular pull (fetch and merge)
                pull_info = remote.pull(branch_name)
                
                # Check pull results
                for info in pull_info:
                    if info.flags & info.ERROR:
                        raise GitOperationError(f"Pull failed: {info.note}")
            
            self.logger.info("Pull completed successfully")
            return True
            
        except Exception as e:
            raise GitOperationError(f"Failed to pull changes: {e}",
                                   git_command="pull",
                                   repository_path=repo.working_dir)
    
    def fetch_changes(self, repo: Repo,
                     remote_name: str = "origin",
                     prune: bool = False) -> bool:
        """Fetch changes from remote repository."""
        
        try:
            if remote_name not in [r.name for r in repo.remotes]:
                raise ValidationError(f"Remote '{remote_name}' not found")
            
            remote = repo.remote(remote_name)
            
            self.logger.info(f"Fetching from {remote_name}")
            
            fetch_kwargs = {}
            if prune:
                fetch_kwargs['prune'] = True
            
            fetch_info = remote.fetch(**fetch_kwargs)
            
            self.logger.info(f"Fetched {len(fetch_info)} refs")
            return True
            
        except Exception as e:
            raise GitOperationError(f"Failed to fetch changes: {e}",
                                   git_command="fetch",
                                   repository_path=repo.working_dir)
    
    def add_remote(self, repo: Repo, name: str, url: str) -> bool:
        """Add a remote repository."""
        
        if not name or not url:
            raise ValidationError("Remote name and URL are required")
        
        try:
            self.logger.info(f"Adding remote '{name}': {url}")
            
            repo.create_remote(name, url)
            
            self.logger.info(f"Remote '{name}' added successfully")
            return True
            
        except Exception as e:
            raise GitOperationError(f"Failed to add remote: {e}",
                                   repository_path=repo.working_dir)
    
    def remove_remote(self, repo: Repo, name: str) -> bool:
        """Remove a remote repository."""
        
        if not name:
            raise ValidationError("Remote name is required", field="name")
        
        try:
            if name not in [r.name for r in repo.remotes]:
                raise ValidationError(f"Remote '{name}' not found")
            
            self.logger.info(f"Removing remote '{name}'")
            
            repo.delete_remote(name)
            
            self.logger.info(f"Remote '{name}' removed successfully")
            return True
            
        except Exception as e:
            raise GitOperationError(f"Failed to remove remote: {e}",
                                   repository_path=repo.working_dir)
    
    def get_commit_history(self, repo: Repo,
                          max_count: int = 100,
                          since: Optional[datetime] = None,
                          until: Optional[datetime] = None,
                          author: Optional[str] = None,
                          path: Optional[str] = None) -> List[CommitInfo]:
        """Get repository commit history."""
        
        try:
            kwargs = {}
            if max_count:
                kwargs['max_count'] = max_count
            if since:
                kwargs['since'] = since
            if until:
                kwargs['until'] = until
            if author:
                kwargs['author'] = author
            if path:
                kwargs['paths'] = path
            
            commits = []
            
            for commit in repo.iter_commits(**kwargs):
                commit_info = CommitInfo(
                    sha=commit.hexsha,
                    message=commit.message.strip(),
                    author_name=commit.author.name,
                    author_email=commit.author.email,
                    author_date=commit.authored_datetime,
                    committer_name=commit.committer.name,
                    committer_email=commit.committer.email,
                    committer_date=commit.committed_datetime,
                    parents=[parent.hexsha for parent in commit.parents]
                )
                
                # Get commit statistics
                try:
                    stats = commit.stats.total
                    commit_info.insertions = stats['insertions']
                    commit_info.deletions = stats['deletions']
                    commit_info.files_changed = list(commit.stats.files.keys())
                except:
                    pass  # Skip if stats unavailable
                
                commits.append(commit_info)
            
            return commits
            
        except Exception as e:
            raise GitOperationError(f"Failed to get commit history: {e}",
                                   repository_path=repo.working_dir)
    
    def get_diff(self, repo: Repo,
                commit1: Optional[str] = None,
                commit2: Optional[str] = None,
                cached: bool = False,
                create_patch: bool = True) -> str:
        """Get diff between commits or working directory."""
        
        try:
            if commit1 and commit2:
                # Diff between two commits
                diff = repo.git.diff(commit1, commit2, create_patch=create_patch)
            elif commit1:
                # Diff from commit to working directory
                diff = repo.git.diff(commit1, create_patch=create_patch)
            elif cached:
                # Diff of staged changes
                diff = repo.git.diff('--cached', create_patch=create_patch)
            else:
                # Diff of working directory changes
                diff = repo.git.diff(create_patch=create_patch)
            
            return diff
            
        except Exception as e:
            raise GitOperationError(f"Failed to get diff: {e}",
                                   repository_path=repo.working_dir)
    
    def stash_changes(self, repo: Repo, message: Optional[str] = None) -> str:
        """Stash current changes."""
        
        try:
            stash_message = message or f"WIP on {repo.active_branch.name}: {repo.head.commit.message.strip()[:50]}"
            
            self.logger.info("Stashing changes")
            
            # Create stash
            repo.git.stash('push', '-m', stash_message)
            
            self.logger.info("Changes stashed successfully")
            return stash_message
            
        except Exception as e:
            raise GitOperationError(f"Failed to stash changes: {e}",
                                   git_command="stash",
                                   repository_path=repo.working_dir)
    
    def apply_stash(self, repo: Repo, stash_index: int = 0) -> bool:
        """Apply stashed changes."""
        
        try:
            self.logger.info(f"Applying stash {stash_index}")
            
            repo.git.stash('apply', f'stash@{{{stash_index}}}')
            
            self.logger.info("Stash applied successfully")
            return True
            
        except Exception as e:
            raise GitOperationError(f"Failed to apply stash: {e}",
                                   git_command="stash",
                                   repository_path=repo.working_dir)
    
    def list_stashes(self, repo: Repo) -> List[Dict[str, Any]]:
        """List all stashes."""
        
        try:
            stash_list = repo.git.stash('list').split('\n')
            stashes = []
            
            for i, stash_line in enumerate(stash_list):
                if stash_line.strip():
                    parts = stash_line.split(': ', 2)
                    if len(parts) >= 3:
                        stashes.append({
                            'index': i,
                            'name': parts[0],
                            'branch': parts[1],
                            'message': parts[2]
                        })
            
            return stashes
            
        except Exception as e:
            # Return empty list if no stashes or error
            return []
    
    def reset_changes(self, repo: Repo,
                     mode: str = "mixed",
                     commit: Optional[str] = None,
                     files: Optional[List[str]] = None) -> bool:
        """Reset repository state."""
        
        if mode not in ['soft', 'mixed', 'hard']:
            raise ValidationError("Invalid reset mode", field="mode")
        
        try:
            self.logger.info(f"Resetting repository ({mode})")
            
            if files:
                # Reset specific files
                repo.git.reset(commit or 'HEAD', '--', *files)
            else:
                # Reset entire repository
                reset_args = [f'--{mode}']
                if commit:
                    reset_args.append(commit)
                
                repo.git.reset(*reset_args)
            
            self.logger.info("Reset completed successfully")
            return True
            
        except Exception as e:
            raise GitOperationError(f"Failed to reset changes: {e}",
                                   git_command="reset",
                                   repository_path=repo.working_dir)
    
    def _configure_repository(self, repo: Repo):
        """Configure repository with default settings."""
        
        try:
            config = repo.config_writer()
            
            if self._git_config.user_name:
                config.set_value("user", "name", self._git_config.user_name)
            if self._git_config.user_email:
                config.set_value("user", "email", self._git_config.user_email)
            
            config.set_value("core", "autocrlf", str(self._git_config.auto_crlf).lower())
            config.set_value("core", "editor", self._git_config.core_editor)
            config.set_value("push", "default", self._git_config.push_default)
            config.set_value("pull", "rebase", str(self._git_config.pull_rebase).lower())
            
            config.release()
            
        except Exception as e:
            self.logger.warning(f"Failed to configure repository: {e}")
    
    def configure_git(self, config: GitConfig):
        """Update Git configuration."""
        self._git_config = config
        self.logger.info("Git configuration updated")


class BranchManager:
    """Branch management functionality."""
    
    def __init__(self, git_ops: GitOperations):
        self.git_ops = git_ops
        self.logger = Logger("BranchManager")
    
    def list_branches(self, repo: Repo, 
                     include_remote: bool = True,
                     include_merged: bool = True) -> List[BranchInfo]:
        """List repository branches."""
        
        try:
            branches = []
            current_branch = None
            
            try:
                current_branch = repo.active_branch.name
            except:
                pass  # Detached HEAD
            
            # Local branches
            for branch in repo.branches:
                branch_info = BranchInfo(
                    name=branch.name,
                    commit_sha=branch.commit.hexsha,
                    is_current=branch.name == current_branch,
                    is_remote=False
                )
                
                # Get commit info
                try:
                    commit = branch.commit
                    branch_info.last_commit_date = commit.committed_datetime
                    branch_info.last_commit_message = commit.message.strip()
                except:
                    pass
                
                # Get tracking branch
                try:
                    if branch.tracking_branch():
                        branch_info.upstream_branch = branch.tracking_branch().name
                        
                        # Calculate ahead/behind
                        try:
                            ahead, behind = repo.git.rev_list(
                                '--left-right', '--count',
                                f'{branch.tracking_branch().name}...{branch.name}'
                            ).split('\t')
                            branch_info.commits_ahead = int(ahead)
                            branch_info.commits_behind = int(behind)
                        except:
                            pass
                except:
                    pass
                
                branches.append(branch_info)
            
            # Remote branches
            if include_remote:
                for remote in repo.remotes:
                    for ref in remote.refs:
                        # Skip HEAD references
                        if ref.name.endswith('/HEAD'):
                            continue
                        
                        branch_info = BranchInfo(
                            name=ref.name,
                            commit_sha=ref.commit.hexsha,
                            is_current=False,
                            is_remote=True
                        )
                        
                        # Get commit info
                        try:
                            commit = ref.commit
                            branch_info.last_commit_date = commit.committed_datetime
                            branch_info.last_commit_message = commit.message.strip()
                        except:
                            pass
                        
                        branches.append(branch_info)
            
            return branches
            
        except Exception as e:
            raise GitOperationError(f"Failed to list branches: {e}",
                                   repository_path=repo.working_dir)
    
    def create_branch(self, repo: Repo,
                     branch_name: str,
                     start_point: Optional[str] = None,
                     checkout: bool = True) -> BranchInfo:
        """Create a new branch."""
        
        if not branch_name:
            raise ValidationError("Branch name is required", field="branch_name")
        
        # Validate branch name
        if not self._is_valid_branch_name(branch_name):
            raise ValidationError("Invalid branch name", field="branch_name")
        
        try:
            self.logger.info(f"Creating branch: {branch_name}")
            
            # Create branch
            if start_point:
                branch = repo.create_head(branch_name, start_point)
            else:
                branch = repo.create_head(branch_name)
            
            # Checkout if requested
            if checkout:
                branch.checkout()
            
            branch_info = BranchInfo(
                name=branch.name,
                commit_sha=branch.commit.hexsha,
                is_current=checkout,
                is_remote=False
            )
            
            self.logger.info(f"Branch '{branch_name}' created successfully")
            return branch_info
            
        except Exception as e:
            raise GitOperationError(f"Failed to create branch: {e}",
                                   git_command="branch",
                                   repository_path=repo.working_dir,
                                   branch=branch_name)
    
    def delete_branch(self, repo: Repo,
                     branch_name: str,
                     force: bool = False) -> bool:
        """Delete a branch."""
        
        if not branch_name:
            raise ValidationError("Branch name is required", field="branch_name")
        
        try:
            # Check if branch exists
            if branch_name not in [b.name for b in repo.branches]:
                raise ValidationError(f"Branch '{branch_name}' not found")
            
            # Check if it's the current branch
            try:
                if repo.active_branch.name == branch_name:
                    raise GitOperationError("Cannot delete current branch")
            except:
                pass  # Detached HEAD
            
            self.logger.info(f"Deleting branch: {branch_name}")
            
            branch = repo.branches[branch_name]
            
            if force:
                repo.delete_head(branch, force=True)
            else:
                # Check if branch is merged
                try:
                    repo.git.branch('-d', branch_name)
                except GitCommandError as e:
                    if 'not fully merged' in str(e):
                        raise GitOperationError(f"Branch '{branch_name}' is not fully merged. Use force=True to delete anyway")
                    raise
            
            self.logger.info(f"Branch '{branch_name}' deleted successfully")
            return True
            
        except Exception as e:
            raise GitOperationError(f"Failed to delete branch: {e}",
                                   git_command="branch",
                                   repository_path=repo.working_dir,
                                   branch=branch_name)
    
    def checkout_branch(self, repo: Repo,
                       branch_name: str,
                       create: bool = False) -> bool:
        """Checkout a branch."""
        
        if not branch_name:
            raise ValidationError("Branch name is required", field="branch_name")
        
        try:
            self.logger.info(f"Checking out branch: {branch_name}")
            
            if create:
                # Create and checkout new branch
                if branch_name in [b.name for b in repo.branches]:
                    raise ValidationError(f"Branch '{branch_name}' already exists")
                
                branch = repo.create_head(branch_name)
                branch.checkout()
            else:
                # Checkout existing branch
                if branch_name in [b.name for b in repo.branches]:
                    # Local branch
                    repo.branches[branch_name].checkout()
                else:
                    # Try remote branch
                    remote_branches = []
                    for remote in repo.remotes:
                        for ref in remote.refs:
                            if ref.name.endswith(f'/{branch_name}'):
                                remote_branches.append(ref)
                    
                    if remote_branches:
                        # Checkout remote branch and create local tracking branch
                        remote_ref = remote_branches[0]
                        local_branch = repo.create_head(branch_name, remote_ref)
                        local_branch.set_tracking_branch(remote_ref)
                        local_branch.checkout()
                    else:
                        raise ValidationError(f"Branch '{branch_name}' not found")
            
            self.logger.info(f"Checked out branch: {branch_name}")
            return True
            
        except Exception as e:
            raise GitOperationError(f"Failed to checkout branch: {e}",
                                   git_command="checkout",
                                   repository_path=repo.working_dir,
                                   branch=branch_name)
    
    def merge_branch(self, repo: Repo,
                    branch_name: str,
                    no_ff: bool = False,
                    squash: bool = False) -> bool:
        """Merge a branch into current branch."""
        
        if not branch_name:
            raise ValidationError("Branch name is required", field="branch_name")
        
        try:
            # Check if branch exists
            if branch_name not in [b.name for b in repo.branches]:
                raise ValidationError(f"Branch '{branch_name}' not found")
            
            current_branch = repo.active_branch.name
            self.logger.info(f"Merging '{branch_name}' into '{current_branch}'")
            
            merge_args = [branch_name]
            if no_ff:
                merge_args.insert(0, '--no-ff')
            if squash:
                merge_args.insert(0, '--squash')
            
            repo.git.merge(*merge_args)
            
            self.logger.info(f"Merged '{branch_name}' successfully")
            return True
            
        except GitCommandError as e:
            if 'conflict' in str(e).lower():
                raise GitOperationError(f"Merge conflicts occurred. Please resolve conflicts and commit.")
            raise GitOperationError(f"Failed to merge branch: {e}")
        except Exception as e:
            raise GitOperationError(f"Failed to merge branch: {e}",
                                   git_command="merge",
                                   repository_path=repo.working_dir,
                                   branch=branch_name)
    
    def rebase_branch(self, repo: Repo,
                     onto_branch: str,
                     interactive: bool = False) -> bool:
        """Rebase current branch onto another branch."""
        
        if not onto_branch:
            raise ValidationError("Target branch is required", field="onto_branch")
        
        try:
            current_branch = repo.active_branch.name
            self.logger.info(f"Rebasing '{current_branch}' onto '{onto_branch}'")
            
            rebase_args = [onto_branch]
            if interactive:
                rebase_args.insert(0, '-i')
            
            repo.git.rebase(*rebase_args)
            
            self.logger.info(f"Rebased '{current_branch}' onto '{onto_branch}' successfully")
            return True
            
        except GitCommandError as e:
            if 'conflict' in str(e).lower():
                raise GitOperationError("Rebase conflicts occurred. Please resolve conflicts and continue rebase.")
            raise GitOperationError(f"Failed to rebase: {e}")
        except Exception as e:
            raise GitOperationError(f"Failed to rebase branch: {e}",
                                   git_command="rebase",
                                   repository_path=repo.working_dir,
                                   branch=onto_branch)
    
    def _is_valid_branch_name(self, name: str) -> bool:
        """Validate branch name according to Git rules."""
        
        if not name or len(name) == 0:
            return False
        
        # Git branch name rules (simplified)
        invalid_chars = [' ', '~', '^', ':', '?', '*', '[', '\\']
        if any(char in name for char in invalid_chars):
            return False
        
        if name.startswith('.') or name.endswith('.'):
            return False
        
        if name.startswith('-') or name.endswith('/'):
            return False
        
        if '..' in name or '@{' in name:
            return False
        
        return True


class VersionControl:
    """High-level version control operations."""
    
    def __init__(self, core):
        self.core = core
        self.git_ops = GitOperations(core)
        self.branch_manager = BranchManager(self.git_ops)
        self.logger = Logger("VersionControl")
    
    def setup_repository(self, local_path: str,
                        remote_url: Optional[str] = None,
                        initial_branch: str = "main") -> Repo:
        """Set up a new repository with best practices."""
        
        try:
            self.logger.info(f"Setting up repository at: {local_path}")
            
            # Initialize repository
            repo = self.git_ops.init_repository(local_path)
            
            # Create initial branch
            if initial_branch != "master":  # Git default
                try:
                    # Create and checkout new default branch
                    initial_commit = repo.git.commit('--allow-empty', '-m', 'Initial commit')
                    repo.git.checkout('-b', initial_branch)
                    repo.git.branch('-D', 'master')  # Delete master branch
                except:
                    pass  # Handle gracefully if already on correct branch
            
            # Add remote if provided
            if remote_url:
                self.git_ops.add_remote(repo, "origin", remote_url)
            
            # Create basic files
            self._create_initial_files(repo)
            
            self.logger.info("Repository setup completed")
            return repo
            
        except Exception as e:
            raise GitOperationError(f"Failed to setup repository: {e}",
                                   repository_path=local_path)
    
    def create_gitflow_branches(self, repo: Repo) -> Dict[str, bool]:
        """Create Git Flow branch structure."""
        
        try:
            results = {}
            
            # Ensure we're on main/master
            main_branch = "main" if "main" in [b.name for b in repo.branches] else "master"
            self.branch_manager.checkout_branch(repo, main_branch)
            
            # Create develop branch
            try:
                develop_info = self.branch_manager.create_branch(repo, "develop", checkout=False)
                results['develop'] = True
                self.logger.info("Created develop branch")
            except Exception as e:
                results['develop'] = False
                self.logger.warning(f"Failed to create develop branch: {e}")
            
            # Create release branch structure is typically done as needed
            # Create hotfix branch structure is typically done as needed
            # Create feature branch structure is typically done as needed
            
            results['setup_complete'] = all(results.values())
            return results
            
        except Exception as e:
            raise GitOperationError(f"Failed to create Git Flow branches: {e}",
                                   repository_path=repo.working_dir)
    
    def create_feature_branch(self, repo: Repo, 
                            feature_name: str,
                            base_branch: str = "develop") -> BranchInfo:
        """Create a feature branch following Git Flow."""
        
        if not feature_name:
            raise ValidationError("Feature name is required", field="feature_name")
        
        branch_name = f"feature/{feature_name}"
        
        try:
            # Ensure base branch is up to date
            self.branch_manager.checkout_branch(repo, base_branch)
            
            # Create feature branch
            feature_branch = self.branch_manager.create_branch(
                repo, branch_name, start_point=base_branch, checkout=True
            )
            
            self.logger.info(f"Created feature branch: {branch_name}")
            return feature_branch
            
        except Exception as e:
            raise GitOperationError(f"Failed to create feature branch: {e}",
                                   repository_path=repo.working_dir,
                                   branch=branch_name)
    
    def finish_feature_branch(self, repo: Repo,
                            feature_name: str,
                            delete_branch: bool = True,
                            target_branch: str = "develop") -> bool:
        """Finish a feature branch by merging and optionally deleting."""
        
        branch_name = f"feature/{feature_name}"
        
        try:
            # Checkout target branch
            self.branch_manager.checkout_branch(repo, target_branch)
            
            # Merge feature branch
            self.branch_manager.merge_branch(repo, branch_name, no_ff=True)
            
            # Delete feature branch if requested
            if delete_branch:
                self.branch_manager.delete_branch(repo, branch_name)
                self.logger.info(f"Deleted feature branch: {branch_name}")
            
            self.logger.info(f"Finished feature: {feature_name}")
            return True
            
        except Exception as e:
            raise GitOperationError(f"Failed to finish feature branch: {e}",
                                   repository_path=repo.working_dir,
                                   branch=branch_name)
    
    def create_release_branch(self, repo: Repo,
                            version: str,
                            base_branch: str = "develop") -> BranchInfo:
        """Create a release branch."""
        
        if not version:
            raise ValidationError("Version is required", field="version")
        
        branch_name = f"release/{version}"
        
        try:
            # Checkout base branch
            self.branch_manager.checkout_branch(repo, base_branch)
            
            # Create release branch
            release_branch = self.branch_manager.create_branch(
                repo, branch_name, start_point=base_branch, checkout=True
            )
            
            self.logger.info(f"Created release branch: {branch_name}")
            return release_branch
            
        except Exception as e:
            raise GitOperationError(f"Failed to create release branch: {e}",
                                   repository_path=repo.working_dir,
                                   branch=branch_name)
    
    def create_hotfix_branch(self, repo: Repo,
                           hotfix_name: str,
                           base_branch: str = "main") -> BranchInfo:
        """Create a hotfix branch."""
        
        if not hotfix_name:
            raise ValidationError("Hotfix name is required", field="hotfix_name")
        
        branch_name = f"hotfix/{hotfix_name}"
        
        try:
            # Checkout base branch
            self.branch_manager.checkout_branch(repo, base_branch)
            
            # Create hotfix branch
            hotfix_branch = self.branch_manager.create_branch(
                repo, branch_name, start_point=base_branch, checkout=True
            )
            
            self.logger.info(f"Created hotfix branch: {branch_name}")
            return hotfix_branch
            
        except Exception as e:
            raise GitOperationError(f"Failed to create hotfix branch: {e}",
                                   repository_path=repo.working_dir,
                                   branch=branch_name)
    
    def _create_initial_files(self, repo: Repo):
        """Create initial files for a new repository."""
        
        if repo.bare:
            return  # Skip for bare repositories
        
        try:
            repo_path = Path(repo.working_dir)
            
            # Create .gitignore if it doesn't exist
            gitignore_path = repo_path / '.gitignore'
            if not gitignore_path.exists():
                gitignore_content = self._get_default_gitignore()
                gitignore_path.write_text(gitignore_content)
                self.logger.info("Created .gitignore file")
            
            # Create README.md if it doesn't exist
            readme_path = repo_path / 'README.md'
            if not readme_path.exists():
                readme_content = f"# {repo_path.name}\n\nDescription of your project.\n"
                readme_path.write_text(readme_content)
                self.logger.info("Created README.md file")
            
        except Exception as e:
            self.logger.warning(f"Failed to create initial files: {e}")
    
    def _get_default_gitignore(self) -> str:
        """Get default .gitignore content."""
        return """\
# Operating System
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/

# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.egg-info/

# Build outputs
dist/
build/
*.build/

# Environment
.env
.env.local
.env.*.local

# Temporary files
*.tmp
*.temp
.cache/
"""


__all__ = [
    'GitOperations',
    'BranchManager', 
    'VersionControl',
    'GitConfig',
    'BranchInfo',
    'CommitInfo'
]