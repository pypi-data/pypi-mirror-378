"""
MeroHub AI Analysis Module
Author: MERO (Telegram: @QP4RM)

Advanced AI and neural network analysis capabilities for GitHub data.
Provides machine learning insights, predictive analytics, and intelligent recommendations.
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    nn = None
    optim = None

from .exceptions import AIAnalysisError, ValidationError
from .utils import Logger, DataProcessor, timed_cache


@dataclass
class AIInsight:
    """AI-generated insight container."""
    
    category: str
    confidence: float
    insight: str
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class MLPrediction:
    """Machine learning prediction container."""
    
    prediction_type: str
    predicted_value: Union[float, int, str]
    confidence: float
    features_used: List[str] = field(default_factory=list)
    model_accuracy: Optional[float] = None
    prediction_date: str = field(default_factory=lambda: datetime.now().isoformat())


class RepoTrendPredictor:
    """Simple neural network for predicting repository trends."""
    
    def __init__(self, input_size: int = 10, hidden_size: int = 20, output_size: int = 1):
        if not TORCH_AVAILABLE:
            raise AIAnalysisError("PyTorch not available for neural network analysis")
        
        self.model = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, output_size),
            nn.Sigmoid()
        )
        
        self.input_size = input_size
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()
        self.trained = False
    
    def prepare_features(self, repo_data: Dict[str, Any]) -> torch.Tensor:
        """Extract and normalize features from repository data."""
        
        features = []
        
        # Basic repository metrics (normalized)
        stars = min(repo_data.get('stargazers_count', 0) / 1000, 10)  # Cap at 10k
        forks = min(repo_data.get('forks_count', 0) / 100, 10)      # Cap at 1k
        watchers = min(repo_data.get('watchers_count', 0) / 1000, 10)
        issues = min(repo_data.get('open_issues_count', 0) / 50, 10)
        size = min(repo_data.get('size', 0) / 10000, 10)            # Cap at 100MB
        
        features.extend([stars, forks, watchers, issues, size])
        
        # Time-based features
        if repo_data.get('created_at'):
            created_date = datetime.fromisoformat(repo_data['created_at'].replace('Z', '+00:00'))
            days_old = (datetime.now(created_date.tzinfo) - created_date).days
            age_factor = min(days_old / 365, 10)  # Normalize to years, cap at 10
        else:
            age_factor = 0
        
        if repo_data.get('pushed_at'):
            pushed_date = datetime.fromisoformat(repo_data['pushed_at'].replace('Z', '+00:00'))
            days_since_update = (datetime.now(pushed_date.tzinfo) - pushed_date).days
            freshness = max(0, 10 - (days_since_update / 30))  # 10 = very fresh, 0 = stale
        else:
            freshness = 0
        
        features.extend([age_factor, freshness])
        
        # Boolean features
        has_license = 1 if repo_data.get('license') else 0
        has_description = 1 if repo_data.get('description') else 0
        has_wiki = 1 if repo_data.get('has_wiki') else 0
        
        features.extend([has_license, has_description, has_wiki])
        
        # Pad or truncate to input_size
        if len(features) < self.input_size:
            features.extend([0] * (self.input_size - len(features)))
        else:
            features = features[:self.input_size]
        
        return torch.FloatTensor(features)
    
    def train_simple(self, training_data: List[Tuple[Dict[str, Any], float]]) -> float:
        """Train the model with simple training data."""
        
        if len(training_data) < 10:
            raise AIAnalysisError("Need at least 10 training samples")
        
        X = []
        y = []
        
        for repo_data, target in training_data:
            features = self.prepare_features(repo_data)
            X.append(features)
            y.append(target)
        
        X_tensor = torch.stack(X)
        y_tensor = torch.FloatTensor(y).unsqueeze(1)
        
        # Simple training loop
        self.model.train()
        total_loss = 0
        
        for epoch in range(100):
            self.optimizer.zero_grad()
            outputs = self.model(X_tensor)
            loss = self.criterion(outputs, y_tensor)
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()
        
        self.trained = True
        avg_loss = total_loss / 100
        return avg_loss
    
    def predict(self, repo_data: Dict[str, Any]) -> float:
        """Make a prediction for a repository."""
        
        if not self.trained:
            # Return a simple heuristic prediction
            return self._heuristic_prediction(repo_data)
        
        self.model.eval()
        with torch.no_grad():
            features = self.prepare_features(repo_data).unsqueeze(0)
            prediction = self.model(features).item()
        
        return prediction
    
    def _heuristic_prediction(self, repo_data: Dict[str, Any]) -> float:
        """Simple heuristic prediction when model isn't trained."""
        
        score = 0
        
        # Star-based score
        stars = repo_data.get('stargazers_count', 0)
        if stars > 1000:
            score += 0.3
        elif stars > 100:
            score += 0.2
        elif stars > 10:
            score += 0.1
        
        # Recency score
        if repo_data.get('pushed_at'):
            pushed_date = datetime.fromisoformat(repo_data['pushed_at'].replace('Z', '+00:00'))
            days_since_update = (datetime.now(pushed_date.tzinfo) - pushed_date).days
            if days_since_update <= 7:
                score += 0.2
            elif days_since_update <= 30:
                score += 0.1
        
        # Quality indicators
        if repo_data.get('license'):
            score += 0.1
        if repo_data.get('description'):
            score += 0.1
        if repo_data.get('has_wiki'):
            score += 0.05
        if repo_data.get('has_issues'):
            score += 0.05
        
        # Activity score
        if repo_data.get('forks_count', 0) > 10:
            score += 0.1
        if repo_data.get('open_issues_count', 0) > 0:
            score += 0.05
        
        return min(score, 1.0)  # Cap at 1.0


class AIAnalyzer:
    """AI-powered analysis for GitHub repositories and users."""
    
    def __init__(self, core):
        self.core = core
        self.logger = Logger("AIAnalyzer")
        self.data_processor = DataProcessor()
        self.predictor = None
        
        if TORCH_AVAILABLE:
            self.predictor = RepoTrendPredictor()
        else:
            self.logger.warning("PyTorch not available, using simplified analysis")
    
    @timed_cache(seconds=600)
    def analyze_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Comprehensive AI analysis of a repository."""
        
        try:
            self.logger.info(f"AI analyzing repository: {owner}/{repo}")
            
            # Get repository data
            repo_data = self.core.get_json(f'/repos/{owner}/{repo}')
            
            # Perform various analyses
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {
                    'language_analysis': executor.submit(self._analyze_languages, owner, repo),
                    'contributor_analysis': executor.submit(self._analyze_contributors, owner, repo),
                    'activity_analysis': executor.submit(self._analyze_activity_patterns, owner, repo),
                    'quality_assessment': executor.submit(self._assess_code_quality, repo_data),
                    'trend_prediction': executor.submit(self._predict_trends, repo_data)
                }
                
                analysis_results = {}
                for key, future in futures.items():
                    try:
                        analysis_results[key] = future.result(timeout=30)
                    except Exception as e:
                        self.logger.warning(f"Failed {key}: {e}")
                        analysis_results[key] = {'error': str(e)}
            
            # Generate AI insights
            insights = self._generate_insights(repo_data, analysis_results)
            
            # Generate recommendations
            recommendations = self._generate_ai_recommendations(repo_data, analysis_results)
            
            return {
                'repository': f"{owner}/{repo}",
                'analysis_timestamp': datetime.now().isoformat(),
                'ai_analyses': analysis_results,
                'ai_insights': insights,
                'ai_recommendations': recommendations,
                'overall_score': self._calculate_ai_score(analysis_results),
                'confidence_level': self._calculate_confidence(analysis_results)
            }
            
        except Exception as e:
            raise AIAnalysisError(f"AI analysis failed: {e}",
                                analysis_type="repository",
                                data_size=0)
    
    def _analyze_languages(self, owner: str, repo: str) -> Dict[str, Any]:
        """Analyze programming languages used in the repository."""
        
        try:
            languages = self.core.get_json(f'/repos/{owner}/{repo}/languages')
            
            if not languages:
                return {'total_languages': 0, 'diversity_score': 0}
            
            total_bytes = sum(languages.values())
            language_percentages = {
                lang: (bytes_count / total_bytes) * 100 
                for lang, bytes_count in languages.items()
            }
            
            # Calculate diversity score (Shannon entropy)
            diversity_score = 0
            for percentage in language_percentages.values():
                if percentage > 0:
                    p = percentage / 100
                    diversity_score -= p * np.log2(p)
            
            # Normalize diversity score (0-10 scale)
            max_diversity = np.log2(len(languages))
            diversity_score = (diversity_score / max_diversity) * 10 if max_diversity > 0 else 0
            
            # Language complexity assessment
            complex_languages = ['C++', 'Rust', 'Assembly', 'Fortran', 'Haskell', 'Scala']
            simple_languages = ['Python', 'JavaScript', 'HTML', 'CSS', 'Markdown']
            
            complexity_score = 0
            for lang, percentage in language_percentages.items():
                if lang in complex_languages:
                    complexity_score += (percentage / 100) * 3
                elif lang in simple_languages:
                    complexity_score += (percentage / 100) * 1
                else:
                    complexity_score += (percentage / 100) * 2
            
            return {
                'total_languages': len(languages),
                'primary_language': max(language_percentages, key=language_percentages.get),
                'language_distribution': language_percentages,
                'diversity_score': round(diversity_score, 2),
                'complexity_score': round(complexity_score, 2),
                'total_code_bytes': total_bytes
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_contributors(self, owner: str, repo: str) -> Dict[str, Any]:
        """Analyze contributor patterns and collaboration."""
        
        try:
            contributors = self.core.paginate(f'/repos/{owner}/{repo}/contributors', max_pages=3)
            
            if not contributors:
                return {'total_contributors': 0, 'collaboration_score': 0}
            
            # Calculate contribution distribution
            total_contributions = sum(c.get('contributions', 0) for c in contributors)
            
            if total_contributions == 0:
                return {'total_contributors': len(contributors), 'collaboration_score': 0}
            
            # Gini coefficient for contribution inequality
            contributions = sorted([c.get('contributions', 0) for c in contributors])
            n = len(contributions)
            index = np.arange(1, n + 1)
            gini = (2 * np.sum(index * contributions)) / (n * total_contributions) - (n + 1) / n
            
            # Collaboration score (inverse of inequality)
            collaboration_score = (1 - gini) * 10
            
            # Contributor diversity
            top_contributor_share = max(c.get('contributions', 0) for c in contributors) / total_contributions
            
            return {
                'total_contributors': len(contributors),
                'total_contributions': total_contributions,
                'collaboration_score': round(collaboration_score, 2),
                'top_contributor_dominance': round(top_contributor_share * 100, 2),
                'contribution_inequality': round(gini, 3),
                'average_contributions': round(total_contributions / len(contributors), 1),
                'top_contributors': contributors[:5]
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_activity_patterns(self, owner: str, repo: str) -> Dict[str, Any]:
        """Analyze repository activity patterns."""
        
        try:
            # Get recent commits
            since_date = (datetime.now() - timedelta(days=90)).isoformat()
            commits = self.core.paginate(
                f'/repos/{owner}/{repo}/commits',
                params={'since': since_date},
                max_pages=5
            )
            
            if not commits:
                return {'activity_level': 'inactive', 'activity_score': 0}
            
            # Analyze commit patterns
            commit_dates = []
            commit_hours = []
            commit_days = []
            
            for commit in commits:
                if commit.get('commit', {}).get('author', {}).get('date'):
                    date_str = commit['commit']['author']['date']
                    commit_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    commit_dates.append(commit_date)
                    commit_hours.append(commit_date.hour)
                    commit_days.append(commit_date.weekday())
            
            if not commit_dates:
                return {'activity_level': 'inactive', 'activity_score': 0}
            
            # Calculate activity metrics
            days_span = (max(commit_dates) - min(commit_dates)).days if len(commit_dates) > 1 else 1
            commits_per_day = len(commits) / max(days_span, 1)
            
            # Activity consistency (coefficient of variation)
            if len(commit_dates) > 5:
                daily_commits = defaultdict(int)
                for date in commit_dates:
                    daily_commits[date.date()] += 1
                
                daily_counts = list(daily_commits.values())
                consistency = 1 - (np.std(daily_counts) / np.mean(daily_counts)) if np.mean(daily_counts) > 0 else 0
                consistency = max(0, consistency)
            else:
                consistency = 0.5
            
            # Activity score
            activity_score = min(commits_per_day * 2 + consistency * 3, 10)
            
            # Determine activity level
            if activity_score >= 7:
                activity_level = 'very_active'
            elif activity_score >= 5:
                activity_level = 'active'
            elif activity_score >= 3:
                activity_level = 'moderate'
            elif activity_score >= 1:
                activity_level = 'low'
            else:
                activity_level = 'inactive'
            
            return {
                'activity_level': activity_level,
                'activity_score': round(activity_score, 2),
                'commits_analyzed': len(commits),
                'commits_per_day': round(commits_per_day, 2),
                'activity_consistency': round(consistency, 2),
                'peak_activity_hour': statistics.mode(commit_hours) if commit_hours else None,
                'most_active_day': statistics.mode(commit_days) if commit_days else None,
                'activity_timespan_days': days_span
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _assess_code_quality(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess code quality based on repository characteristics."""
        
        try:
            quality_score = 0
            quality_factors = {}
            
            # Documentation score
            has_readme = bool(repo_data.get('has_pages') or 'readme' in repo_data.get('description', '').lower())
            has_description = bool(repo_data.get('description'))
            has_wiki = bool(repo_data.get('has_wiki'))
            
            documentation_score = (
                (2 if has_readme else 0) +
                (1 if has_description else 0) +
                (1 if has_wiki else 0)
            )
            quality_factors['documentation'] = documentation_score
            quality_score += documentation_score
            
            # License score
            license_score = 2 if repo_data.get('license') else 0
            quality_factors['license'] = license_score
            quality_score += license_score
            
            # Issue management score
            has_issues = repo_data.get('has_issues', False)
            open_issues = repo_data.get('open_issues_count', 0)
            
            if has_issues:
                # Good if issues are enabled and managed (not too many open)
                if open_issues < 10:
                    issue_score = 2
                elif open_issues < 50:
                    issue_score = 1
                else:
                    issue_score = 0.5
            else:
                issue_score = 0
            
            quality_factors['issue_management'] = issue_score
            quality_score += issue_score
            
            # Community engagement score
            stars = repo_data.get('stargazers_count', 0)
            forks = repo_data.get('forks_count', 0)
            watchers = repo_data.get('watchers_count', 0)
            
            engagement_score = min(
                np.log10(stars + 1) * 0.5 +
                np.log10(forks + 1) * 0.3 +
                np.log10(watchers + 1) * 0.2,
                3
            )
            quality_factors['community_engagement'] = round(engagement_score, 2)
            quality_score += engagement_score
            
            # Maintenance score
            if repo_data.get('pushed_at'):
                pushed_date = datetime.fromisoformat(repo_data['pushed_at'].replace('Z', '+00:00'))
                days_since_update = (datetime.now(pushed_date.tzinfo) - pushed_date).days
                
                if days_since_update <= 7:
                    maintenance_score = 2
                elif days_since_update <= 30:
                    maintenance_score = 1.5
                elif days_since_update <= 90:
                    maintenance_score = 1
                elif days_since_update <= 365:
                    maintenance_score = 0.5
                else:
                    maintenance_score = 0
            else:
                maintenance_score = 0
            
            quality_factors['maintenance'] = maintenance_score
            quality_score += maintenance_score
            
            # Normalize to 0-10 scale
            max_score = 2 + 2 + 2 + 3 + 2  # Sum of maximum possible scores
            normalized_score = (quality_score / max_score) * 10
            
            # Quality grade
            if normalized_score >= 8.5:
                grade = 'A'
            elif normalized_score >= 7:
                grade = 'B'
            elif normalized_score >= 5.5:
                grade = 'C'
            elif normalized_score >= 4:
                grade = 'D'
            else:
                grade = 'F'
            
            return {
                'overall_quality_score': round(normalized_score, 2),
                'quality_grade': grade,
                'quality_factors': quality_factors,
                'strengths': self._identify_quality_strengths(quality_factors),
                'improvement_areas': self._identify_improvement_areas(quality_factors)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _predict_trends(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict repository trends using AI/ML."""
        
        try:
            predictions = {}
            
            # Use neural network predictor if available
            if self.predictor and TORCH_AVAILABLE:
                trend_score = self.predictor.predict(repo_data)
                predictions['ai_trend_score'] = round(trend_score, 3)
                
                if trend_score > 0.7:
                    predictions['trend_prediction'] = 'rising'
                elif trend_score > 0.4:
                    predictions['trend_prediction'] = 'stable'
                else:
                    predictions['trend_prediction'] = 'declining'
            
            # Growth prediction based on historical data
            current_stars = repo_data.get('stargazers_count', 0)
            
            if repo_data.get('created_at'):
                created_date = datetime.fromisoformat(repo_data['created_at'].replace('Z', '+00:00'))
                days_old = (datetime.now(created_date.tzinfo) - created_date).days
                
                if days_old > 0:
                    stars_per_day = current_stars / days_old
                    
                    # Predict stars in next 30/90/365 days
                    predictions['predicted_stars_30d'] = int(current_stars + stars_per_day * 30)
                    predictions['predicted_stars_90d'] = int(current_stars + stars_per_day * 90)
                    predictions['predicted_stars_1y'] = int(current_stars + stars_per_day * 365)
                    
                    # Growth rate classification
                    if stars_per_day > 1:
                        predictions['growth_rate'] = 'rapid'
                    elif stars_per_day > 0.1:
                        predictions['growth_rate'] = 'steady'
                    elif stars_per_day > 0.01:
                        predictions['growth_rate'] = 'slow'
                    else:
                        predictions['growth_rate'] = 'stagnant'
            
            # Popularity prediction factors
            factors = []
            
            # Recent activity factor
            if repo_data.get('pushed_at'):
                pushed_date = datetime.fromisoformat(repo_data['pushed_at'].replace('Z', '+00:00'))
                days_since_update = (datetime.now(pushed_date.tzinfo) - pushed_date).days
                if days_since_update <= 30:
                    factors.append('recent_activity')
            
            # Community factor
            if repo_data.get('forks_count', 0) > 10:
                factors.append('strong_community')
            
            # Quality factor
            if repo_data.get('license') and repo_data.get('description'):
                factors.append('good_documentation')
            
            predictions['positive_factors'] = factors
            predictions['confidence'] = min(len(factors) / 3, 1.0)
            
            return predictions
            
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_insights(self, repo_data: Dict[str, Any], 
                          analyses: Dict[str, Any]) -> List[AIInsight]:
        """Generate AI-powered insights from analysis results."""
        
        insights = []
        
        # Language insights
        lang_analysis = analyses.get('language_analysis', {})
        if not lang_analysis.get('error') and lang_analysis.get('diversity_score', 0) > 5:
            insights.append(AIInsight(
                category='language_diversity',
                confidence=0.8,
                insight=f"High language diversity (score: {lang_analysis['diversity_score']:.1f}) indicates a complex, multi-faceted project",
                supporting_data=lang_analysis,
                recommendations=['Consider documenting the architecture to help newcomers understand the codebase structure']
            ))
        
        # Activity insights
        activity_analysis = analyses.get('activity_analysis', {})
        if not activity_analysis.get('error'):
            activity_level = activity_analysis.get('activity_level', 'unknown')
            if activity_level == 'very_active':
                insights.append(AIInsight(
                    category='high_activity',
                    confidence=0.9,
                    insight="Repository shows very high development activity, indicating active maintenance",
                    supporting_data=activity_analysis,
                    recommendations=['Maintain this excellent development pace', 'Consider automating releases for frequent updates']
                ))
            elif activity_level == 'inactive':
                insights.append(AIInsight(
                    category='low_activity',
                    confidence=0.7,
                    insight="Repository shows low activity, which may indicate maintenance issues or project completion",
                    supporting_data=activity_analysis,
                    recommendations=['Update documentation to clarify project status', 'Consider archiving if project is complete']
                ))
        
        # Quality insights
        quality_analysis = analyses.get('quality_assessment', {})
        if not quality_analysis.get('error'):
            quality_score = quality_analysis.get('overall_quality_score', 0)
            if quality_score > 8:
                insights.append(AIInsight(
                    category='high_quality',
                    confidence=0.85,
                    insight=f"Excellent code quality score ({quality_score:.1f}/10) indicates well-maintained project",
                    supporting_data=quality_analysis,
                    recommendations=['Share best practices with the community', 'Consider creating templates for other projects']
                ))
        
        # Trend insights
        trend_analysis = analyses.get('trend_prediction', {})
        if not trend_analysis.get('error'):
            if trend_analysis.get('trend_prediction') == 'rising':
                insights.append(AIInsight(
                    category='positive_trend',
                    confidence=0.7,
                    insight="AI analysis predicts positive growth trend for this repository",
                    supporting_data=trend_analysis,
                    recommendations=['Prepare for increased community attention', 'Ensure scalable contribution processes']
                ))
        
        return insights
    
    def _generate_ai_recommendations(self, repo_data: Dict[str, Any], 
                                   analyses: Dict[str, Any]) -> List[str]:
        """Generate AI-powered recommendations."""
        
        recommendations = []
        
        # Quality-based recommendations
        quality_analysis = analyses.get('quality_assessment', {})
        if quality_analysis and not quality_analysis.get('error'):
            improvement_areas = quality_analysis.get('improvement_areas', [])
            for area in improvement_areas:
                if area == 'documentation':
                    recommendations.append("🤖 AI suggests improving documentation to increase project accessibility")
                elif area == 'maintenance':
                    recommendations.append("🤖 AI detects maintenance gaps - consider more frequent updates")
                elif area == 'community':
                    recommendations.append("🤖 AI recommends enhancing community engagement through better issue management")
        
        # Activity-based recommendations
        activity_analysis = analyses.get('activity_analysis', {})
        if activity_analysis and not activity_analysis.get('error'):
            activity_score = activity_analysis.get('activity_score', 0)
            if activity_score < 3:
                recommendations.append("🤖 AI suggests increasing development activity to maintain project momentum")
        
        # Language-based recommendations
        lang_analysis = analyses.get('language_analysis', {})
        if lang_analysis and not lang_analysis.get('error'):
            complexity_score = lang_analysis.get('complexity_score', 0)
            if complexity_score > 7:
                recommendations.append("🤖 AI detects high code complexity - consider adding more comprehensive documentation")
        
        # Contribution-based recommendations
        contrib_analysis = analyses.get('contributor_analysis', {})
        if contrib_analysis and not contrib_analysis.get('error'):
            dominance = contrib_analysis.get('top_contributor_dominance', 0)
            if dominance > 80:
                recommendations.append("🤖 AI suggests encouraging more diverse contributions to reduce bus factor")
        
        return recommendations
    
    def _calculate_ai_score(self, analyses: Dict[str, Any]) -> float:
        """Calculate overall AI score."""
        
        scores = []
        
        # Quality score
        quality_analysis = analyses.get('quality_assessment', {})
        if quality_analysis and not quality_analysis.get('error'):
            scores.append(quality_analysis.get('overall_quality_score', 0))
        
        # Activity score
        activity_analysis = analyses.get('activity_analysis', {})
        if activity_analysis and not activity_analysis.get('error'):
            scores.append(activity_analysis.get('activity_score', 0))
        
        # Language diversity score
        lang_analysis = analyses.get('language_analysis', {})
        if lang_analysis and not lang_analysis.get('error'):
            scores.append(lang_analysis.get('diversity_score', 0))
        
        # Collaboration score
        contrib_analysis = analyses.get('contributor_analysis', {})
        if contrib_analysis and not contrib_analysis.get('error'):
            scores.append(contrib_analysis.get('collaboration_score', 0))
        
        if scores:
            return round(sum(scores) / len(scores), 2)
        else:
            return 0.0
    
    def _calculate_confidence(self, analyses: Dict[str, Any]) -> float:
        """Calculate confidence level of the analysis."""
        
        successful_analyses = sum(1 for analysis in analyses.values() if not analysis.get('error'))
        total_analyses = len(analyses)
        
        if total_analyses == 0:
            return 0.0
        
        base_confidence = successful_analyses / total_analyses
        
        # Adjust based on data availability
        data_quality_factors = []
        
        # Check if we have substantial data for analysis
        for analysis_name, analysis_data in analyses.items():
            if analysis_data.get('error'):
                continue
                
            if analysis_name == 'contributor_analysis':
                if analysis_data.get('total_contributors', 0) > 5:
                    data_quality_factors.append(1.0)
                else:
                    data_quality_factors.append(0.5)
            elif analysis_name == 'activity_analysis':
                if analysis_data.get('commits_analyzed', 0) > 20:
                    data_quality_factors.append(1.0)
                else:
                    data_quality_factors.append(0.7)
            else:
                data_quality_factors.append(0.8)
        
        if data_quality_factors:
            data_quality = sum(data_quality_factors) / len(data_quality_factors)
            confidence = (base_confidence * 0.6) + (data_quality * 0.4)
        else:
            confidence = base_confidence
        
        return round(min(confidence, 1.0), 2)
    
    def _identify_quality_strengths(self, quality_factors: Dict[str, float]) -> List[str]:
        """Identify quality strengths."""
        
        strengths = []
        
        if quality_factors.get('documentation', 0) >= 3:
            strengths.append('Excellent documentation')
        if quality_factors.get('license', 0) >= 2:
            strengths.append('Proper licensing')
        if quality_factors.get('community_engagement', 0) >= 2:
            strengths.append('Strong community engagement')
        if quality_factors.get('maintenance', 0) >= 1.5:
            strengths.append('Active maintenance')
        if quality_factors.get('issue_management', 0) >= 1.5:
            strengths.append('Good issue management')
        
        return strengths
    
    def _identify_improvement_areas(self, quality_factors: Dict[str, float]) -> List[str]:
        """Identify areas for improvement."""
        
        improvements = []
        
        if quality_factors.get('documentation', 0) < 2:
            improvements.append('documentation')
        if quality_factors.get('license', 0) < 1:
            improvements.append('licensing')
        if quality_factors.get('community_engagement', 0) < 1:
            improvements.append('community')
        if quality_factors.get('maintenance', 0) < 1:
            improvements.append('maintenance')
        if quality_factors.get('issue_management', 0) < 1:
            improvements.append('issue_management')
        
        return improvements


class NeuralNetworkAnalyzer:
    """Advanced neural network analysis for deeper insights."""
    
    def __init__(self, core):
        self.core = core
        self.logger = Logger("NeuralNetworkAnalyzer")
        
        if not TORCH_AVAILABLE:
            self.logger.warning("PyTorch not available for advanced neural network analysis")
    
    def deep_analysis(self, owner: str, repo: str) -> Dict[str, Any]:
        """Perform deep neural network analysis."""
        
        if not TORCH_AVAILABLE:
            return {
                'error': 'PyTorch not available',
                'message': 'Advanced neural network analysis requires PyTorch installation'
            }
        
        try:
            # Get repository data
            repo_data = self.core.get_json(f'/repos/{owner}/{repo}')
            
            # Create and use predictor
            predictor = RepoTrendPredictor()
            
            # Generate prediction
            trend_prediction = predictor.predict(repo_data)
            
            # Create synthetic training data for demonstration
            training_data = self._create_synthetic_training_data()
            
            # Train the model
            loss = predictor.train_simple(training_data)
            
            # Make prediction with trained model
            trained_prediction = predictor.predict(repo_data)
            
            return {
                'neural_network_prediction': round(trained_prediction, 4),
                'model_training_loss': round(loss, 4),
                'prediction_confidence': min(1.0 - loss, 1.0),
                'model_architecture': 'Multi-layer Perceptron',
                'features_analyzed': predictor.input_size,
                'training_samples': len(training_data)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _create_synthetic_training_data(self) -> List[Tuple[Dict[str, Any], float]]:
        """Create synthetic training data for demonstration."""
        
        training_data = []
        
        # Simulate different types of repositories
        repo_types = [
            # High-performing repos
            {'stargazers_count': 1500, 'forks_count': 200, 'open_issues_count': 15, 'has_wiki': True, 'license': {'name': 'MIT'}, 'description': 'Great project', 'created_at': '2022-01-01T00:00:00Z', 'pushed_at': '2024-01-01T00:00:00Z', 'size': 5000},
            {'stargazers_count': 800, 'forks_count': 120, 'open_issues_count': 8, 'has_wiki': True, 'license': {'name': 'Apache'}, 'description': 'Awesome tool', 'created_at': '2023-01-01T00:00:00Z', 'pushed_at': '2024-02-01T00:00:00Z', 'size': 3000},
            {'stargazers_count': 2500, 'forks_count': 300, 'open_issues_count': 25, 'has_wiki': True, 'license': {'name': 'BSD'}, 'description': 'Popular framework', 'created_at': '2021-01-01T00:00:00Z', 'pushed_at': '2024-01-15T00:00:00Z', 'size': 8000},
            
            # Medium-performing repos
            {'stargazers_count': 150, 'forks_count': 25, 'open_issues_count': 5, 'has_wiki': False, 'license': {'name': 'MIT'}, 'description': 'Useful utility', 'created_at': '2023-06-01T00:00:00Z', 'pushed_at': '2024-01-10T00:00:00Z', 'size': 1500},
            {'stargazers_count': 300, 'forks_count': 45, 'open_issues_count': 12, 'has_wiki': True, 'license': None, 'description': 'Nice project', 'created_at': '2022-08-01T00:00:00Z', 'pushed_at': '2023-12-01T00:00:00Z', 'size': 2200},
            {'stargazers_count': 75, 'forks_count': 12, 'open_issues_count': 3, 'has_wiki': False, 'license': {'name': 'GPL'}, 'description': 'Small tool', 'created_at': '2023-03-01T00:00:00Z', 'pushed_at': '2024-01-05T00:00:00Z', 'size': 800},
            
            # Low-performing repos
            {'stargazers_count': 15, 'forks_count': 2, 'open_issues_count': 1, 'has_wiki': False, 'license': None, 'description': '', 'created_at': '2023-01-01T00:00:00Z', 'pushed_at': '2023-03-01T00:00:00Z', 'size': 200},
            {'stargazers_count': 8, 'forks_count': 1, 'open_issues_count': 0, 'has_wiki': False, 'license': None, 'description': 'Test', 'created_at': '2023-10-01T00:00:00Z', 'pushed_at': '2023-11-01T00:00:00Z', 'size': 100},
            {'stargazers_count': 3, 'forks_count': 0, 'open_issues_count': 2, 'has_wiki': False, 'license': None, 'description': None, 'created_at': '2024-01-01T00:00:00Z', 'pushed_at': '2024-01-02T00:00:00Z', 'size': 50},
            {'stargazers_count': 25, 'forks_count': 3, 'open_issues_count': 8, 'has_wiki': False, 'license': None, 'description': 'Old project', 'created_at': '2020-01-01T00:00:00Z', 'pushed_at': '2022-01-01T00:00:00Z', 'size': 500},
        ]
        
        # Assign target values (0-1 scale representing success/trending potential)
        targets = [0.9, 0.8, 0.95, 0.6, 0.65, 0.5, 0.2, 0.15, 0.1, 0.25]
        
        for repo_data, target in zip(repo_types, targets):
            training_data.append((repo_data, target))
        
        return training_data


class MLPredictor:
    """Machine learning predictor for various GitHub metrics."""
    
    def __init__(self, core):
        self.core = core
        self.logger = Logger("MLPredictor")
        self.data_processor = DataProcessor()
    
    def predict_repository_metrics(self, owner: str, repo: str) -> Dict[str, MLPrediction]:
        """Predict various repository metrics using ML techniques."""
        
        try:
            repo_data = self.core.get_json(f'/repos/{owner}/{repo}')
            
            predictions = {}
            
            # Star growth prediction
            star_prediction = self._predict_star_growth(repo_data)
            predictions['star_growth'] = star_prediction
            
            # Issue resolution time prediction
            resolution_prediction = self._predict_issue_resolution_time(owner, repo)
            predictions['issue_resolution_time'] = resolution_prediction
            
            # Contributor growth prediction
            contributor_prediction = self._predict_contributor_growth(owner, repo)
            predictions['contributor_growth'] = contributor_prediction
            
            # Activity level prediction
            activity_prediction = self._predict_activity_level(repo_data)
            predictions['activity_level'] = activity_prediction
            
            return predictions
            
        except Exception as e:
            raise AIAnalysisError(f"ML prediction failed: {e}",
                                analysis_type="ml_prediction")
    
    def _predict_star_growth(self, repo_data: Dict[str, Any]) -> MLPrediction:
        """Predict star growth using historical data analysis."""
        
        current_stars = repo_data.get('stargazers_count', 0)
        
        if repo_data.get('created_at'):
            created_date = datetime.fromisoformat(repo_data['created_at'].replace('Z', '+00:00'))
            days_old = (datetime.now(created_date.tzinfo) - created_date).days
            
            if days_old > 0:
                growth_rate = current_stars / days_old
                
                # Simple linear prediction for next 30 days
                predicted_growth = growth_rate * 30
                
                # Adjust based on recent activity
                if repo_data.get('pushed_at'):
                    pushed_date = datetime.fromisoformat(repo_data['pushed_at'].replace('Z', '+00:00'))
                    days_since_update = (datetime.now(pushed_date.tzinfo) - pushed_date).days
                    
                    # Reduce prediction if not recently updated
                    if days_since_update > 30:
                        predicted_growth *= 0.5
                    elif days_since_update > 7:
                        predicted_growth *= 0.8
                
                confidence = min(current_stars / 100, 1.0)  # More confidence with more stars
                
                return MLPrediction(
                    prediction_type='star_growth_30d',
                    predicted_value=max(0, int(predicted_growth)),
                    confidence=confidence,
                    features_used=['current_stars', 'repository_age', 'recent_activity']
                )
        
        # Fallback prediction
        return MLPrediction(
            prediction_type='star_growth_30d',
            predicted_value=0,
            confidence=0.1,
            features_used=['current_stars']
        )
    
    def _predict_issue_resolution_time(self, owner: str, repo: str) -> MLPrediction:
        """Predict average issue resolution time."""
        
        try:
            # Get recent closed issues
            closed_issues = self.core.paginate(
                f'/repos/{owner}/{repo}/issues',
                params={'state': 'closed'},
                max_pages=2
            )
            
            resolution_times = []
            
            for issue in closed_issues[:20]:  # Limit to prevent too many API calls
                if issue.get('closed_at') and issue.get('created_at'):
                    created = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
                    closed = datetime.fromisoformat(issue['closed_at'].replace('Z', '+00:00'))
                    resolution_time = (closed - created).total_seconds() / 3600  # hours
                    resolution_times.append(resolution_time)
            
            if resolution_times:
                avg_resolution_time = statistics.mean(resolution_times)
                confidence = min(len(resolution_times) / 20, 1.0)
                
                return MLPrediction(
                    prediction_type='avg_issue_resolution_hours',
                    predicted_value=round(avg_resolution_time, 1),
                    confidence=confidence,
                    features_used=['historical_issue_data']
                )
            
        except Exception as e:
            pass
        
        # Default prediction
        return MLPrediction(
            prediction_type='avg_issue_resolution_hours',
            predicted_value=72.0,  # 3 days default
            confidence=0.3,
            features_used=[]
        )
    
    def _predict_contributor_growth(self, owner: str, repo: str) -> MLPrediction:
        """Predict contributor growth."""
        
        try:
            contributors = self.core.paginate(
                f'/repos/{owner}/{repo}/contributors',
                max_pages=2
            )
            
            current_contributors = len(contributors)
            
            # Simple heuristic based on repository characteristics
            repo_data = self.core.get_json(f'/repos/{owner}/{repo}')
            
            growth_factors = 0
            
            # Active repository factor
            if repo_data.get('pushed_at'):
                pushed_date = datetime.fromisoformat(repo_data['pushed_at'].replace('Z', '+00:00'))
                days_since_update = (datetime.now(pushed_date.tzinfo) - pushed_date).days
                if days_since_update <= 30:
                    growth_factors += 2
            
            # Popular repository factor
            if repo_data.get('stargazers_count', 0) > 100:
                growth_factors += 1
            
            # Open source friendliness
            if repo_data.get('license') and repo_data.get('has_issues'):
                growth_factors += 1
            
            # Predict growth percentage
            monthly_growth_rate = growth_factors * 0.05  # 5% per factor
            predicted_new_contributors = int(current_contributors * monthly_growth_rate)
            
            return MLPrediction(
                prediction_type='new_contributors_30d',
                predicted_value=max(0, predicted_new_contributors),
                confidence=min(growth_factors / 4, 0.8),
                features_used=['current_contributors', 'activity', 'popularity', 'openness']
            )
            
        except Exception as e:
            pass
        
        return MLPrediction(
            prediction_type='new_contributors_30d',
            predicted_value=0,
            confidence=0.2,
            features_used=[]
        )
    
    def _predict_activity_level(self, repo_data: Dict[str, Any]) -> MLPrediction:
        """Predict future activity level."""
        
        activity_indicators = []
        
        # Recent update indicator
        if repo_data.get('pushed_at'):
            pushed_date = datetime.fromisoformat(repo_data['pushed_at'].replace('Z', '+00:00'))
            days_since_update = (datetime.now(pushed_date.tzinfo) - pushed_date).days
            
            if days_since_update <= 7:
                activity_indicators.append(3)  # Very recent
            elif days_since_update <= 30:
                activity_indicators.append(2)  # Recent
            elif days_since_update <= 90:
                activity_indicators.append(1)  # Somewhat recent
            else:
                activity_indicators.append(0)  # Stale
        
        # Community engagement indicator
        stars = repo_data.get('stargazers_count', 0)
        forks = repo_data.get('forks_count', 0)
        open_issues = repo_data.get('open_issues_count', 0)
        
        if stars > 500 or forks > 100 or open_issues > 10:
            activity_indicators.append(2)
        elif stars > 50 or forks > 10 or open_issues > 1:
            activity_indicators.append(1)
        else:
            activity_indicators.append(0)
        
        # Calculate predicted activity level
        avg_indicator = sum(activity_indicators) / len(activity_indicators) if activity_indicators else 0
        
        if avg_indicator >= 2.5:
            predicted_level = "very_active"
        elif avg_indicator >= 2:
            predicted_level = "active"
        elif avg_indicator >= 1:
            predicted_level = "moderate"
        else:
            predicted_level = "low"
        
        return MLPrediction(
            prediction_type='activity_level_30d',
            predicted_value=predicted_level,
            confidence=min(len(activity_indicators) / 3, 0.9),
            features_used=['recent_updates', 'community_engagement']
        )
    
    def predict_future_trends(self, owner: str, repo: str) -> Dict[str, Any]:
        """Predict future trends for the repository."""
        
        try:
            repo_data = self.core.get_json(f'/repos/{owner}/{repo}')
            
            # Collect trend indicators
            trend_factors = {
                'positive_factors': [],
                'negative_factors': [],
                'neutral_factors': []
            }
            
            # Analyze recent activity
            if repo_data.get('pushed_at'):
                pushed_date = datetime.fromisoformat(repo_data['pushed_at'].replace('Z', '+00:00'))
                days_since_update = (datetime.now(pushed_date.tzinfo) - pushed_date).days
                
                if days_since_update <= 7:
                    trend_factors['positive_factors'].append('very_recent_activity')
                elif days_since_update <= 30:
                    trend_factors['positive_factors'].append('recent_activity')
                elif days_since_update <= 180:
                    trend_factors['neutral_factors'].append('moderate_activity')
                else:
                    trend_factors['negative_factors'].append('stale_activity')
            
            # Analyze community engagement
            stars = repo_data.get('stargazers_count', 0)
            forks = repo_data.get('forks_count', 0)
            
            if stars > 1000:
                trend_factors['positive_factors'].append('high_popularity')
            elif stars > 100:
                trend_factors['positive_factors'].append('moderate_popularity')
            elif stars < 10:
                trend_factors['negative_factors'].append('low_popularity')
            
            if forks > 100:
                trend_factors['positive_factors'].append('strong_fork_activity')
            elif forks < 5:
                trend_factors['negative_factors'].append('limited_fork_activity')
            
            # Analyze project health
            if repo_data.get('license'):
                trend_factors['positive_factors'].append('has_license')
            if repo_data.get('description'):
                trend_factors['positive_factors'].append('has_description')
            if repo_data.get('has_issues'):
                trend_factors['positive_factors'].append('issues_enabled')
            
            # Calculate overall trend prediction
            positive_score = len(trend_factors['positive_factors']) * 2
            negative_score = len(trend_factors['negative_factors']) * 1
            neutral_score = len(trend_factors['neutral_factors']) * 0.5
            
            total_score = positive_score - negative_score + neutral_score
            
            if total_score > 5:
                trend_prediction = 'strongly_positive'
                confidence = 0.8
            elif total_score > 2:
                trend_prediction = 'positive'
                confidence = 0.7
            elif total_score > -1:
                trend_prediction = 'stable'
                confidence = 0.6
            elif total_score > -3:
                trend_prediction = 'declining'
                confidence = 0.7
            else:
                trend_prediction = 'strongly_declining'
                confidence = 0.8
            
            return {
                'overall_trend': trend_prediction,
                'confidence': confidence,
                'trend_factors': trend_factors,
                'trend_score': total_score,
                'prediction_horizon': '3-6 months'
            }
            
        except Exception as e:
            return {'error': str(e)}


__all__ = [
    'AIAnalyzer',
    'NeuralNetworkAnalyzer',
    'MLPredictor',
    'AIInsight',
    'MLPrediction',
    'RepoTrendPredictor'
]