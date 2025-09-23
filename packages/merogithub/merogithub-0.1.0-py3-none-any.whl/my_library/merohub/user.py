"""
MeroHub User Management Module
Author: MERO (Telegram: @QP4RM)

Comprehensive user management, profile analysis, and social network
functionality for GitHub users. Provides detailed insights and analytics.
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
from .exceptions import UserError, ValidationError, APIError, validate_username
from .utils import Logger, DataProcessor, retry_on_exception, timed_cache


@dataclass
class UserProfile:
    """User profile data container."""
    
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: Optional[str]
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool
    name: Optional[str] = None
    company: Optional[str] = None
    blog: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    hireable: Optional[bool] = None
    bio: Optional[str] = None
    twitter_username: Optional[str] = None
    public_repos: int = 0
    public_gists: int = 0
    followers: int = 0
    following: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Extended metrics
    influence_score: float = 0.0
    activity_score: float = 0.0
    expertise_score: float = 0.0
    community_score: float = 0.0


@dataclass
class UserAnalytics:
    """User analytics and insights container."""
    
    profile: UserProfile
    repositories: List[Dict[str, Any]] = field(default_factory=list)
    starred_repos: List[Dict[str, Any]] = field(default_factory=list)
    followers_data: List[Dict[str, Any]] = field(default_factory=list)
    following_data: List[Dict[str, Any]] = field(default_factory=list)
    organizations: List[Dict[str, Any]] = field(default_factory=list)
    gists: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    
    # Computed insights
    language_expertise: Dict[str, float] = field(default_factory=dict)
    topic_interests: Dict[str, int] = field(default_factory=dict)
    contribution_patterns: Dict[str, Any] = field(default_factory=dict)
    network_analysis: Dict[str, Any] = field(default_factory=dict)
    activity_timeline: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class UserAnalyzer:
    """Advanced user analysis and metrics calculation."""
    
    def __init__(self, core):
        self.core = core
        self.logger = Logger("UserAnalyzer")
        self.data_processor = DataProcessor()
        self._cache = {}
        self._cache_lock = threading.Lock()
    
    @timed_cache(seconds=600)  # Cache for 10 minutes
    def analyze_user(self, username: str, deep_analysis: bool = True) -> UserAnalytics:
        """Comprehensive user analysis."""
        
        validate_username(username)
        self.logger.info(f"Analyzing user: {username}")
        
        try:
            # Get basic user profile
            user_data = self.core.get_json(f'/users/{username}')
            profile = self._create_user_profile(user_data)
            
            # Get additional data based on analysis depth
            if deep_analysis:
                analytics_data = self._get_comprehensive_user_data(username)
            else:
                analytics_data = self._get_basic_user_data(username)
            
            # Create analytics object
            analytics = UserAnalytics(profile=profile, **analytics_data)
            
            # Compute insights
            self._compute_user_insights(analytics)
            self._compute_user_scores(analytics)
            self._generate_recommendations(analytics)
            
            return analytics
            
        except Exception as e:
            raise UserError(f"Failed to analyze user: {e}",
                          username=username, operation="analyze")
    
    def _create_user_profile(self, user_data: Dict[str, Any]) -> UserProfile:
        """Create UserProfile from API data."""
        
        created_at = None
        updated_at = None
        
        if user_data.get('created_at'):
            created_at = datetime.fromisoformat(user_data['created_at'].replace('Z', '+00:00'))
        
        if user_data.get('updated_at'):
            updated_at = datetime.fromisoformat(user_data['updated_at'].replace('Z', '+00:00'))
        
        return UserProfile(
            login=user_data['login'],
            id=user_data['id'],
            node_id=user_data['node_id'],
            avatar_url=user_data['avatar_url'],
            gravatar_id=user_data.get('gravatar_id'),
            url=user_data['url'],
            html_url=user_data['html_url'],
            followers_url=user_data['followers_url'],
            following_url=user_data['following_url'],
            gists_url=user_data['gists_url'],
            starred_url=user_data['starred_url'],
            subscriptions_url=user_data['subscriptions_url'],
            organizations_url=user_data['organizations_url'],
            repos_url=user_data['repos_url'],
            events_url=user_data['events_url'],
            received_events_url=user_data['received_events_url'],
            type=user_data['type'],
            site_admin=user_data['site_admin'],
            name=user_data.get('name'),
            company=user_data.get('company'),
            blog=user_data.get('blog'),
            location=user_data.get('location'),
            email=user_data.get('email'),
            hireable=user_data.get('hireable'),
            bio=user_data.get('bio'),
            twitter_username=user_data.get('twitter_username'),
            public_repos=user_data.get('public_repos', 0),
            public_gists=user_data.get('public_gists', 0),
            followers=user_data.get('followers', 0),
            following=user_data.get('following', 0),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def _get_comprehensive_user_data(self, username: str) -> Dict[str, Any]:
        """Get comprehensive user data using parallel requests."""
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {
                'repositories': executor.submit(
                    self._get_user_repositories, username
                ),
                'starred_repos': executor.submit(
                    self._get_starred_repositories, username
                ),
                'followers_data': executor.submit(
                    self._get_followers, username
                ),
                'following_data': executor.submit(
                    self._get_following, username
                ),
                'organizations': executor.submit(
                    self._get_organizations, username
                ),
                'gists': executor.submit(
                    self._get_gists, username
                ),
                'events': executor.submit(
                    self._get_recent_events, username
                )
            }
            
            results = {}
            for key, future in futures.items():
                try:
                    results[key] = future.result(timeout=30)
                except Exception as e:
                    self.logger.warning(f"Failed to get {key} for {username}: {e}")
                    results[key] = []
        
        return results
    
    def _get_basic_user_data(self, username: str) -> Dict[str, Any]:
        """Get basic user data for lightweight analysis."""
        
        return {
            'repositories': self._get_user_repositories(username, limit=20),
            'starred_repos': [],
            'followers_data': [],
            'following_data': [],
            'organizations': self._get_organizations(username),
            'gists': [],
            'events': []
        }
    
    def _get_user_repositories(self, username: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get user's repositories."""
        try:
            repos = self.core.paginate(
                f'/users/{username}/repos',
                params={'sort': 'updated', 'direction': 'desc'},
                per_page=100,
                max_pages=3 if not limit else (limit // 100) + 1
            )
            
            if limit:
                repos = repos[:limit]
            
            # Enhance repository data
            for repo in repos:
                # Calculate repository score
                stars = repo.get('stargazers_count', 0)
                forks = repo.get('forks_count', 0)
                watchers = repo.get('watchers_count', 0)
                
                repo['repo_score'] = stars * 3 + forks * 2 + watchers * 1
                
                # Add activity indicator
                if repo.get('pushed_at'):
                    pushed_date = datetime.fromisoformat(repo['pushed_at'].replace('Z', '+00:00'))
                    days_since_update = (datetime.now(pushed_date.tzinfo) - pushed_date).days
                    repo['days_since_update'] = days_since_update
                    repo['is_active'] = days_since_update <= 30
            
            return repos
            
        except Exception as e:
            self.logger.error(f"Failed to get repositories for {username}: {e}")
            return []
    
    def _get_starred_repositories(self, username: str) -> List[Dict[str, Any]]:
        """Get repositories starred by user."""
        try:
            return self.core.paginate(
                f'/users/{username}/starred',
                params={'sort': 'created', 'direction': 'desc'},
                per_page=100,
                max_pages=2  # Limit to 200 most recent stars
            )
        except Exception as e:
            self.logger.error(f"Failed to get starred repos for {username}: {e}")
            return []
    
    def _get_followers(self, username: str) -> List[Dict[str, Any]]:
        """Get user's followers."""
        try:
            return self.core.paginate(
                f'/users/{username}/followers',
                per_page=100,
                max_pages=2  # Limit to 200 followers
            )
        except Exception as e:
            self.logger.error(f"Failed to get followers for {username}: {e}")
            return []
    
    def _get_following(self, username: str) -> List[Dict[str, Any]]:
        """Get users followed by user."""
        try:
            return self.core.paginate(
                f'/users/{username}/following',
                per_page=100,
                max_pages=2  # Limit to 200 following
            )
        except Exception as e:
            self.logger.error(f"Failed to get following for {username}: {e}")
            return []
    
    def _get_organizations(self, username: str) -> List[Dict[str, Any]]:
        """Get user's organizations."""
        try:
            return self.core.paginate(f'/users/{username}/orgs', per_page=100, max_pages=1)
        except Exception as e:
            self.logger.error(f"Failed to get organizations for {username}: {e}")
            return []
    
    def _get_gists(self, username: str) -> List[Dict[str, Any]]:
        """Get user's gists."""
        try:
            return self.core.paginate(
                f'/users/{username}/gists',
                params={'per_page': 100},
                per_page=100,
                max_pages=1
            )
        except Exception as e:
            self.logger.error(f"Failed to get gists for {username}: {e}")
            return []
    
    def _get_recent_events(self, username: str) -> List[Dict[str, Any]]:
        """Get user's recent public events."""
        try:
            return self.core.paginate(
                f'/users/{username}/events/public',
                per_page=100,
                max_pages=1
            )
        except Exception as e:
            self.logger.error(f"Failed to get events for {username}: {e}")
            return []
    
    def _compute_user_insights(self, analytics: UserAnalytics):
        """Compute advanced user insights."""
        
        # Language expertise analysis
        self._compute_language_expertise(analytics)
        
        # Topic interests analysis
        self._compute_topic_interests(analytics)
        
        # Contribution patterns
        self._compute_contribution_patterns(analytics)
        
        # Network analysis
        self._compute_network_analysis(analytics)
        
        # Activity timeline
        self._compute_activity_timeline(analytics)
    
    def _compute_language_expertise(self, analytics: UserAnalytics):
        """Compute programming language expertise scores."""
        
        language_stats = defaultdict(lambda: {'repos': 0, 'stars': 0, 'size': 0})
        
        for repo in analytics.repositories:
            language = repo.get('language')
            if language:
                language_stats[language]['repos'] += 1
                language_stats[language]['stars'] += repo.get('stargazers_count', 0)
                language_stats[language]['size'] += repo.get('size', 0)
        
        # Calculate expertise scores
        total_repos = len(analytics.repositories)
        total_stars = sum(repo.get('stargazers_count', 0) for repo in analytics.repositories)
        
        for language, stats in language_stats.items():
            # Composite score based on multiple factors
            repo_percentage = (stats['repos'] / total_repos) * 100 if total_repos > 0 else 0
            star_percentage = (stats['stars'] / total_stars) * 100 if total_stars > 0 else 0
            
            # Weight: 40% repos, 40% stars, 20% code size
            expertise_score = (
                repo_percentage * 0.4 +
                star_percentage * 0.4 +
                min(stats['size'] / 10000, 100) * 0.2  # Normalize size
            )
            
            analytics.language_expertise[language] = round(expertise_score, 2)
        
        # Sort by expertise score
        analytics.language_expertise = dict(
            sorted(analytics.language_expertise.items(), 
                  key=lambda x: x[1], reverse=True)
        )
    
    def _compute_topic_interests(self, analytics: UserAnalytics):
        """Compute topic interests based on repositories and stars."""
        
        topic_counter = Counter()
        
        # From own repositories
        for repo in analytics.repositories:
            topics = repo.get('topics', [])
            for topic in topics:
                topic_counter[topic] += 2  # Own repos count double
        
        # From starred repositories
        for repo in analytics.starred_repos[:100]:  # Limit to recent 100 stars
            topics = repo.get('topics', [])
            for topic in topics:
                topic_counter[topic] += 1
        
        # Convert to dict and sort
        analytics.topic_interests = dict(topic_counter.most_common(20))
    
    def _compute_contribution_patterns(self, analytics: UserAnalytics):
        """Compute contribution patterns and activity analysis."""
        
        patterns = {
            'total_repositories': len(analytics.repositories),
            'active_repositories': 0,
            'total_stars_earned': 0,
            'total_forks_received': 0,
            'repository_creation_trend': defaultdict(int),
            'language_distribution': defaultdict(int),
            'repository_types': {'original': 0, 'forks': 0},
            'average_repo_size': 0,
            'most_successful_repos': []
        }
        
        repo_sizes = []
        creation_dates = []
        
        for repo in analytics.repositories:
            # Activity check
            if repo.get('is_active'):
                patterns['active_repositories'] += 1
            
            # Stars and forks
            patterns['total_stars_earned'] += repo.get('stargazers_count', 0)
            patterns['total_forks_received'] += repo.get('forks_count', 0)
            
            # Repository creation trend
            if repo.get('created_at'):
                created_date = datetime.fromisoformat(repo['created_at'].replace('Z', '+00:00'))
                month_key = created_date.strftime('%Y-%m')
                patterns['repository_creation_trend'][month_key] += 1
                creation_dates.append(created_date)
            
            # Language distribution
            language = repo.get('language')
            if language:
                patterns['language_distribution'][language] += 1
            
            # Repository types
            if repo.get('fork'):
                patterns['repository_types']['forks'] += 1
            else:
                patterns['repository_types']['original'] += 1
            
            # Size tracking
            repo_sizes.append(repo.get('size', 0))
        
        # Calculate averages
        if repo_sizes:
            patterns['average_repo_size'] = statistics.mean(repo_sizes)
        
        # Most successful repositories
        successful_repos = sorted(
            analytics.repositories,
            key=lambda x: x.get('repo_score', 0),
            reverse=True
        )[:10]
        
        patterns['most_successful_repos'] = [
            {
                'name': repo['name'],
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'language': repo.get('language'),
                'score': repo.get('repo_score', 0)
            }
            for repo in successful_repos
        ]
        
        # Activity timeline
        if creation_dates:
            patterns['account_age_days'] = (datetime.now(creation_dates[0].tzinfo) - 
                                          min(creation_dates)).days
            patterns['repos_per_month'] = (
                len(analytics.repositories) / max(patterns['account_age_days'] / 30.44, 1)
            )
        
        analytics.contribution_patterns = dict(patterns)
    
    def _compute_network_analysis(self, analytics: UserAnalytics):
        """Compute social network analysis."""
        
        network = {
            'followers_count': analytics.profile.followers,
            'following_count': analytics.profile.following,
            'follower_following_ratio': 0,
            'organizations_count': len(analytics.organizations),
            'network_reach_score': 0,
            'influential_followers': [],
            'common_interests_network': {},
            'collaboration_potential': 0
        }
        
        # Calculate ratios
        if analytics.profile.following > 0:
            network['follower_following_ratio'] = (
                analytics.profile.followers / analytics.profile.following
            )
        
        # Network reach score (logarithmic scale)
        import math
        if analytics.profile.followers > 0:
            network['network_reach_score'] = min(
                math.log10(analytics.profile.followers + 1) * 20, 100
            )
        
        # Analyze influential followers (if data available)
        if analytics.followers_data:
            influential_followers = []
            for follower in analytics.followers_data:
                if follower.get('followers', 0) > 100:  # Followers with 100+ followers
                    influential_followers.append({
                        'login': follower['login'],
                        'followers': follower.get('followers', 0),
                        'public_repos': follower.get('public_repos', 0)
                    })
            
            # Sort by influence
            influential_followers.sort(key=lambda x: x['followers'], reverse=True)
            network['influential_followers'] = influential_followers[:10]
        
        # Collaboration potential based on organizations and network
        collaboration_score = 0
        collaboration_score += len(analytics.organizations) * 10  # Organization membership
        collaboration_score += min(analytics.profile.followers / 10, 50)  # Network size
        collaboration_score += min(analytics.contribution_patterns.get('total_forks_received', 0), 30)
        network['collaboration_potential'] = min(collaboration_score, 100)
        
        analytics.network_analysis = network
    
    def _compute_activity_timeline(self, analytics: UserAnalytics):
        """Compute activity timeline and patterns."""
        
        timeline = {
            'account_created': analytics.profile.created_at.isoformat() if analytics.profile.created_at else None,
            'last_activity': analytics.profile.updated_at.isoformat() if analytics.profile.updated_at else None,
            'activity_frequency': 'unknown',
            'peak_activity_periods': [],
            'recent_activity_summary': {},
            'activity_consistency_score': 0
        }
        
        # Analyze recent events for activity patterns
        if analytics.events:
            event_dates = []
            event_types = Counter()
            
            for event in analytics.events:
                if event.get('created_at'):
                    event_date = datetime.fromisoformat(event['created_at'].replace('Z', '+00:00'))
                    event_dates.append(event_date)
                    event_types[event.get('type', 'unknown')] += 1
            
            # Calculate activity frequency
            if event_dates:
                date_range = (max(event_dates) - min(event_dates)).days
                if date_range > 0:
                    events_per_day = len(event_dates) / date_range
                    if events_per_day > 5:
                        timeline['activity_frequency'] = 'very_high'
                    elif events_per_day > 2:
                        timeline['activity_frequency'] = 'high'
                    elif events_per_day > 0.5:
                        timeline['activity_frequency'] = 'moderate'
                    elif events_per_day > 0.1:
                        timeline['activity_frequency'] = 'low'
                    else:
                        timeline['activity_frequency'] = 'very_low'
            
            # Recent activity summary
            timeline['recent_activity_summary'] = dict(event_types.most_common(10))
        
        # Repository creation timeline analysis
        repo_dates = []
        for repo in analytics.repositories:
            if repo.get('created_at'):
                created_date = datetime.fromisoformat(repo['created_at'].replace('Z', '+00:00'))
                repo_dates.append(created_date)
        
        if repo_dates:
            # Find peak activity periods (months with most repo creations)
            monthly_activity = defaultdict(int)
            for date in repo_dates:
                month_key = date.strftime('%Y-%m')
                monthly_activity[month_key] += 1
            
            # Get top 5 most active months
            timeline['peak_activity_periods'] = [
                {'month': month, 'repositories_created': count}
                for month, count in sorted(monthly_activity.items(), 
                                         key=lambda x: x[1], reverse=True)[:5]
            ]
            
            # Activity consistency score
            if len(monthly_activity) > 1:
                monthly_counts = list(monthly_activity.values())
                consistency_score = (1 - (statistics.stdev(monthly_counts) / 
                                         statistics.mean(monthly_counts))) * 100
                timeline['activity_consistency_score'] = max(0, round(consistency_score, 2))
        
        analytics.activity_timeline = timeline
    
    def _compute_user_scores(self, analytics: UserAnalytics):
        """Compute comprehensive user scores."""
        
        # Influence Score (based on followers, stars, network)
        followers = analytics.profile.followers
        stars = analytics.contribution_patterns.get('total_stars_earned', 0)
        
        import math
        influence_base = math.log10(followers + 1) * 15 + math.log10(stars + 1) * 10
        influence_score = min(influence_base, 100)
        
        # Activity Score (based on recent activity and consistency)
        activity_frequency = analytics.activity_timeline.get('activity_frequency', 'unknown')
        activity_mapping = {
            'very_high': 100, 'high': 80, 'moderate': 60, 'low': 40, 'very_low': 20, 'unknown': 0
        }
        activity_base = activity_mapping.get(activity_frequency, 0)
        
        # Adjust for consistency
        consistency = analytics.activity_timeline.get('activity_consistency_score', 0)
        activity_score = (activity_base * 0.7) + (consistency * 0.3)
        
        # Expertise Score (based on language expertise and repository quality)
        if analytics.language_expertise:
            top_language_score = list(analytics.language_expertise.values())[0]
            language_diversity = len(analytics.language_expertise)
            expertise_score = min(top_language_score + (language_diversity * 2), 100)
        else:
            expertise_score = 0
        
        # Community Score (based on collaboration and network)
        community_score = analytics.network_analysis.get('collaboration_potential', 0)
        
        # Update profile with scores
        analytics.profile.influence_score = round(influence_score, 2)
        analytics.profile.activity_score = round(activity_score, 2)
        analytics.profile.expertise_score = round(expertise_score, 2)
        analytics.profile.community_score = round(community_score, 2)
    
    def _generate_recommendations(self, analytics: UserAnalytics):
        """Generate personalized recommendations for the user."""
        
        recommendations = []
        
        # Activity recommendations
        activity_freq = analytics.activity_timeline.get('activity_frequency', 'unknown')
        if activity_freq in ['low', 'very_low']:
            recommendations.append("🚀 Increase your GitHub activity by contributing to open source projects")
        
        # Language expertise recommendations
        if len(analytics.language_expertise) == 1:
            recommendations.append("🌈 Consider exploring additional programming languages to diversify your skills")
        elif len(analytics.language_expertise) > 5:
            recommendations.append("🎯 Focus on your top 2-3 languages to deepen expertise")
        
        # Repository recommendations
        total_repos = analytics.contribution_patterns.get('total_repositories', 0)
        active_repos = analytics.contribution_patterns.get('active_repositories', 0)
        
        if total_repos > 0 and (active_repos / total_repos) < 0.3:
            recommendations.append("🔄 Consider archiving inactive repositories to maintain a clean profile")
        
        if total_repos < 5:
            recommendations.append("📦 Create more repositories to showcase your skills and interests")
        
        # Network recommendations
        followers = analytics.profile.followers
        following = analytics.profile.following
        
        if followers > 0 and following == 0:
            recommendations.append("🤝 Follow other developers in your field to build connections")
        
        if following > followers * 3:
            recommendations.append("⚖️ Consider curating your following list for better engagement")
        
        # Visibility recommendations
        if analytics.profile.bio is None or len(analytics.profile.bio or '') < 50:
            recommendations.append("✍️ Add a compelling bio to help others understand your background")
        
        if analytics.profile.company is None:
            recommendations.append("🏢 Add your company/organization to increase professional visibility")
        
        # Collaboration recommendations
        total_forks = analytics.contribution_patterns.get('total_forks_received', 0)
        if total_forks == 0 and total_repos > 5:
            recommendations.append("🍴 Encourage contributions by adding clear README files and contribution guides")
        
        # Topic recommendations
        if not analytics.topic_interests:
            recommendations.append("🏷️ Add topics to your repositories to improve discoverability")
        
        analytics.recommendations = recommendations


class UserManager:
    """Comprehensive user management functionality."""
    
    def __init__(self, core):
        self.core = core
        self.logger = Logger("UserManager")
        self.analyzer = UserAnalyzer(core)
        self.data_processor = DataProcessor()
    
    def get_user(self, username: Optional[str] = None) -> Dict[str, Any]:
        """Get user information."""
        endpoint = f'/users/{username}' if username else '/user'
        
        try:
            return self.core.get_json(endpoint)
        except Exception as e:
            raise UserError(f"Failed to get user: {e}",
                          username=username, operation="get")
    
    def get_user_analytics(self, username: str, deep_analysis: bool = True) -> UserAnalytics:
        """Get comprehensive user analytics."""
        return self.analyzer.analyze_user(username, deep_analysis)
    
    def get_user_repositories(self, username: str,
                             type: str = "all",
                             sort: str = "updated",
                             direction: str = "desc") -> List[Dict[str, Any]]:
        """Get user repositories."""
        validate_username(username)
        
        params = {
            'type': type,
            'sort': sort,
            'direction': direction
        }
        
        try:
            return self.core.paginate(f'/users/{username}/repos', params=params)
        except Exception as e:
            raise UserError(f"Failed to get user repositories: {e}",
                          username=username, operation="get_repositories")
    
    def get_user_followers(self, username: str) -> List[Dict[str, Any]]:
        """Get user followers."""
        validate_username(username)
        
        try:
            return self.core.paginate(f'/users/{username}/followers')
        except Exception as e:
            raise UserError(f"Failed to get user followers: {e}",
                          username=username, operation="get_followers")
    
    def get_user_following(self, username: str) -> List[Dict[str, Any]]:
        """Get users followed by user."""
        validate_username(username)
        
        try:
            return self.core.paginate(f'/users/{username}/following')
        except Exception as e:
            raise UserError(f"Failed to get user following: {e}",
                          username=username, operation="get_following")
    
    def get_user_organizations(self, username: str) -> List[Dict[str, Any]]:
        """Get user organizations."""
        validate_username(username)
        
        try:
            return self.core.paginate(f'/users/{username}/orgs')
        except Exception as e:
            raise UserError(f"Failed to get user organizations: {e}",
                          username=username, operation="get_organizations")
    
    def follow_user(self, username: str) -> bool:
        """Follow a user."""
        validate_username(username)
        
        try:
            response = self.core.put(f'/user/following/{username}')
            return response.status_code == 204
        except Exception as e:
            raise UserError(f"Failed to follow user: {e}",
                          username=username, operation="follow")
    
    def unfollow_user(self, username: str) -> bool:
        """Unfollow a user."""
        validate_username(username)
        
        try:
            response = self.core.delete(f'/user/following/{username}')
            return response.status_code == 204
        except Exception as e:
            raise UserError(f"Failed to unfollow user: {e}",
                          username=username, operation="unfollow")
    
    def is_following_user(self, username: str) -> bool:
        """Check if currently following a user."""
        validate_username(username)
        
        try:
            response = self.core.get(f'/user/following/{username}')
            return response.status_code == 204
        except APIError as e:
            if e.status_code == 404:
                return False
            raise
        except Exception as e:
            raise UserError(f"Failed to check following status: {e}",
                          username=username, operation="check_following")
    
    def update_profile(self, **kwargs) -> Dict[str, Any]:
        """Update authenticated user profile."""
        
        try:
            return self.core.post_json('/user', json_data=kwargs)
        except Exception as e:
            raise UserError(f"Failed to update profile: {e}",
                          operation="update_profile")
    
    def compare_users(self, usernames: List[str]) -> Dict[str, Any]:
        """Compare multiple users."""
        
        if len(usernames) < 2:
            raise ValidationError("At least 2 users required for comparison")
        
        user_data = {}
        
        # Analyze each user
        with ThreadPoolExecutor(max_workers=len(usernames)) as executor:
            future_to_username = {
                executor.submit(self.get_user_analytics, username, False): username
                for username in usernames
            }
            
            for future in as_completed(future_to_username):
                username = future_to_username[future]
                try:
                    analytics = future.result(timeout=30)
                    user_data[username] = analytics
                except Exception as e:
                    self.logger.error(f"Failed to analyze {username}: {e}")
                    user_data[username] = {'error': str(e)}
        
        # Generate comparison insights
        comparison = self._generate_user_comparison(user_data)
        
        return {
            'users': {k: v for k, v in user_data.items() if not isinstance(v, dict) or 'error' not in v},
            'comparison': comparison,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_user_comparison(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from user comparison."""
        
        valid_users = {k: v for k, v in user_data.items() 
                      if not isinstance(v, dict) or 'error' not in v}
        
        if len(valid_users) < 2:
            return {'error': 'Not enough valid users for comparison'}
        
        comparison = {
            'metrics_comparison': {},
            'leaders': {},
            'insights': []
        }
        
        # Compare key metrics
        metrics = ['followers', 'following', 'public_repos', 'public_gists']
        scores = ['influence_score', 'activity_score', 'expertise_score', 'community_score']
        
        for metric in metrics + scores:
            comparison['metrics_comparison'][metric] = {}
            
            for username, analytics in valid_users.items():
                if isinstance(analytics, UserAnalytics):
                    if metric in scores:
                        value = getattr(analytics.profile, metric, 0)
                    else:
                        value = getattr(analytics.profile, metric, 0)
                    comparison['metrics_comparison'][metric][username] = value
        
        # Find leaders in each category
        for metric, values in comparison['metrics_comparison'].items():
            if values:
                leader = max(values.items(), key=lambda x: x[1])
                comparison['leaders'][metric] = {
                    'username': leader[0],
                    'value': leader[1]
                }
        
        # Generate insights
        insights = []
        
        # Most influential
        influence_leader = comparison['leaders'].get('influence_score', {})
        if influence_leader:
            insights.append(f"🌟 {influence_leader['username']} has the highest influence score")
        
        # Most active
        activity_leader = comparison['leaders'].get('activity_score', {})
        if activity_leader:
            insights.append(f"⚡ {activity_leader['username']} is the most active")
        
        # Most repositories
        repos_leader = comparison['leaders'].get('public_repos', {})
        if repos_leader:
            insights.append(f"📦 {repos_leader['username']} has the most public repositories")
        
        comparison['insights'] = insights
        
        return comparison


class ProfileManager:
    """Profile management and optimization utilities."""
    
    def __init__(self, core):
        self.core = core
        self.logger = Logger("ProfileManager")
        self.user_manager = UserManager(core)
    
    def get_profile_optimization_suggestions(self, username: str) -> Dict[str, Any]:
        """Get suggestions for optimizing user profile."""
        
        analytics = self.user_manager.get_user_analytics(username, deep_analysis=True)
        
        suggestions = {
            'profile_completeness': self._calculate_profile_completeness(analytics.profile),
            'optimization_suggestions': analytics.recommendations,
            'quick_wins': [],
            'long_term_goals': [],
            'benchmarks': self._get_profile_benchmarks(analytics)
        }
        
        # Categorize suggestions
        for suggestion in analytics.recommendations:
            if any(word in suggestion.lower() for word in ['add', 'create', 'enable']):
                suggestions['quick_wins'].append(suggestion)
            else:
                suggestions['long_term_goals'].append(suggestion)
        
        return suggestions
    
    def _calculate_profile_completeness(self, profile: UserProfile) -> Dict[str, Any]:
        """Calculate profile completeness score."""
        
        completeness = {
            'score': 0,
            'max_score': 100,
            'completed_fields': [],
            'missing_fields': []
        }
        
        # Profile fields and their weights
        fields = {
            'name': 15,
            'bio': 20,
            'company': 15,
            'location': 10,
            'email': 10,
            'blog': 10,
            'twitter_username': 10,
            'hireable': 10
        }
        
        for field, weight in fields.items():
            value = getattr(profile, field, None)
            if value:
                completeness['score'] += weight
                completeness['completed_fields'].append(field)
            else:
                completeness['missing_fields'].append(field)
        
        completeness['percentage'] = (completeness['score'] / completeness['max_score']) * 100
        
        return completeness
    
    def _get_profile_benchmarks(self, analytics: UserAnalytics) -> Dict[str, Any]:
        """Get benchmarks for profile metrics."""
        
        # These would ideally be based on real data analysis
        benchmarks = {
            'followers': {
                'beginner': 10,
                'intermediate': 100,
                'advanced': 1000,
                'expert': 5000
            },
            'public_repos': {
                'beginner': 5,
                'intermediate': 25,
                'advanced': 100,
                'expert': 500
            },
            'influence_score': {
                'beginner': 20,
                'intermediate': 50,
                'advanced': 75,
                'expert': 90
            }
        }
        
        user_level = {}
        for metric, levels in benchmarks.items():
            if metric == 'influence_score':
                user_value = analytics.profile.influence_score
            else:
                user_value = getattr(analytics.profile, metric, 0)
            
            if user_value >= levels['expert']:
                user_level[metric] = 'expert'
            elif user_value >= levels['advanced']:
                user_level[metric] = 'advanced'
            elif user_value >= levels['intermediate']:
                user_level[metric] = 'intermediate'
            else:
                user_level[metric] = 'beginner'
        
        return {
            'benchmarks': benchmarks,
            'user_levels': user_level
        }


__all__ = [
    'UserManager',
    'UserAnalyzer',
    'ProfileManager',
    'UserProfile',
    'UserAnalytics'
]