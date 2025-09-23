"""
MeroHub Repository Management Module
Author: MERO (Telegram: @QP4RM)

Comprehensive repository management with advanced analytics, statistics,
and operations for GitHub repositories. Provides full CRUD operations
and detailed analysis capabilities.
"""

import os
import json
import time
import tempfile
import shutil
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import zipfile
import tarfile
from urllib.parse import urlparse
import git
from git import Repo, InvalidGitRepositoryError
from .exceptions import (
    RepositoryError, ValidationError, APIError, 
    GitOperationError, validate_repository_name
)
from .utils import Logger, DataProcessor, retry_on_exception, timed_cache


@dataclass
class RepositoryStats:
    """Container for repository statistics."""
    
    name: str
    full_name: str
    owner: str
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime
    size: int
    stargazers_count: int
    watchers_count: int
    forks_count: int
    open_issues_count: int
    subscribers_count: int
    network_count: int
    language: Optional[str]
    languages: Dict[str, int]
    topics: List[str]
    license_name: Optional[str]
    default_branch: str
    has_issues: bool
    has_projects: bool
    has_wiki: bool
    has_pages: bool
    has_downloads: bool
    archived: bool
    disabled: bool
    private: bool
    fork: bool
    
    # Computed metrics
    activity_score: float = 0.0
    popularity_score: float = 0.0
    health_score: float = 0.0
    freshness_score: float = 0.0
    community_score: float = 0.0


class RepositoryAnalyzer:
    """Advanced repository analysis and metrics calculation."""
    
    def __init__(self, core):
        self.core = core
        self.logger = Logger("RepositoryAnalyzer")
        self.data_processor = DataProcessor()
        self._cache = {}
        self._cache_lock = threading.Lock()
    
    @timed_cache(seconds=300)  # Cache for 5 minutes
    def analyze_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Comprehensive repository analysis."""
        self.logger.info(f"Analyzing repository {owner}/{repo}")
        
        try:
            # Get basic repository info
            repo_data = self.core.get_json(f'/repos/{owner}/{repo}')
            
            # Get additional data in parallel
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {
                    'contributors': executor.submit(self._get_contributors, owner, repo),
                    'commits': executor.submit(self._get_recent_commits, owner, repo),
                    'languages': executor.submit(self._get_languages, owner, repo),
                    'releases': executor.submit(self._get_releases, owner, repo),
                    'issues': executor.submit(self._get_issues_analysis, owner, repo),
                    'pull_requests': executor.submit(self._get_pr_analysis, owner, repo),
                    'traffic': executor.submit(self._get_traffic_stats, owner, repo),
                    'community': executor.submit(self._get_community_profile, owner, repo),
                    'security': executor.submit(self._get_security_analysis, owner, repo),
                    'dependency': executor.submit(self._get_dependency_analysis, owner, repo)
                }
                
                analysis_data = {'repository': repo_data}
                
                for key, future in futures.items():
                    try:
                        analysis_data[key] = future.result(timeout=30)
                    except Exception as e:
                        self.logger.warning(f"Failed to get {key} data: {e}")
                        analysis_data[key] = {}
            
            # Calculate comprehensive metrics
            analysis_data['metrics'] = self._calculate_metrics(analysis_data)
            analysis_data['scores'] = self._calculate_scores(analysis_data)
            analysis_data['insights'] = self._generate_insights(analysis_data)
            analysis_data['recommendations'] = self._generate_recommendations(analysis_data)
            
            # Add timestamp
            analysis_data['analysis_timestamp'] = datetime.now().isoformat()
            
            return analysis_data
            
        except Exception as e:
            raise RepositoryError(f"Failed to analyze repository: {e}", 
                                repository=f"{owner}/{repo}", operation="analyze")
    
    def _get_contributors(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Get repository contributors with detailed statistics."""
        try:
            contributors = self.core.paginate(f'/repos/{owner}/{repo}/contributors',
                                            per_page=100, max_pages=10)
            
            # Enhance contributor data
            for contributor in contributors:
                # Calculate contribution percentage
                total_contributions = sum(c['contributions'] for c in contributors)
                if total_contributions > 0:
                    contributor['contribution_percentage'] = (
                        contributor['contributions'] / total_contributions * 100
                    )
                else:
                    contributor['contribution_percentage'] = 0
                
                # Get contributor details
                try:
                    if not contributor.get('type') == 'Bot':
                        user_data = self.core.get_json(f"/users/{contributor['login']}")
                        contributor.update({
                            'name': user_data.get('name'),
                            'company': user_data.get('company'),
                            'location': user_data.get('location'),
                            'public_repos': user_data.get('public_repos', 0),
                            'followers': user_data.get('followers', 0),
                            'following': user_data.get('following', 0)
                        })
                except:
                    pass  # Skip if user data unavailable
            
            return contributors[:50]  # Limit to top 50 contributors
            
        except Exception as e:
            self.logger.error(f"Failed to get contributors: {e}")
            return []
    
    def _get_recent_commits(self, owner: str, repo: str, days: int = 30) -> Dict[str, Any]:
        """Get recent commit activity analysis."""
        try:
            since = (datetime.now() - timedelta(days=days)).isoformat()
            commits = self.core.paginate(f'/repos/{owner}/{repo}/commits',
                                       params={'since': since},
                                       per_page=100, max_pages=10)
            
            # Analyze commit patterns
            commit_analysis = {
                'total_commits': len(commits),
                'unique_authors': len(set(c['commit']['author']['email'] for c in commits if c.get('commit'))),
                'commits_by_day': {},
                'commits_by_hour': {},
                'commits_by_author': {},
                'average_message_length': 0,
                'merge_commits': 0,
                'commit_frequency': 0
            }
            
            if commits:
                # Daily distribution
                for commit in commits:
                    commit_date = commit['commit']['author']['date'][:10]  # YYYY-MM-DD
                    commit_hour = int(commit['commit']['author']['date'][11:13])
                    author = commit['commit']['author']['email']
                    
                    commit_analysis['commits_by_day'][commit_date] = (
                        commit_analysis['commits_by_day'].get(commit_date, 0) + 1
                    )
                    commit_analysis['commits_by_hour'][commit_hour] = (
                        commit_analysis['commits_by_hour'].get(commit_hour, 0) + 1
                    )
                    commit_analysis['commits_by_author'][author] = (
                        commit_analysis['commits_by_author'].get(author, 0) + 1
                    )
                    
                    # Check if merge commit
                    if commit.get('parents') and len(commit['parents']) > 1:
                        commit_analysis['merge_commits'] += 1
                
                # Calculate averages
                messages = [c['commit']['message'] for c in commits]
                if messages:
                    commit_analysis['average_message_length'] = (
                        sum(len(msg) for msg in messages) / len(messages)
                    )
                
                commit_analysis['commit_frequency'] = len(commits) / days
            
            return commit_analysis
            
        except Exception as e:
            self.logger.error(f"Failed to get commit analysis: {e}")
            return {}
    
    def _get_languages(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get detailed language statistics."""
        try:
            languages = self.core.get_json(f'/repos/{owner}/{repo}/languages')
            
            if languages:
                total_bytes = sum(languages.values())
                language_stats = {}
                
                for language, bytes_count in languages.items():
                    percentage = (bytes_count / total_bytes) * 100
                    language_stats[language] = {
                        'bytes': bytes_count,
                        'percentage': round(percentage, 2)
                    }
                
                # Sort by percentage
                sorted_languages = sorted(language_stats.items(), 
                                        key=lambda x: x[1]['percentage'], 
                                        reverse=True)
                
                return {
                    'languages': dict(sorted_languages),
                    'primary_language': sorted_languages[0][0] if sorted_languages else None,
                    'language_count': len(languages),
                    'total_bytes': total_bytes
                }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Failed to get languages: {e}")
            return {}
    
    def _get_releases(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get release information and patterns."""
        try:
            releases = self.core.paginate(f'/repos/{owner}/{repo}/releases',
                                        per_page=50, max_pages=5)
            
            if not releases:
                return {'total_releases': 0, 'latest_release': None}
            
            # Analyze release patterns
            release_dates = []
            for release in releases:
                if release.get('published_at'):
                    release_dates.append(datetime.fromisoformat(
                        release['published_at'].replace('Z', '+00:00')
                    ))
            
            release_analysis = {
                'total_releases': len(releases),
                'latest_release': releases[0] if releases else None,
                'release_frequency': 0,
                'average_time_between_releases': 0,
                'pre_releases': sum(1 for r in releases if r.get('prerelease')),
                'draft_releases': sum(1 for r in releases if r.get('draft'))
            }
            
            if len(release_dates) > 1:
                # Calculate time between releases
                time_diffs = []
                for i in range(len(release_dates) - 1):
                    diff = (release_dates[i] - release_dates[i + 1]).days
                    time_diffs.append(diff)
                
                if time_diffs:
                    release_analysis['average_time_between_releases'] = (
                        sum(time_diffs) / len(time_diffs)
                    )
                    
                    # Calculate frequency (releases per year)
                    if release_dates:
                        time_span = (release_dates[0] - release_dates[-1]).days
                        if time_span > 0:
                            release_analysis['release_frequency'] = (
                                len(releases) * 365 / time_span
                            )
            
            return release_analysis
            
        except Exception as e:
            self.logger.error(f"Failed to get releases: {e}")
            return {}
    
    def _get_issues_analysis(self, owner: str, repo: str) -> Dict[str, Any]:
        """Analyze repository issues."""
        try:
            # Get open and closed issues
            open_issues = self.core.paginate(f'/repos/{owner}/{repo}/issues',
                                           params={'state': 'open'},
                                           per_page=100, max_pages=5)
            
            closed_issues = self.core.paginate(f'/repos/{owner}/{repo}/issues',
                                             params={'state': 'closed'},
                                             per_page=100, max_pages=5)
            
            all_issues = open_issues + closed_issues
            
            # Filter out pull requests (they appear in issues API)
            issues_only = [issue for issue in all_issues if 'pull_request' not in issue]
            
            issue_analysis = {
                'total_issues': len(issues_only),
                'open_issues': len([i for i in issues_only if i['state'] == 'open']),
                'closed_issues': len([i for i in issues_only if i['state'] == 'closed']),
                'issues_with_labels': 0,
                'issues_with_assignees': 0,
                'issues_with_milestones': 0,
                'average_comments_per_issue': 0,
                'most_common_labels': {},
                'issue_authors': {},
                'response_time_analysis': {}
            }
            
            if issues_only:
                # Detailed analysis
                label_count = {}
                author_count = {}
                comment_counts = []
                
                for issue in issues_only:
                    # Count labels
                    if issue.get('labels'):
                        issue_analysis['issues_with_labels'] += 1
                        for label in issue['labels']:
                            label_name = label['name']
                            label_count[label_name] = label_count.get(label_name, 0) + 1
                    
                    # Count assignees
                    if issue.get('assignees'):
                        issue_analysis['issues_with_assignees'] += 1
                    
                    # Count milestones
                    if issue.get('milestone'):
                        issue_analysis['issues_with_milestones'] += 1
                    
                    # Count comments
                    comment_counts.append(issue.get('comments', 0))
                    
                    # Count authors
                    author = issue['user']['login']
                    author_count[author] = author_count.get(author, 0) + 1
                
                # Calculate averages and statistics
                if comment_counts:
                    issue_analysis['average_comments_per_issue'] = (
                        sum(comment_counts) / len(comment_counts)
                    )
                
                # Most common labels (top 10)
                issue_analysis['most_common_labels'] = dict(
                    sorted(label_count.items(), key=lambda x: x[1], reverse=True)[:10]
                )
                
                # Most active issue authors (top 10)
                issue_analysis['issue_authors'] = dict(
                    sorted(author_count.items(), key=lambda x: x[1], reverse=True)[:10]
                )
            
            return issue_analysis
            
        except Exception as e:
            self.logger.error(f"Failed to get issues analysis: {e}")
            return {}
    
    def _get_pr_analysis(self, owner: str, repo: str) -> Dict[str, Any]:
        """Analyze pull requests."""
        try:
            # Get recent pull requests
            open_prs = self.core.paginate(f'/repos/{owner}/{repo}/pulls',
                                        params={'state': 'open'},
                                        per_page=50, max_pages=3)
            
            closed_prs = self.core.paginate(f'/repos/{owner}/{repo}/pulls',
                                          params={'state': 'closed'},
                                          per_page=50, max_pages=3)
            
            all_prs = open_prs + closed_prs
            
            pr_analysis = {
                'total_prs': len(all_prs),
                'open_prs': len(open_prs),
                'closed_prs': len(closed_prs),
                'merged_prs': len([pr for pr in closed_prs if pr.get('merged_at')]),
                'draft_prs': len([pr for pr in all_prs if pr.get('draft')]),
                'average_comments_per_pr': 0,
                'pr_authors': {},
                'merge_time_analysis': {}
            }
            
            if all_prs:
                comment_counts = []
                author_count = {}
                merge_times = []
                
                for pr in all_prs:
                    # Count comments
                    comment_counts.append(pr.get('comments', 0))
                    
                    # Count authors
                    author = pr['user']['login']
                    author_count[author] = author_count.get(author, 0) + 1
                    
                    # Calculate merge time for merged PRs
                    if pr.get('merged_at') and pr.get('created_at'):
                        created = datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00'))
                        merged = datetime.fromisoformat(pr['merged_at'].replace('Z', '+00:00'))
                        merge_time = (merged - created).total_seconds() / 3600  # hours
                        merge_times.append(merge_time)
                
                # Calculate statistics
                if comment_counts:
                    pr_analysis['average_comments_per_pr'] = (
                        sum(comment_counts) / len(comment_counts)
                    )
                
                pr_analysis['pr_authors'] = dict(
                    sorted(author_count.items(), key=lambda x: x[1], reverse=True)[:10]
                )
                
                if merge_times:
                    pr_analysis['merge_time_analysis'] = {
                        'average_merge_time_hours': sum(merge_times) / len(merge_times),
                        'median_merge_time_hours': statistics.median(merge_times),
                        'fastest_merge_hours': min(merge_times),
                        'slowest_merge_hours': max(merge_times)
                    }
            
            return pr_analysis
            
        except Exception as e:
            self.logger.error(f"Failed to get PR analysis: {e}")
            return {}
    
    def _get_traffic_stats(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository traffic statistics (requires push access)."""
        try:
            # These endpoints require push access to the repository
            traffic_data = {}
            
            try:
                views = self.core.get_json(f'/repos/{owner}/{repo}/traffic/views')
                traffic_data['views'] = views
            except APIError as e:
                if e.status_code == 403:
                    traffic_data['views'] = {'error': 'No access to traffic data'}
                else:
                    raise
            
            try:
                clones = self.core.get_json(f'/repos/{owner}/{repo}/traffic/clones')
                traffic_data['clones'] = clones
            except APIError as e:
                if e.status_code == 403:
                    traffic_data['clones'] = {'error': 'No access to traffic data'}
                else:
                    raise
            
            try:
                popular_paths = self.core.get_json(f'/repos/{owner}/{repo}/traffic/popular/paths')
                traffic_data['popular_paths'] = popular_paths
            except APIError as e:
                if e.status_code == 403:
                    traffic_data['popular_paths'] = {'error': 'No access to traffic data'}
                else:
                    raise
            
            try:
                popular_referrers = self.core.get_json(f'/repos/{owner}/{repo}/traffic/popular/referrers')
                traffic_data['popular_referrers'] = popular_referrers
            except APIError as e:
                if e.status_code == 403:
                    traffic_data['popular_referrers'] = {'error': 'No access to traffic data'}
                else:
                    raise
            
            return traffic_data
            
        except Exception as e:
            self.logger.warning(f"Failed to get traffic stats: {e}")
            return {'error': str(e)}
    
    def _get_community_profile(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get community profile and health metrics."""
        try:
            community = self.core.get_json(f'/repos/{owner}/{repo}/community/profile')
            return community
            
        except Exception as e:
            self.logger.error(f"Failed to get community profile: {e}")
            return {}
    
    def _get_security_analysis(self, owner: str, repo: str) -> Dict[str, Any]:
        """Analyze repository security features."""
        try:
            security_analysis = {}
            
            # Check for security policy
            try:
                security_policy = self.core.get_json(f'/repos/{owner}/{repo}/contents/.github/SECURITY.md')
                security_analysis['has_security_policy'] = True
                security_analysis['security_policy_size'] = security_policy.get('size', 0)
            except APIError:
                security_analysis['has_security_policy'] = False
            
            # Check for vulnerability alerts (requires admin access)
            try:
                alerts = self.core.get_json(f'/repos/{owner}/{repo}/vulnerability-alerts')
                security_analysis['vulnerability_alerts_enabled'] = True
            except APIError as e:
                if e.status_code == 404:
                    security_analysis['vulnerability_alerts_enabled'] = False
                else:
                    security_analysis['vulnerability_alerts_enabled'] = 'unknown'
            
            return security_analysis
            
        except Exception as e:
            self.logger.error(f"Failed to get security analysis: {e}")
            return {}
    
    def _get_dependency_analysis(self, owner: str, repo: str) -> Dict[str, Any]:
        """Analyze repository dependencies."""
        try:
            dependency_analysis = {
                'package_files': [],
                'dependency_count': 0,
                'security_vulnerabilities': 0
            }
            
            # Common dependency files
            dependency_files = [
                'package.json', 'requirements.txt', 'Gemfile', 'pom.xml',
                'build.gradle', 'composer.json', 'Cargo.toml', 'go.mod',
                'setup.py', 'pyproject.toml'
            ]
            
            for file_name in dependency_files:
                try:
                    file_info = self.core.get_json(f'/repos/{owner}/{repo}/contents/{file_name}')
                    dependency_analysis['package_files'].append({
                        'name': file_name,
                        'size': file_info.get('size', 0),
                        'sha': file_info.get('sha')
                    })
                except APIError:
                    pass  # File doesn't exist
            
            return dependency_analysis
            
        except Exception as e:
            self.logger.error(f"Failed to get dependency analysis: {e}")
            return {}
    
    def _calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive repository metrics."""
        repo = data.get('repository', {})
        
        metrics = {
            'activity_score': self._calculate_activity_score(data),
            'popularity_score': self._calculate_popularity_score(data),
            'health_score': self._calculate_health_score(data),
            'freshness_score': self._calculate_freshness_score(data),
            'community_score': self._calculate_community_score(data),
            'code_quality_score': self._calculate_code_quality_score(data),
            'maintenance_score': self._calculate_maintenance_score(data)
        }
        
        # Overall score (weighted average)
        weights = {
            'activity_score': 0.2,
            'popularity_score': 0.15,
            'health_score': 0.2,
            'freshness_score': 0.15,
            'community_score': 0.15,
            'code_quality_score': 0.1,
            'maintenance_score': 0.05
        }
        
        metrics['overall_score'] = sum(
            metrics[key] * weight for key, weight in weights.items()
        )
        
        return metrics
    
    def _calculate_activity_score(self, data: Dict[str, Any]) -> float:
        """Calculate repository activity score (0-100)."""
        commits = data.get('commits', {})
        issues = data.get('issues', {})
        prs = data.get('pull_requests', {})
        
        score = 0
        
        # Recent commits (40 points)
        commit_count = commits.get('total_commits', 0)
        if commit_count > 0:
            score += min(commit_count * 2, 40)  # Max 40 points
        
        # Issue activity (30 points)
        total_issues = issues.get('total_issues', 0)
        if total_issues > 0:
            score += min(total_issues * 0.5, 30)  # Max 30 points
        
        # PR activity (30 points)
        total_prs = prs.get('total_prs', 0)
        if total_prs > 0:
            score += min(total_prs * 0.8, 30)  # Max 30 points
        
        return min(score, 100)
    
    def _calculate_popularity_score(self, data: Dict[str, Any]) -> float:
        """Calculate repository popularity score (0-100)."""
        repo = data.get('repository', {})
        
        stars = repo.get('stargazers_count', 0)
        forks = repo.get('forks_count', 0)
        watchers = repo.get('watchers_count', 0)
        
        # Logarithmic scaling for large numbers
        import math
        
        star_score = min(math.log10(stars + 1) * 20, 60)  # Max 60 points
        fork_score = min(math.log10(forks + 1) * 15, 25)  # Max 25 points
        watcher_score = min(math.log10(watchers + 1) * 10, 15)  # Max 15 points
        
        return star_score + fork_score + watcher_score
    
    def _calculate_health_score(self, data: Dict[str, Any]) -> float:
        """Calculate repository health score (0-100)."""
        repo = data.get('repository', {})
        community = data.get('community', {})
        
        score = 0
        
        # Has README
        if community.get('files', {}).get('readme'):
            score += 20
        
        # Has LICENSE
        if repo.get('license'):
            score += 15
        
        # Has description
        if repo.get('description'):
            score += 10
        
        # Has issues enabled
        if repo.get('has_issues'):
            score += 10
        
        # Has contributing guide
        if community.get('files', {}).get('contributing'):
            score += 15
        
        # Has code of conduct
        if community.get('files', {}).get('code_of_conduct'):
            score += 10
        
        # Recent activity (last push)
        if repo.get('pushed_at'):
            pushed_at = datetime.fromisoformat(repo['pushed_at'].replace('Z', '+00:00'))
            days_since_push = (datetime.now(pushed_at.tzinfo) - pushed_at).days
            if days_since_push < 30:
                score += 20
            elif days_since_push < 90:
                score += 10
        
        return min(score, 100)
    
    def _calculate_freshness_score(self, data: Dict[str, Any]) -> float:
        """Calculate repository freshness score (0-100)."""
        repo = data.get('repository', {})
        commits = data.get('commits', {})
        
        score = 0
        
        # Recent pushes
        if repo.get('pushed_at'):
            pushed_at = datetime.fromisoformat(repo['pushed_at'].replace('Z', '+00:00'))
            days_since_push = (datetime.now(pushed_at.tzinfo) - pushed_at).days
            
            if days_since_push < 7:
                score += 40
            elif days_since_push < 30:
                score += 30
            elif days_since_push < 90:
                score += 20
            elif days_since_push < 180:
                score += 10
        
        # Commit frequency
        commit_frequency = commits.get('commit_frequency', 0)
        if commit_frequency > 1:  # More than 1 commit per day
            score += 30
        elif commit_frequency > 0.5:  # More than 0.5 commits per day
            score += 20
        elif commit_frequency > 0.1:  # More than 0.1 commits per day
            score += 10
        
        # Recent releases
        releases = data.get('releases', {})
        if releases.get('latest_release'):
            latest_release = releases['latest_release']
            if latest_release.get('published_at'):
                published_at = datetime.fromisoformat(
                    latest_release['published_at'].replace('Z', '+00:00')
                )
                days_since_release = (datetime.now(published_at.tzinfo) - published_at).days
                if days_since_release < 30:
                    score += 30
                elif days_since_release < 90:
                    score += 20
                elif days_since_release < 180:
                    score += 10
        
        return min(score, 100)
    
    def _calculate_community_score(self, data: Dict[str, Any]) -> float:
        """Calculate repository community score (0-100)."""
        contributors = data.get('contributors', [])
        issues = data.get('issues', {})
        prs = data.get('pull_requests', {})
        
        score = 0
        
        # Number of contributors
        contributor_count = len(contributors)
        if contributor_count > 20:
            score += 30
        elif contributor_count > 10:
            score += 25
        elif contributor_count > 5:
            score += 20
        elif contributor_count > 1:
            score += 15
        
        # Contributor diversity (not dominated by single contributor)
        if contributors:
            top_contributor_percentage = contributors[0].get('contribution_percentage', 100)
            if top_contributor_percentage < 50:
                score += 20
            elif top_contributor_percentage < 70:
                score += 15
            elif top_contributor_percentage < 90:
                score += 10
        
        # Issue engagement
        avg_comments = issues.get('average_comments_per_issue', 0)
        if avg_comments > 3:
            score += 15
        elif avg_comments > 1:
            score += 10
        elif avg_comments > 0:
            score += 5
        
        # PR engagement
        avg_pr_comments = prs.get('average_comments_per_pr', 0)
        if avg_pr_comments > 3:
            score += 15
        elif avg_pr_comments > 1:
            score += 10
        elif avg_pr_comments > 0:
            score += 5
        
        # External contributors (forks with PRs)
        fork_count = data.get('repository', {}).get('forks_count', 0)
        if fork_count > 10:
            score += 20
        elif fork_count > 5:
            score += 15
        elif fork_count > 0:
            score += 10
        
        return min(score, 100)
    
    def _calculate_code_quality_score(self, data: Dict[str, Any]) -> float:
        """Calculate code quality score based on available indicators."""
        score = 50  # Base score
        
        # TODO: Implement more sophisticated code quality metrics
        # This would require analyzing actual code content
        
        return score
    
    def _calculate_maintenance_score(self, data: Dict[str, Any]) -> float:
        """Calculate maintenance score."""
        issues = data.get('issues', {})
        prs = data.get('pull_requests', {})
        
        score = 0
        
        # Issue resolution rate
        total_issues = issues.get('total_issues', 0)
        closed_issues = issues.get('closed_issues', 0)
        
        if total_issues > 0:
            resolution_rate = closed_issues / total_issues
            score += resolution_rate * 40
        
        # PR merge rate
        total_prs = prs.get('total_prs', 0)
        merged_prs = prs.get('merged_prs', 0)
        
        if total_prs > 0:
            merge_rate = merged_prs / total_prs
            score += merge_rate * 40
        
        # Recent maintenance activity
        commits = data.get('commits', {})
        if commits.get('total_commits', 0) > 0:
            score += 20
        
        return min(score, 100)
    
    def _calculate_scores(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate all scores and provide letter grades."""
        metrics = data.get('metrics', {})
        
        def get_letter_grade(score: float) -> str:
            if score >= 90:
                return 'A+'
            elif score >= 85:
                return 'A'
            elif score >= 80:
                return 'A-'
            elif score >= 75:
                return 'B+'
            elif score >= 70:
                return 'B'
            elif score >= 65:
                return 'B-'
            elif score >= 60:
                return 'C+'
            elif score >= 55:
                return 'C'
            elif score >= 50:
                return 'C-'
            elif score >= 45:
                return 'D+'
            elif score >= 40:
                return 'D'
            else:
                return 'F'
        
        scores = {}
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                scores[key] = {
                    'score': round(value, 1),
                    'grade': get_letter_grade(value)
                }
        
        return scores
    
    def _generate_insights(self, data: Dict[str, Any]) -> List[str]:
        """Generate insights about the repository."""
        insights = []
        repo = data.get('repository', {})
        metrics = data.get('metrics', {})
        
        # Activity insights
        if metrics.get('activity_score', 0) > 80:
            insights.append("🔥 This repository is very active with frequent commits and contributions")
        elif metrics.get('activity_score', 0) < 30:
            insights.append("💤 This repository has low activity - consider encouraging more contributions")
        
        # Popularity insights
        stars = repo.get('stargazers_count', 0)
        if stars > 1000:
            insights.append(f"⭐ Popular project with {stars:,} stars")
        elif stars > 100:
            insights.append(f"📈 Growing project with {stars} stars")
        
        # Language insights
        languages = data.get('languages', {})
        if languages.get('language_count', 0) > 5:
            insights.append(f"🌈 Multi-language project with {languages['language_count']} languages")
        
        # Community insights
        contributors = data.get('contributors', [])
        if len(contributors) > 50:
            insights.append(f"👥 Strong community with {len(contributors)}+ contributors")
        elif len(contributors) == 1:
            insights.append("👤 Single contributor - consider encouraging community participation")
        
        # Maintenance insights
        if metrics.get('freshness_score', 0) < 40:
            insights.append("⚠️ Repository may need attention - no recent activity")
        
        return insights
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        repo = data.get('repository', {})
        community = data.get('community', {})
        metrics = data.get('metrics', {})
        
        # Documentation recommendations
        if not repo.get('description'):
            recommendations.append("📝 Add a clear repository description")
        
        if not community.get('files', {}).get('readme'):
            recommendations.append("📖 Add a comprehensive README file")
        
        if not repo.get('license'):
            recommendations.append("⚖️ Add a license to clarify usage rights")
        
        # Community recommendations
        if not community.get('files', {}).get('contributing'):
            recommendations.append("🤝 Add contribution guidelines to encourage participation")
        
        if not community.get('files', {}).get('code_of_conduct'):
            recommendations.append("📋 Add a code of conduct to set community standards")
        
        # Issues and PR recommendations
        if not repo.get('has_issues'):
            recommendations.append("🐛 Enable issues to allow bug reports and feature requests")
        
        # Security recommendations
        security = data.get('security', {})
        if not security.get('has_security_policy'):
            recommendations.append("🔒 Add a security policy to handle vulnerability reports")
        
        # Activity recommendations
        if metrics.get('activity_score', 0) < 50:
            recommendations.append("🚀 Increase activity with regular commits and releases")
        
        # Release recommendations
        releases = data.get('releases', {})
        if releases.get('total_releases', 0) == 0:
            recommendations.append("🏷️ Create releases to make it easy for users to track versions")
        
        return recommendations


class RepositoryManager:
    """Comprehensive repository management with full CRUD operations."""
    
    def __init__(self, core):
        self.core = core
        self.logger = Logger("RepositoryManager")
        self.analyzer = RepositoryAnalyzer(core)
        self.data_processor = DataProcessor()
    
    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get detailed repository information."""
        validate_repository_name(repo)
        
        try:
            return self.core.get_json(f'/repos/{owner}/{repo}')
        except Exception as e:
            raise RepositoryError(f"Failed to get repository: {e}",
                                repository=f"{owner}/{repo}", operation="get")
    
    def create_repository(self, name: str, 
                         description: str = "",
                         private: bool = False,
                         auto_init: bool = True,
                         gitignore_template: Optional[str] = None,
                         license_template: Optional[str] = None,
                         allow_squash_merge: bool = True,
                         allow_merge_commit: bool = True,
                         allow_rebase_merge: bool = True,
                         delete_branch_on_merge: bool = False,
                         has_issues: bool = True,
                         has_projects: bool = True,
                         has_wiki: bool = True) -> Dict[str, Any]:
        """Create a new repository."""
        
        validate_repository_name(name)
        
        payload = {
            'name': name,
            'description': description,
            'private': private,
            'auto_init': auto_init,
            'allow_squash_merge': allow_squash_merge,
            'allow_merge_commit': allow_merge_commit,
            'allow_rebase_merge': allow_rebase_merge,
            'delete_branch_on_merge': delete_branch_on_merge,
            'has_issues': has_issues,
            'has_projects': has_projects,
            'has_wiki': has_wiki
        }
        
        if gitignore_template:
            payload['gitignore_template'] = gitignore_template
        
        if license_template:
            payload['license_template'] = license_template
        
        try:
            self.logger.info(f"Creating repository: {name}")
            return self.core.post_json('/user/repos', json_data=payload)
            
        except Exception as e:
            raise RepositoryError(f"Failed to create repository: {e}",
                                repository=name, operation="create")
    
    def update_repository(self, owner: str, repo: str, **kwargs) -> Dict[str, Any]:
        """Update repository settings."""
        validate_repository_name(repo)
        
        try:
            self.logger.info(f"Updating repository: {owner}/{repo}")
            return self.core.post_json(f'/repos/{owner}/{repo}', json_data=kwargs)
            
        except Exception as e:
            raise RepositoryError(f"Failed to update repository: {e}",
                                repository=f"{owner}/{repo}", operation="update")
    
    def delete_repository(self, owner: str, repo: str) -> bool:
        """Delete a repository."""
        validate_repository_name(repo)
        
        try:
            self.logger.warning(f"Deleting repository: {owner}/{repo}")
            response = self.core.delete(f'/repos/{owner}/{repo}')
            return response.status_code == 204
            
        except Exception as e:
            raise RepositoryError(f"Failed to delete repository: {e}",
                                repository=f"{owner}/{repo}", operation="delete")
    
    def fork_repository(self, owner: str, repo: str,
                       organization: Optional[str] = None) -> Dict[str, Any]:
        """Fork a repository."""
        validate_repository_name(repo)
        
        payload = {}
        if organization:
            payload['organization'] = organization
        
        try:
            self.logger.info(f"Forking repository: {owner}/{repo}")
            return self.core.post_json(f'/repos/{owner}/{repo}/forks', 
                                     json_data=payload if payload else None)
            
        except Exception as e:
            raise RepositoryError(f"Failed to fork repository: {e}",
                                repository=f"{owner}/{repo}", operation="fork")
    
    def star_repository(self, owner: str, repo: str) -> bool:
        """Star a repository."""
        validate_repository_name(repo)
        
        try:
            response = self.core.put(f'/user/starred/{owner}/{repo}')
            return response.status_code == 204
            
        except Exception as e:
            raise RepositoryError(f"Failed to star repository: {e}",
                                repository=f"{owner}/{repo}", operation="star")
    
    def unstar_repository(self, owner: str, repo: str) -> bool:
        """Unstar a repository."""
        validate_repository_name(repo)
        
        try:
            response = self.core.delete(f'/user/starred/{owner}/{repo}')
            return response.status_code == 204
            
        except Exception as e:
            raise RepositoryError(f"Failed to unstar repository: {e}",
                                repository=f"{owner}/{repo}", operation="unstar")
    
    def watch_repository(self, owner: str, repo: str, 
                        subscribed: bool = True,
                        ignored: bool = False) -> bool:
        """Watch/subscribe to a repository."""
        validate_repository_name(repo)
        
        payload = {
            'subscribed': subscribed,
            'ignored': ignored
        }
        
        try:
            response = self.core.put(f'/repos/{owner}/{repo}/subscription',
                                   json_data=payload)
            return response.status_code == 200
            
        except Exception as e:
            raise RepositoryError(f"Failed to watch repository: {e}",
                                repository=f"{owner}/{repo}", operation="watch")
    
    def unwatch_repository(self, owner: str, repo: str) -> bool:
        """Unwatch/unsubscribe from a repository."""
        validate_repository_name(repo)
        
        try:
            response = self.core.delete(f'/repos/{owner}/{repo}/subscription')
            return response.status_code == 204
            
        except Exception as e:
            raise RepositoryError(f"Failed to unwatch repository: {e}",
                                repository=f"{owner}/{repo}", operation="unwatch")
    
    def get_contributors(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Get repository contributors."""
        validate_repository_name(repo)
        
        try:
            return self.core.paginate(f'/repos/{owner}/{repo}/contributors')
        except Exception as e:
            raise RepositoryError(f"Failed to get contributors: {e}",
                                repository=f"{owner}/{repo}", operation="get_contributors")
    
    def get_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Get repository languages."""
        validate_repository_name(repo)
        
        try:
            return self.core.get_json(f'/repos/{owner}/{repo}/languages')
        except Exception as e:
            raise RepositoryError(f"Failed to get languages: {e}",
                                repository=f"{owner}/{repo}", operation="get_languages")
    
    def get_repository_stats(self, owner: str, repo: str) -> RepositoryStats:
        """Get comprehensive repository statistics."""
        validate_repository_name(repo)
        
        try:
            # Get basic repository data
            repo_data = self.get_repository(owner, repo)
            languages = self.get_languages(owner, repo)
            
            # Create RepositoryStats object
            return RepositoryStats(
                name=repo_data['name'],
                full_name=repo_data['full_name'],
                owner=repo_data['owner']['login'],
                created_at=datetime.fromisoformat(repo_data['created_at'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(repo_data['updated_at'].replace('Z', '+00:00')),
                pushed_at=datetime.fromisoformat(repo_data['pushed_at'].replace('Z', '+00:00')),
                size=repo_data['size'],
                stargazers_count=repo_data['stargazers_count'],
                watchers_count=repo_data['watchers_count'],
                forks_count=repo_data['forks_count'],
                open_issues_count=repo_data['open_issues_count'],
                subscribers_count=repo_data.get('subscribers_count', 0),
                network_count=repo_data.get('network_count', 0),
                language=repo_data.get('language'),
                languages=languages,
                topics=repo_data.get('topics', []),
                license_name=repo_data.get('license', {}).get('name') if repo_data.get('license') else None,
                default_branch=repo_data['default_branch'],
                has_issues=repo_data['has_issues'],
                has_projects=repo_data['has_projects'],
                has_wiki=repo_data['has_wiki'],
                has_pages=repo_data['has_pages'],
                has_downloads=repo_data['has_downloads'],
                archived=repo_data['archived'],
                disabled=repo_data['disabled'],
                private=repo_data['private'],
                fork=repo_data['fork']
            )
            
        except Exception as e:
            raise RepositoryError(f"Failed to get repository stats: {e}",
                                repository=f"{owner}/{repo}", operation="get_stats")
    
    def get_repository_insights(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get comprehensive repository insights using the analyzer."""
        return self.analyzer.analyze_repository(owner, repo)
    
    def download_repository(self, owner: str, repo: str,
                          ref: str = "main",
                          format: str = "zipball",
                          output_path: Optional[str] = None) -> str:
        """Download repository archive."""
        validate_repository_name(repo)
        
        if format not in ['zipball', 'tarball']:
            raise ValidationError("Format must be 'zipball' or 'tarball'", field="format")
        
        try:
            self.logger.info(f"Downloading repository: {owner}/{repo}")
            
            # Make request for archive
            response = self.core.get(f'/repos/{owner}/{repo}/{format}/{ref}', stream=True)
            
            # Determine output path
            if not output_path:
                extension = 'zip' if format == 'zipball' else 'tar.gz'
                output_path = f"{repo}-{ref}.{extension}"
            
            # Write to file
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.info(f"Repository downloaded to: {output_path}")
            return output_path
            
        except Exception as e:
            raise RepositoryError(f"Failed to download repository: {e}",
                                repository=f"{owner}/{repo}", operation="download")
    
    def clone_repository(self, owner: str, repo: str,
                        clone_path: Optional[str] = None,
                        branch: Optional[str] = None) -> str:
        """Clone repository using Git."""
        validate_repository_name(repo)
        
        if not clone_path:
            clone_path = f"./{repo}"
        
        # Get repository data to get clone URL
        repo_data = self.get_repository(owner, repo)
        clone_url = repo_data['clone_url']
        
        try:
            self.logger.info(f"Cloning repository: {clone_url}")
            
            # Clone repository
            if branch:
                git_repo = Repo.clone_from(clone_url, clone_path, branch=branch)
            else:
                git_repo = Repo.clone_from(clone_url, clone_path)
            
            self.logger.info(f"Repository cloned to: {clone_path}")
            return clone_path
            
        except Exception as e:
            raise GitOperationError(f"Failed to clone repository: {e}",
                                  repository_path=clone_path,
                                  git_command="clone")


class RepoStats:
    """Repository statistics and analytics utilities."""
    
    def __init__(self, core):
        self.core = core
        self.logger = Logger("RepoStats")
    
    def compare_repositories(self, repositories: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Compare multiple repositories."""
        if len(repositories) < 2:
            raise ValidationError("At least 2 repositories required for comparison")
        
        comparison_data = {}
        
        # Get data for each repository
        for owner, repo in repositories:
            try:
                analyzer = RepositoryAnalyzer(self.core)
                analysis = analyzer.analyze_repository(owner, repo)
                comparison_data[f"{owner}/{repo}"] = analysis
            except Exception as e:
                self.logger.error(f"Failed to analyze {owner}/{repo}: {e}")
                comparison_data[f"{owner}/{repo}"] = {'error': str(e)}
        
        # Generate comparison insights
        comparison_insights = self._generate_comparison_insights(comparison_data)
        
        return {
            'repositories': comparison_data,
            'comparison': comparison_insights,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_comparison_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from repository comparison."""
        valid_repos = {k: v for k, v in data.items() if 'error' not in v}
        
        if len(valid_repos) < 2:
            return {'error': 'Not enough valid repositories for comparison'}
        
        metrics_comparison = {}
        
        # Compare key metrics
        for repo_name, repo_data in valid_repos.items():
            metrics = repo_data.get('metrics', {})
            for metric_name, value in metrics.items():
                if isinstance(value, (int, float)):
                    if metric_name not in metrics_comparison:
                        metrics_comparison[metric_name] = {}
                    metrics_comparison[metric_name][repo_name] = value
        
        # Find leaders in each category
        leaders = {}
        for metric, values in metrics_comparison.items():
            if values:
                leader = max(values.items(), key=lambda x: x[1])
                leaders[metric] = {
                    'repository': leader[0],
                    'value': leader[1]
                }
        
        return {
            'metrics_comparison': metrics_comparison,
            'category_leaders': leaders,
            'repository_count': len(valid_repos)
        }


__all__ = [
    'RepositoryManager',
    'RepositoryAnalyzer',
    'RepoStats',
    'RepositoryStats'
]