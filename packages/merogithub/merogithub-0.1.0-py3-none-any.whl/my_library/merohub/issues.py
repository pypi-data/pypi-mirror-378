"""
MeroHub Issues and Pull Requests Management Module
Author: MERO (Telegram: @QP4RM)

Comprehensive issue and pull request management with advanced analytics,
automation, and project management capabilities for GitHub repositories.
"""

import json
import time
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from .exceptions import IssueError, PullRequestError, ValidationError, APIError
from .utils import Logger, DataProcessor, retry_on_exception, timed_cache


@dataclass
class IssueTemplate:
    """Issue template container."""
    
    title: str
    body: str
    labels: List[str] = field(default_factory=list)
    assignees: List[str] = field(default_factory=list)
    milestone: Optional[str] = None
    template_type: str = "bug_report"


@dataclass
class PullRequestTemplate:
    """Pull request template container."""
    
    title: str
    body: str
    base: str = "main"
    head: str = ""
    draft: bool = False
    maintainer_can_modify: bool = True


class IssueManager:
    """Comprehensive issue management with advanced features."""
    
    def __init__(self, core):
        self.core = core
        self.logger = Logger("IssueManager")
        self.data_processor = DataProcessor()
        self._templates = {}
        
        # Issue statistics tracking
        self.issue_stats = {
            'total_created': 0,
            'total_closed': 0,
            'average_resolution_time': 0.0,
            'most_used_labels': Counter(),
            'assignee_performance': defaultdict(list)
        }
    
    def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """Get specific issue details."""
        try:
            return self.core.get_json(f'/repos/{owner}/{repo}/issues/{issue_number}')
        except Exception as e:
            raise IssueError(f"Failed to get issue: {e}",
                           issue_number=issue_number,
                           repository=f"{owner}/{repo}",
                           operation="get")
    
    def list_issues(self, owner: str, repo: str,
                   state: str = "open",
                   labels: Optional[List[str]] = None,
                   assignee: Optional[str] = None,
                   creator: Optional[str] = None,
                   mentioned: Optional[str] = None,
                   milestone: Optional[str] = None,
                   sort: str = "created",
                   direction: str = "desc",
                   since: Optional[str] = None,
                   per_page: int = 30) -> List[Dict[str, Any]]:
        """List repository issues with advanced filtering."""
        
        params = {
            'state': state,
            'sort': sort,
            'direction': direction,
            'per_page': per_page
        }
        
        if labels:
            params['labels'] = ','.join(labels)
        if assignee:
            params['assignee'] = assignee
        if creator:
            params['creator'] = creator
        if mentioned:
            params['mentioned'] = mentioned
        if milestone:
            params['milestone'] = milestone
        if since:
            params['since'] = since
        
        try:
            return self.core.paginate(f'/repos/{owner}/{repo}/issues', params=params)
        except Exception as e:
            raise IssueError(f"Failed to list issues: {e}",
                           repository=f"{owner}/{repo}",
                           operation="list")
    
    def create_issue(self, owner: str, repo: str,
                    title: str,
                    body: str = "",
                    labels: Optional[List[str]] = None,
                    assignees: Optional[List[str]] = None,
                    milestone: Optional[int] = None) -> Dict[str, Any]:
        """Create a new issue."""
        
        if not title or len(title.strip()) == 0:
            raise ValidationError("Issue title cannot be empty", field="title")
        
        payload = {
            'title': title.strip(),
            'body': body
        }
        
        if labels:
            payload['labels'] = labels
        if assignees:
            payload['assignees'] = assignees
        if milestone:
            payload['milestone'] = milestone
        
        try:
            self.logger.info(f"Creating issue: {title}")
            result = self.core.post_json(f'/repos/{owner}/{repo}/issues', json_data=payload)
            
            # Update statistics
            self.issue_stats['total_created'] += 1
            if labels:
                self.issue_stats['most_used_labels'].update(labels)
            
            return result
            
        except Exception as e:
            raise IssueError(f"Failed to create issue: {e}",
                           repository=f"{owner}/{repo}",
                           operation="create")
    
    def update_issue(self, owner: str, repo: str, issue_number: int,
                    **kwargs) -> Dict[str, Any]:
        """Update an existing issue."""
        
        try:
            self.logger.info(f"Updating issue #{issue_number}")
            return self.core.post_json(f'/repos/{owner}/{repo}/issues/{issue_number}',
                                     json_data=kwargs)
        except Exception as e:
            raise IssueError(f"Failed to update issue: {e}",
                           issue_number=issue_number,
                           repository=f"{owner}/{repo}",
                           operation="update")
    
    def close_issue(self, owner: str, repo: str, issue_number: int,
                   reason: Optional[str] = None) -> Dict[str, Any]:
        """Close an issue."""
        
        payload = {'state': 'closed'}
        if reason:
            payload['state_reason'] = reason
        
        try:
            self.logger.info(f"Closing issue #{issue_number}")
            result = self.update_issue(owner, repo, issue_number, **payload)
            
            # Update statistics
            self.issue_stats['total_closed'] += 1
            
            return result
            
        except Exception as e:
            raise IssueError(f"Failed to close issue: {e}",
                           issue_number=issue_number,
                           repository=f"{owner}/{repo}",
                           operation="close")
    
    def reopen_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """Reopen a closed issue."""
        
        try:
            self.logger.info(f"Reopening issue #{issue_number}")
            return self.update_issue(owner, repo, issue_number, state='open')
        except Exception as e:
            raise IssueError(f"Failed to reopen issue: {e}",
                           issue_number=issue_number,
                           repository=f"{owner}/{repo}",
                           operation="reopen")
    
    def add_labels(self, owner: str, repo: str, issue_number: int,
                  labels: List[str]) -> List[Dict[str, Any]]:
        """Add labels to an issue."""
        
        try:
            self.logger.info(f"Adding labels to issue #{issue_number}: {labels}")
            response = self.core.post_json(
                f'/repos/{owner}/{repo}/issues/{issue_number}/labels',
                json_data={'labels': labels}
            )
            
            # Update statistics
            self.issue_stats['most_used_labels'].update(labels)
            
            return response
            
        except Exception as e:
            raise IssueError(f"Failed to add labels: {e}",
                           issue_number=issue_number,
                           repository=f"{owner}/{repo}",
                           operation="add_labels")
    
    def remove_label(self, owner: str, repo: str, issue_number: int,
                    label: str) -> bool:
        """Remove a label from an issue."""
        
        try:
            self.logger.info(f"Removing label from issue #{issue_number}: {label}")
            response = self.core.delete(
                f'/repos/{owner}/{repo}/issues/{issue_number}/labels/{label}'
            )
            return response.status_code == 200
            
        except Exception as e:
            raise IssueError(f"Failed to remove label: {e}",
                           issue_number=issue_number,
                           repository=f"{owner}/{repo}",
                           operation="remove_label")
    
    def assign_issue(self, owner: str, repo: str, issue_number: int,
                    assignees: List[str]) -> Dict[str, Any]:
        """Assign users to an issue."""
        
        try:
            self.logger.info(f"Assigning issue #{issue_number} to: {assignees}")
            return self.core.post_json(
                f'/repos/{owner}/{repo}/issues/{issue_number}/assignees',
                json_data={'assignees': assignees}
            )
        except Exception as e:
            raise IssueError(f"Failed to assign issue: {e}",
                           issue_number=issue_number,
                           repository=f"{owner}/{repo}",
                           operation="assign")
    
    def unassign_issue(self, owner: str, repo: str, issue_number: int,
                      assignees: List[str]) -> Dict[str, Any]:
        """Unassign users from an issue."""
        
        try:
            self.logger.info(f"Unassigning issue #{issue_number} from: {assignees}")
            return self.core.delete(
                f'/repos/{owner}/{repo}/issues/{issue_number}/assignees',
                json_data={'assignees': assignees}
            )
        except Exception as e:
            raise IssueError(f"Failed to unassign issue: {e}",
                           issue_number=issue_number,
                           repository=f"{owner}/{repo}",
                           operation="unassign")
    
    def create_issue_comment(self, owner: str, repo: str, issue_number: int,
                           body: str) -> Dict[str, Any]:
        """Add a comment to an issue."""
        
        if not body or len(body.strip()) == 0:
            raise ValidationError("Comment body cannot be empty", field="body")
        
        payload = {'body': body.strip()}
        
        try:
            self.logger.info(f"Adding comment to issue #{issue_number}")
            return self.core.post_json(
                f'/repos/{owner}/{repo}/issues/{issue_number}/comments',
                json_data=payload
            )
        except Exception as e:
            raise IssueError(f"Failed to create comment: {e}",
                           issue_number=issue_number,
                           repository=f"{owner}/{repo}",
                           operation="create_comment")
    
    def get_issue_comments(self, owner: str, repo: str, issue_number: int,
                          sort: str = "created",
                          direction: str = "asc") -> List[Dict[str, Any]]:
        """Get comments for an issue."""
        
        params = {
            'sort': sort,
            'direction': direction
        }
        
        try:
            return self.core.paginate(
                f'/repos/{owner}/{repo}/issues/{issue_number}/comments',
                params=params
            )
        except Exception as e:
            raise IssueError(f"Failed to get comments: {e}",
                           issue_number=issue_number,
                           repository=f"{owner}/{repo}",
                           operation="get_comments")
    
    def get_issue_events(self, owner: str, repo: str, issue_number: int) -> List[Dict[str, Any]]:
        """Get events for an issue."""
        
        try:
            return self.core.paginate(f'/repos/{owner}/{repo}/issues/{issue_number}/events')
        except Exception as e:
            raise IssueError(f"Failed to get issue events: {e}",
                           issue_number=issue_number,
                           repository=f"{owner}/{repo}",
                           operation="get_events")
    
    def get_issue_timeline(self, owner: str, repo: str, issue_number: int) -> List[Dict[str, Any]]:
        """Get timeline events for an issue."""
        
        try:
            headers = {'Accept': 'application/vnd.github.mockingbird-preview+json'}
            return self.core.paginate(
                f'/repos/{owner}/{repo}/issues/{issue_number}/timeline',
                headers=headers
            )
        except Exception as e:
            raise IssueError(f"Failed to get issue timeline: {e}",
                           issue_number=issue_number,
                           repository=f"{owner}/{repo}",
                           operation="get_timeline")
    
    def lock_issue(self, owner: str, repo: str, issue_number: int,
                  lock_reason: Optional[str] = None) -> bool:
        """Lock an issue conversation."""
        
        payload = {}
        if lock_reason:
            payload['lock_reason'] = lock_reason
        
        try:
            self.logger.info(f"Locking issue #{issue_number}")
            response = self.core.put(
                f'/repos/{owner}/{repo}/issues/{issue_number}/lock',
                json_data=payload if payload else None
            )
            return response.status_code == 204
            
        except Exception as e:
            raise IssueError(f"Failed to lock issue: {e}",
                           issue_number=issue_number,
                           repository=f"{owner}/{repo}",
                           operation="lock")
    
    def unlock_issue(self, owner: str, repo: str, issue_number: int) -> bool:
        """Unlock an issue conversation."""
        
        try:
            self.logger.info(f"Unlocking issue #{issue_number}")
            response = self.core.delete(f'/repos/{owner}/{repo}/issues/{issue_number}/lock')
            return response.status_code == 204
            
        except Exception as e:
            raise IssueError(f"Failed to unlock issue: {e}",
                           issue_number=issue_number,
                           repository=f"{owner}/{repo}",
                           operation="unlock")
    
    def analyze_issues(self, owner: str, repo: str,
                      timeframe_days: int = 90) -> Dict[str, Any]:
        """Comprehensive issue analysis for a repository."""
        
        self.logger.info(f"Analyzing issues for {owner}/{repo}")
        
        try:
            # Get issues data
            since_date = (datetime.now() - timedelta(days=timeframe_days)).isoformat()
            
            open_issues = self.list_issues(owner, repo, state="open", per_page=100)
            closed_issues = self.list_issues(owner, repo, state="closed", 
                                           since=since_date, per_page=100)
            
            all_issues = open_issues + closed_issues
            
            # Perform analysis
            analysis = {
                'summary': self._analyze_issue_summary(all_issues),
                'labels': self._analyze_issue_labels(all_issues),
                'assignees': self._analyze_issue_assignees(all_issues),
                'response_times': self._analyze_response_times(owner, repo, all_issues[:50]),
                'trends': self._analyze_issue_trends(all_issues, timeframe_days),
                'resolution_patterns': self._analyze_resolution_patterns(closed_issues),
                'recommendations': self._generate_issue_recommendations(all_issues)
            }
            
            analysis['metadata'] = {
                'repository': f"{owner}/{repo}",
                'timeframe_days': timeframe_days,
                'analysis_date': datetime.now().isoformat(),
                'total_issues_analyzed': len(all_issues)
            }
            
            return analysis
            
        except Exception as e:
            raise IssueError(f"Failed to analyze issues: {e}",
                           repository=f"{owner}/{repo}",
                           operation="analyze")
    
    def _analyze_issue_summary(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze issue summary statistics."""
        
        open_count = len([i for i in issues if i['state'] == 'open'])
        closed_count = len([i for i in issues if i['state'] == 'closed'])
        
        # Calculate resolution times for closed issues
        resolution_times = []
        for issue in issues:
            if issue['state'] == 'closed' and issue.get('closed_at') and issue.get('created_at'):
                created = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
                closed = datetime.fromisoformat(issue['closed_at'].replace('Z', '+00:00'))
                resolution_time = (closed - created).total_seconds() / 3600  # hours
                resolution_times.append(resolution_time)
        
        # Comment statistics
        comment_counts = [issue.get('comments', 0) for issue in issues]
        
        return {
            'total_issues': len(issues),
            'open_issues': open_count,
            'closed_issues': closed_count,
            'resolution_rate': (closed_count / len(issues)) * 100 if issues else 0,
            'average_resolution_time_hours': statistics.mean(resolution_times) if resolution_times else 0,
            'median_resolution_time_hours': statistics.median(resolution_times) if resolution_times else 0,
            'average_comments_per_issue': statistics.mean(comment_counts) if comment_counts else 0,
            'issues_without_comments': len([c for c in comment_counts if c == 0]),
            'highly_discussed_issues': len([c for c in comment_counts if c >= 10])
        }
    
    def _analyze_issue_labels(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze issue label usage."""
        
        label_counter = Counter()
        label_combinations = Counter()
        issues_without_labels = 0
        
        for issue in issues:
            labels = issue.get('labels', [])
            if not labels:
                issues_without_labels += 1
            else:
                label_names = [label['name'] for label in labels]
                label_counter.update(label_names)
                
                # Track label combinations for issues with multiple labels
                if len(label_names) > 1:
                    combination = tuple(sorted(label_names))
                    label_combinations[combination] += 1
        
        return {
            'most_common_labels': dict(label_counter.most_common(15)),
            'common_label_combinations': [
                {'labels': list(combo), 'count': count}
                for combo, count in label_combinations.most_common(10)
            ],
            'issues_without_labels': issues_without_labels,
            'unique_labels': len(label_counter),
            'average_labels_per_issue': sum(label_counter.values()) / len(issues) if issues else 0
        }
    
    def _analyze_issue_assignees(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze issue assignee patterns."""
        
        assignee_counter = Counter()
        issues_without_assignees = 0
        multiple_assignee_issues = 0
        
        for issue in issues:
            assignees = issue.get('assignees', [])
            if not assignees:
                issues_without_assignees += 1
            else:
                if len(assignees) > 1:
                    multiple_assignee_issues += 1
                
                for assignee in assignees:
                    assignee_counter[assignee['login']] += 1
        
        return {
            'most_active_assignees': dict(assignee_counter.most_common(10)),
            'issues_without_assignees': issues_without_assignees,
            'issues_with_multiple_assignees': multiple_assignee_issues,
            'unique_assignees': len(assignee_counter),
            'assignment_rate': ((len(issues) - issues_without_assignees) / len(issues)) * 100 if issues else 0
        }
    
    def _analyze_response_times(self, owner: str, repo: str, 
                              issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze issue response times."""
        
        first_response_times = []
        
        # Get first comment for each issue to calculate response time
        for issue in issues[:20]:  # Limit to avoid too many API calls
            try:
                comments = self.get_issue_comments(owner, repo, issue['number'])
                if comments:
                    # First comment response time
                    created = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
                    first_comment = datetime.fromisoformat(comments[0]['created_at'].replace('Z', '+00:00'))
                    response_time = (first_comment - created).total_seconds() / 3600  # hours
                    first_response_times.append(response_time)
            except:
                continue  # Skip if we can't get comments
        
        return {
            'average_first_response_time_hours': statistics.mean(first_response_times) if first_response_times else None,
            'median_first_response_time_hours': statistics.median(first_response_times) if first_response_times else None,
            'fastest_response_hours': min(first_response_times) if first_response_times else None,
            'slowest_response_hours': max(first_response_times) if first_response_times else None,
            'issues_with_no_response': len(issues) - len([i for i in issues if i.get('comments', 0) > 0])
        }
    
    def _analyze_issue_trends(self, issues: List[Dict[str, Any]], 
                            timeframe_days: int) -> Dict[str, Any]:
        """Analyze issue creation and closure trends."""
        
        daily_created = defaultdict(int)
        daily_closed = defaultdict(int)
        
        for issue in issues:
            # Creation trend
            if issue.get('created_at'):
                created_date = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
                date_key = created_date.strftime('%Y-%m-%d')
                daily_created[date_key] += 1
            
            # Closure trend
            if issue.get('closed_at'):
                closed_date = datetime.fromisoformat(issue['closed_at'].replace('Z', '+00:00'))
                date_key = closed_date.strftime('%Y-%m-%d')
                daily_closed[date_key] += 1
        
        # Calculate trends
        created_values = list(daily_created.values())
        closed_values = list(daily_closed.values())
        
        return {
            'daily_creation_trend': dict(daily_created),
            'daily_closure_trend': dict(daily_closed),
            'average_daily_creation': statistics.mean(created_values) if created_values else 0,
            'average_daily_closure': statistics.mean(closed_values) if closed_values else 0,
            'peak_creation_day': max(daily_created.items(), key=lambda x: x[1]) if daily_created else None,
            'peak_closure_day': max(daily_closed.items(), key=lambda x: x[1]) if daily_closed else None
        }
    
    def _analyze_resolution_patterns(self, closed_issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how issues get resolved."""
        
        resolution_methods = Counter()
        closing_users = Counter()
        
        for issue in closed_issues:
            # Who closed the issue
            if issue.get('closed_by'):
                closing_users[issue['closed_by']['login']] += 1
            
            # Try to determine resolution method from events (simplified)
            if issue.get('state_reason'):
                resolution_methods[issue['state_reason']] += 1
            else:
                resolution_methods['completed'] += 1
        
        return {
            'resolution_methods': dict(resolution_methods),
            'top_closers': dict(closing_users.most_common(10)),
            'self_closed_rate': 0  # Would need to compare with issue creator
        }
    
    def _generate_issue_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for issue management."""
        
        recommendations = []
        
        if not issues:
            return ["📝 Start tracking issues to improve project management"]
        
        # Calculate key metrics
        open_count = len([i for i in issues if i['state'] == 'open'])
        total_count = len(issues)
        no_label_count = len([i for i in issues if not i.get('labels')])
        no_assignee_count = len([i for i in issues if not i.get('assignees')])
        
        # High open issue ratio
        if total_count > 0 and (open_count / total_count) > 0.7:
            recommendations.append("⚠️ High number of open issues - consider triaging and closing stale issues")
        
        # Many issues without labels
        if total_count > 0 and (no_label_count / total_count) > 0.5:
            recommendations.append("🏷️ Add labels to issues for better organization and filtering")
        
        # Many issues without assignees
        if total_count > 0 and (no_assignee_count / total_count) > 0.6:
            recommendations.append("👥 Assign issues to team members for better accountability")
        
        # No comments on many issues
        no_comment_count = len([i for i in issues if i.get('comments', 0) == 0])
        if total_count > 0 and (no_comment_count / total_count) > 0.4:
            recommendations.append("💬 Improve issue engagement by responding to user reports")
        
        return recommendations
    
    def create_issue_template(self, template_name: str, template: IssueTemplate):
        """Create an issue template."""
        self._templates[template_name] = template
        self.logger.info(f"Created issue template: {template_name}")
    
    def create_issue_from_template(self, owner: str, repo: str,
                                 template_name: str,
                                 **kwargs) -> Dict[str, Any]:
        """Create an issue from a template."""
        
        if template_name not in self._templates:
            raise ValidationError(f"Template '{template_name}' not found")
        
        template = self._templates[template_name]
        
        # Merge template with provided kwargs
        issue_data = {
            'title': kwargs.get('title', template.title),
            'body': kwargs.get('body', template.body),
            'labels': kwargs.get('labels', template.labels),
            'assignees': kwargs.get('assignees', template.assignees)
        }
        
        if template.milestone:
            issue_data['milestone'] = kwargs.get('milestone', template.milestone)
        
        return self.create_issue(owner, repo, **issue_data)
    
    def get_issue_statistics(self) -> Dict[str, Any]:
        """Get issue management statistics."""
        return self.issue_stats.copy()


class PullRequestManager:
    """Comprehensive pull request management."""
    
    def __init__(self, core):
        self.core = core
        self.logger = Logger("PullRequestManager")
        self.data_processor = DataProcessor()
        
        # PR statistics tracking
        self.pr_stats = {
            'total_created': 0,
            'total_merged': 0,
            'total_closed': 0,
            'average_merge_time': 0.0,
            'review_patterns': Counter()
        }
    
    def get_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get specific pull request details."""
        try:
            return self.core.get_json(f'/repos/{owner}/{repo}/pulls/{pr_number}')
        except Exception as e:
            raise PullRequestError(f"Failed to get pull request: {e}",
                                 pr_number=pr_number,
                                 repository=f"{owner}/{repo}",
                                 operation="get")
    
    def list_pull_requests(self, owner: str, repo: str,
                          state: str = "open",
                          head: Optional[str] = None,
                          base: Optional[str] = None,
                          sort: str = "created",
                          direction: str = "desc") -> List[Dict[str, Any]]:
        """List repository pull requests."""
        
        params = {
            'state': state,
            'sort': sort,
            'direction': direction
        }
        
        if head:
            params['head'] = head
        if base:
            params['base'] = base
        
        try:
            return self.core.paginate(f'/repos/{owner}/{repo}/pulls', params=params)
        except Exception as e:
            raise PullRequestError(f"Failed to list pull requests: {e}",
                                 repository=f"{owner}/{repo}",
                                 operation="list")
    
    def create_pull_request(self, owner: str, repo: str,
                           title: str,
                           head: str,
                           base: str = "main",
                           body: str = "",
                           draft: bool = False,
                           maintainer_can_modify: bool = True) -> Dict[str, Any]:
        """Create a new pull request."""
        
        if not title or len(title.strip()) == 0:
            raise ValidationError("Pull request title cannot be empty", field="title")
        
        if not head:
            raise ValidationError("Head branch is required", field="head")
        
        payload = {
            'title': title.strip(),
            'head': head,
            'base': base,
            'body': body,
            'draft': draft,
            'maintainer_can_modify': maintainer_can_modify
        }
        
        try:
            self.logger.info(f"Creating pull request: {title}")
            result = self.core.post_json(f'/repos/{owner}/{repo}/pulls', json_data=payload)
            
            # Update statistics
            self.pr_stats['total_created'] += 1
            
            return result
            
        except Exception as e:
            raise PullRequestError(f"Failed to create pull request: {e}",
                                 repository=f"{owner}/{repo}",
                                 operation="create")
    
    def update_pull_request(self, owner: str, repo: str, pr_number: int,
                           **kwargs) -> Dict[str, Any]:
        """Update an existing pull request."""
        
        try:
            self.logger.info(f"Updating pull request #{pr_number}")
            return self.core.post_json(f'/repos/{owner}/{repo}/pulls/{pr_number}',
                                     json_data=kwargs)
        except Exception as e:
            raise PullRequestError(f"Failed to update pull request: {e}",
                                 pr_number=pr_number,
                                 repository=f"{owner}/{repo}",
                                 operation="update")
    
    def merge_pull_request(self, owner: str, repo: str, pr_number: int,
                          commit_title: Optional[str] = None,
                          commit_message: Optional[str] = None,
                          merge_method: str = "merge") -> Dict[str, Any]:
        """Merge a pull request."""
        
        if merge_method not in ['merge', 'squash', 'rebase']:
            raise ValidationError("Invalid merge method", field="merge_method")
        
        payload = {'merge_method': merge_method}
        
        if commit_title:
            payload['commit_title'] = commit_title
        if commit_message:
            payload['commit_message'] = commit_message
        
        try:
            self.logger.info(f"Merging pull request #{pr_number}")
            result = self.core.put(f'/repos/{owner}/{repo}/pulls/{pr_number}/merge',
                                 json_data=payload)
            
            # Update statistics
            self.pr_stats['total_merged'] += 1
            
            return result.json()
            
        except Exception as e:
            raise PullRequestError(f"Failed to merge pull request: {e}",
                                 pr_number=pr_number,
                                 repository=f"{owner}/{repo}",
                                 operation="merge")
    
    def close_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Close a pull request without merging."""
        
        try:
            self.logger.info(f"Closing pull request #{pr_number}")
            result = self.update_pull_request(owner, repo, pr_number, state='closed')
            
            # Update statistics
            self.pr_stats['total_closed'] += 1
            
            return result
            
        except Exception as e:
            raise PullRequestError(f"Failed to close pull request: {e}",
                                 pr_number=pr_number,
                                 repository=f"{owner}/{repo}",
                                 operation="close")
    
    def get_pull_request_files(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Get files changed in a pull request."""
        
        try:
            return self.core.paginate(f'/repos/{owner}/{repo}/pulls/{pr_number}/files')
        except Exception as e:
            raise PullRequestError(f"Failed to get PR files: {e}",
                                 pr_number=pr_number,
                                 repository=f"{owner}/{repo}",
                                 operation="get_files")
    
    def get_pull_request_reviews(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Get reviews for a pull request."""
        
        try:
            return self.core.paginate(f'/repos/{owner}/{repo}/pulls/{pr_number}/reviews')
        except Exception as e:
            raise PullRequestError(f"Failed to get PR reviews: {e}",
                                 pr_number=pr_number,
                                 repository=f"{owner}/{repo}",
                                 operation="get_reviews")
    
    def create_pull_request_review(self, owner: str, repo: str, pr_number: int,
                                  body: Optional[str] = None,
                                  event: str = "COMMENT",
                                  comments: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Create a review for a pull request."""
        
        if event not in ['APPROVE', 'REQUEST_CHANGES', 'COMMENT']:
            raise ValidationError("Invalid review event", field="event")
        
        payload = {'event': event}
        
        if body:
            payload['body'] = body
        if comments:
            payload['comments'] = comments
        
        try:
            self.logger.info(f"Creating review for PR #{pr_number}")
            result = self.core.post_json(
                f'/repos/{owner}/{repo}/pulls/{pr_number}/reviews',
                json_data=payload
            )
            
            # Update statistics
            self.pr_stats['review_patterns'][event] += 1
            
            return result
            
        except Exception as e:
            raise PullRequestError(f"Failed to create review: {e}",
                                 pr_number=pr_number,
                                 repository=f"{owner}/{repo}",
                                 operation="create_review")
    
    def request_pull_request_reviewers(self, owner: str, repo: str, pr_number: int,
                                     reviewers: Optional[List[str]] = None,
                                     team_reviewers: Optional[List[str]] = None) -> Dict[str, Any]:
        """Request reviewers for a pull request."""
        
        payload = {}
        if reviewers:
            payload['reviewers'] = reviewers
        if team_reviewers:
            payload['team_reviewers'] = team_reviewers
        
        if not payload:
            raise ValidationError("Must specify reviewers or team_reviewers")
        
        try:
            self.logger.info(f"Requesting reviewers for PR #{pr_number}")
            return self.core.post_json(
                f'/repos/{owner}/{repo}/pulls/{pr_number}/requested_reviewers',
                json_data=payload
            )
        except Exception as e:
            raise PullRequestError(f"Failed to request reviewers: {e}",
                                 pr_number=pr_number,
                                 repository=f"{owner}/{repo}",
                                 operation="request_reviewers")
    
    def analyze_pull_requests(self, owner: str, repo: str,
                            timeframe_days: int = 90) -> Dict[str, Any]:
        """Comprehensive pull request analysis."""
        
        self.logger.info(f"Analyzing pull requests for {owner}/{repo}")
        
        try:
            # Get PR data
            open_prs = self.list_pull_requests(owner, repo, state="open")
            closed_prs = self.list_pull_requests(owner, repo, state="closed")
            
            all_prs = open_prs + closed_prs
            
            # Limit to timeframe
            cutoff_date = datetime.now() - timedelta(days=timeframe_days)
            recent_prs = []
            
            for pr in all_prs:
                if pr.get('created_at'):
                    created_date = datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00'))
                    if created_date >= cutoff_date:
                        recent_prs.append(pr)
            
            # Perform analysis
            analysis = {
                'summary': self._analyze_pr_summary(recent_prs),
                'merge_patterns': self._analyze_merge_patterns(recent_prs),
                'review_analysis': self._analyze_pr_reviews(owner, repo, recent_prs[:20]),
                'file_changes': self._analyze_pr_file_changes(owner, repo, recent_prs[:20]),
                'trends': self._analyze_pr_trends(recent_prs, timeframe_days),
                'recommendations': self._generate_pr_recommendations(recent_prs)
            }
            
            analysis['metadata'] = {
                'repository': f"{owner}/{repo}",
                'timeframe_days': timeframe_days,
                'analysis_date': datetime.now().isoformat(),
                'total_prs_analyzed': len(recent_prs)
            }
            
            return analysis
            
        except Exception as e:
            raise PullRequestError(f"Failed to analyze pull requests: {e}",
                                 repository=f"{owner}/{repo}",
                                 operation="analyze")
    
    def _analyze_pr_summary(self, prs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze PR summary statistics."""
        
        open_count = len([pr for pr in prs if pr['state'] == 'open'])
        closed_count = len([pr for pr in prs if pr['state'] == 'closed'])
        merged_count = len([pr for pr in prs if pr.get('merged')])
        draft_count = len([pr for pr in prs if pr.get('draft')])
        
        # Calculate merge times
        merge_times = []
        for pr in prs:
            if pr.get('merged_at') and pr.get('created_at'):
                created = datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00'))
                merged = datetime.fromisoformat(pr['merged_at'].replace('Z', '+00:00'))
                merge_time = (merged - created).total_seconds() / 3600  # hours
                merge_times.append(merge_time)
        
        return {
            'total_prs': len(prs),
            'open_prs': open_count,
            'closed_prs': closed_count,
            'merged_prs': merged_count,
            'draft_prs': draft_count,
            'merge_rate': (merged_count / len(prs)) * 100 if prs else 0,
            'average_merge_time_hours': statistics.mean(merge_times) if merge_times else 0,
            'median_merge_time_hours': statistics.median(merge_times) if merge_times else 0,
            'fastest_merge_hours': min(merge_times) if merge_times else 0,
            'slowest_merge_hours': max(merge_times) if merge_times else 0
        }
    
    def _analyze_merge_patterns(self, prs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze PR merge patterns."""
        
        authors = Counter()
        target_branches = Counter()
        source_branches = Counter()
        
        for pr in prs:
            if pr.get('user'):
                authors[pr['user']['login']] += 1
            
            if pr.get('base'):
                target_branches[pr['base']['ref']] += 1
            
            if pr.get('head'):
                source_branches[pr['head']['ref']] += 1
        
        return {
            'most_active_contributors': dict(authors.most_common(10)),
            'target_branch_distribution': dict(target_branches.most_common(10)),
            'source_branch_patterns': dict(source_branches.most_common(10)),
            'unique_contributors': len(authors)
        }
    
    def _analyze_pr_reviews(self, owner: str, repo: str, 
                          prs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze PR review patterns."""
        
        review_stats = {
            'total_reviews': 0,
            'average_reviews_per_pr': 0,
            'review_types': Counter(),
            'top_reviewers': Counter(),
            'prs_without_reviews': 0
        }
        
        total_review_count = 0
        
        for pr in prs[:10]:  # Limit to avoid too many API calls
            try:
                reviews = self.get_pull_request_reviews(owner, repo, pr['number'])
                
                if not reviews:
                    review_stats['prs_without_reviews'] += 1
                else:
                    total_review_count += len(reviews)
                    
                    for review in reviews:
                        review_stats['review_types'][review.get('state', 'UNKNOWN')] += 1
                        if review.get('user'):
                            review_stats['top_reviewers'][review['user']['login']] += 1
                        
            except:
                continue  # Skip if we can't get reviews
        
        review_stats['total_reviews'] = total_review_count
        review_stats['average_reviews_per_pr'] = total_review_count / len(prs) if prs else 0
        review_stats['top_reviewers'] = dict(review_stats['top_reviewers'].most_common(10))
        review_stats['review_types'] = dict(review_stats['review_types'])
        
        return review_stats
    
    def _analyze_pr_file_changes(self, owner: str, repo: str,
                               prs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze file changes in PRs."""
        
        file_stats = {
            'average_files_per_pr': 0,
            'average_additions_per_pr': 0,
            'average_deletions_per_pr': 0,
            'most_changed_files': Counter(),
            'file_type_distribution': Counter()
        }
        
        total_files = 0
        total_additions = 0
        total_deletions = 0
        
        for pr in prs[:10]:  # Limit to avoid too many API calls
            try:
                files = self.get_pull_request_files(owner, repo, pr['number'])
                
                total_files += len(files)
                
                for file in files:
                    file_stats['most_changed_files'][file['filename']] += 1
                    
                    # File type
                    ext = file['filename'].split('.')[-1] if '.' in file['filename'] else 'no_extension'
                    file_stats['file_type_distribution'][ext] += 1
                    
                    # Additions/deletions
                    total_additions += file.get('additions', 0)
                    total_deletions += file.get('deletions', 0)
                        
            except:
                continue  # Skip if we can't get files
        
        file_stats['average_files_per_pr'] = total_files / len(prs) if prs else 0
        file_stats['average_additions_per_pr'] = total_additions / len(prs) if prs else 0
        file_stats['average_deletions_per_pr'] = total_deletions / len(prs) if prs else 0
        file_stats['most_changed_files'] = dict(file_stats['most_changed_files'].most_common(10))
        file_stats['file_type_distribution'] = dict(file_stats['file_type_distribution'].most_common(10))
        
        return file_stats
    
    def _analyze_pr_trends(self, prs: List[Dict[str, Any]], 
                         timeframe_days: int) -> Dict[str, Any]:
        """Analyze PR creation and merge trends."""
        
        daily_created = defaultdict(int)
        daily_merged = defaultdict(int)
        
        for pr in prs:
            # Creation trend
            if pr.get('created_at'):
                created_date = datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00'))
                date_key = created_date.strftime('%Y-%m-%d')
                daily_created[date_key] += 1
            
            # Merge trend
            if pr.get('merged_at'):
                merged_date = datetime.fromisoformat(pr['merged_at'].replace('Z', '+00:00'))
                date_key = merged_date.strftime('%Y-%m-%d')
                daily_merged[date_key] += 1
        
        return {
            'daily_creation_trend': dict(daily_created),
            'daily_merge_trend': dict(daily_merged),
            'average_daily_creation': statistics.mean(list(daily_created.values())) if daily_created else 0,
            'average_daily_merge': statistics.mean(list(daily_merged.values())) if daily_merged else 0
        }
    
    def _generate_pr_recommendations(self, prs: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for PR management."""
        
        recommendations = []
        
        if not prs:
            return ["📝 Start using pull requests for better code review and collaboration"]
        
        # Calculate key metrics
        merged_count = len([pr for pr in prs if pr.get('merged')])
        draft_count = len([pr for pr in prs if pr.get('draft')])
        total_count = len(prs)
        
        # Low merge rate
        if total_count > 5 and (merged_count / total_count) < 0.5:
            recommendations.append("⚠️ Low PR merge rate - review your approval process")
        
        # Too many draft PRs
        if total_count > 0 and (draft_count / total_count) > 0.3:
            recommendations.append("📋 Many draft PRs - consider setting clear completion criteria")
        
        # Size recommendations
        large_prs = len([pr for pr in prs if pr.get('additions', 0) + pr.get('deletions', 0) > 1000])
        if total_count > 0 and (large_prs / total_count) > 0.3:
            recommendations.append("📏 Many large PRs - consider breaking changes into smaller pieces")
        
        return recommendations
    
    def get_pr_statistics(self) -> Dict[str, Any]:
        """Get pull request management statistics."""
        return self.pr_stats.copy()


class ProjectManager:
    """Project management utilities for GitHub repositories."""
    
    def __init__(self, core):
        self.core = core
        self.issue_manager = IssueManager(core)
        self.pr_manager = PullRequestManager(core)
        self.logger = Logger("ProjectManager")
    
    def get_project_overview(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get comprehensive project overview."""
        
        try:
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    'issues': executor.submit(self.issue_manager.analyze_issues, owner, repo),
                    'pull_requests': executor.submit(self.pr_manager.analyze_pull_requests, owner, repo),
                    'repository': executor.submit(self.core.get_json, f'/repos/{owner}/{repo}')
                }
                
                results = {}
                for key, future in futures.items():
                    try:
                        results[key] = future.result(timeout=60)
                    except Exception as e:
                        self.logger.error(f"Failed to get {key} data: {e}")
                        results[key] = {'error': str(e)}
            
            # Generate overall insights
            overview = {
                'repository': results['repository'],
                'issues_analysis': results['issues'],
                'pull_requests_analysis': results['pull_requests'],
                'project_health': self._calculate_project_health(results),
                'recommendations': self._generate_project_recommendations(results),
                'generated_at': datetime.now().isoformat()
            }
            
            return overview
            
        except Exception as e:
            raise IssueError(f"Failed to get project overview: {e}",
                           repository=f"{owner}/{repo}",
                           operation="project_overview")
    
    def _calculate_project_health(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall project health score."""
        
        health = {
            'score': 0,
            'max_score': 100,
            'factors': {}
        }
        
        # Issue management health (40 points)
        issues = data.get('issues_analysis', {})
        if not issues.get('error'):
            issue_summary = issues.get('summary', {})
            resolution_rate = issue_summary.get('resolution_rate', 0)
            
            issue_score = min(resolution_rate * 0.4, 40)
            health['factors']['issue_management'] = issue_score
            health['score'] += issue_score
        
        # PR management health (40 points)
        prs = data.get('pull_requests_analysis', {})
        if not prs.get('error'):
            pr_summary = prs.get('summary', {})
            merge_rate = pr_summary.get('merge_rate', 0)
            
            pr_score = min(merge_rate * 0.4, 40)
            health['factors']['pr_management'] = pr_score
            health['score'] += pr_score
        
        # Repository health (20 points)
        repo = data.get('repository', {})
        if not repo.get('error'):
            repo_score = 0
            
            if repo.get('description'):
                repo_score += 5
            if repo.get('license'):
                repo_score += 5
            if repo.get('has_wiki'):
                repo_score += 3
            if repo.get('has_issues'):
                repo_score += 3
            if repo.get('stargazers_count', 0) > 10:
                repo_score += 4
            
            health['factors']['repository_setup'] = repo_score
            health['score'] += repo_score
        
        health['percentage'] = (health['score'] / health['max_score']) * 100
        
        # Health grade
        if health['percentage'] >= 90:
            health['grade'] = 'A'
        elif health['percentage'] >= 80:
            health['grade'] = 'B'
        elif health['percentage'] >= 70:
            health['grade'] = 'C'
        elif health['percentage'] >= 60:
            health['grade'] = 'D'
        else:
            health['grade'] = 'F'
        
        return health
    
    def _generate_project_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Generate comprehensive project recommendations."""
        
        recommendations = []
        
        # Issue recommendations
        issues = data.get('issues_analysis', {})
        if issues and not issues.get('error'):
            issue_recs = issues.get('recommendations', [])
            recommendations.extend(issue_recs)
        
        # PR recommendations
        prs = data.get('pull_requests_analysis', {})
        if prs and not prs.get('error'):
            pr_recs = prs.get('recommendations', [])
            recommendations.extend(pr_recs)
        
        # Repository setup recommendations
        repo = data.get('repository', {})
        if repo and not repo.get('error'):
            if not repo.get('description'):
                recommendations.append("📝 Add a clear repository description")
            if not repo.get('license'):
                recommendations.append("⚖️ Add a license to clarify usage rights")
            if not repo.get('has_wiki'):
                recommendations.append("📚 Enable wiki for additional documentation")
        
        return list(set(recommendations))  # Remove duplicates


__all__ = [
    'IssueManager',
    'PullRequestManager',
    'ProjectManager',
    'IssueTemplate',
    'PullRequestTemplate'
]