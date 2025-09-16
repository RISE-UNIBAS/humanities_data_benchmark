# Cost Tracking Strategy for Humanities Data Benchmark

This document outlines a comprehensive cost tracking strategy for monitoring and analyzing the financial aspects of running AI model benchmarks. Created by Claude Code on 2025-09-16.

## Table of Contents
- [Overview](#overview)
- [Cost Components](#cost-components)
- [Tracking Architecture](#tracking-architecture)
- [Implementation Strategy](#implementation-strategy)
- [Cost Analysis Features](#cost-analysis-features)
- [Reporting and Visualization](#reporting-and-visualization)
- [Budget Management](#budget-management)

## Overview

Cost tracking is critical for:
- **Research Budget Planning** - Understanding true costs of benchmark evaluations
- **Model Comparison** - Cost-effectiveness analysis across different providers/models
- **Resource Optimization** - Identifying expensive operations and optimizing them
- **Grant Reporting** - Accurate financial reporting for funded research
- **Scaling Decisions** - Cost projections for larger benchmark suites

## Cost Components

### 1. API Usage Costs
The primary cost driver for most providers:

#### Token-Based Pricing (OpenAI, Anthropic)
```python
@dataclass
class TokenCost:
    input_tokens: int
    output_tokens: int
    input_cost_per_1k: float
    output_cost_per_1k: float
    total_cost: float
    
    def calculate_total(self) -> float:
        input_cost = (self.input_tokens / 1000) * self.input_cost_per_1k
        output_cost = (self.output_tokens / 1000) * self.output_cost_per_1k
        return input_cost + output_cost
```

#### Request-Based Pricing (Google Gemini)
```python
@dataclass
class RequestCost:
    num_requests: int
    images_per_request: int
    cost_per_request: float
    cost_per_image: float
    total_cost: float
```

#### Subscription-Based Models
```python
@dataclass
class SubscriptionCost:
    monthly_fee: float
    usage_period_days: int
    requests_made: int
    allocated_cost: float  # Portion attributed to this benchmark
```

### 2. Infrastructure Costs
For local model deployments or cloud computing:

```python
@dataclass
class InfrastructureCost:
    compute_hours: float
    cost_per_hour: float
    storage_gb: float
    storage_cost_per_gb: float
    bandwidth_gb: float
    bandwidth_cost: float
    total_cost: float
```

### 3. Development and Maintenance Costs
Human time and resources:

```python
@dataclass
class DevelopmentCost:
    researcher_hours: float
    developer_hours: float
    hourly_rate: float
    total_labor_cost: float
```

## Tracking Architecture

### 1. Cost Collector Interface
Base class for all cost tracking implementations:

```python
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional

class CostCollector(ABC):
    """Base interface for cost tracking implementations"""
    
    @abstractmethod
    def track_request(self, 
                     provider: str,
                     model: str, 
                     benchmark_name: str,
                     image_count: int,
                     prompt_tokens: int,
                     completion_tokens: int,
                     request_metadata: Dict[str, Any]) -> str:
        """Track a single API request and return cost_id"""
        pass
    
    @abstractmethod
    def finalize_benchmark_run(self, 
                              benchmark_id: str,
                              total_requests: int,
                              total_cost: float,
                              metadata: Dict[str, Any]) -> None:
        """Record final benchmark run costs"""
        pass
    
    @abstractmethod
    def get_costs(self, 
                 start_date: datetime,
                 end_date: datetime,
                 filters: Optional[Dict[str, str]] = None) -> List[Dict]:
        """Retrieve cost data for analysis"""
        pass
```

### 2. Provider-Specific Cost Trackers

#### OpenAI Cost Tracker
```python
class OpenAICostTracker(CostCollector):
    # Current OpenAI pricing (as of 2025-09-16)
    PRICING = {
        'gpt-4o': {
            'input': 0.0025,   # per 1K tokens
            'output': 0.010,   # per 1K tokens
        },
        'gpt-4o-mini': {
            'input': 0.000150, # per 1K tokens  
            'output': 0.000600, # per 1K tokens
        }
        # Add other models...
    }
    
    def track_request(self, provider, model, benchmark_name, 
                     image_count, prompt_tokens, completion_tokens, 
                     request_metadata):
        pricing = self.PRICING.get(model, {})
        
        input_cost = (prompt_tokens / 1000) * pricing.get('input', 0)
        output_cost = (completion_tokens / 1000) * pricing.get('output', 0)
        total_cost = input_cost + output_cost
        
        cost_record = {
            'timestamp': datetime.now(),
            'provider': provider,
            'model': model,
            'benchmark': benchmark_name,
            'image_count': image_count,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost,
            'metadata': request_metadata
        }
        
        return self._store_cost_record(cost_record)
```

#### Anthropic Cost Tracker
```python
class AnthropicCostTracker(CostCollector):
    PRICING = {
        'claude-3-5-sonnet-20241022': {
            'input': 0.003,    # per 1K tokens
            'output': 0.015,   # per 1K tokens
        },
        'claude-3-5-haiku-20241022': {
            'input': 0.00025,  # per 1K tokens
            'output': 0.00125, # per 1K tokens
        }
        # Add other models...
    }
    
    def track_request(self, provider, model, benchmark_name,
                     image_count, prompt_tokens, completion_tokens,
                     request_metadata):
        # Similar implementation to OpenAI
        # Handle Anthropic-specific pricing structure
        pass
```

### 3. Cost Database Schema

```sql
-- Cost tracking database schema
CREATE TABLE benchmark_runs (
    id UUID PRIMARY KEY,
    benchmark_name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    total_images INTEGER,
    total_requests INTEGER,
    total_cost DECIMAL(10,4),
    status VARCHAR(20) DEFAULT 'running',
    metadata JSONB
);

CREATE TABLE request_costs (
    id UUID PRIMARY KEY,
    benchmark_run_id UUID REFERENCES benchmark_runs(id),
    timestamp TIMESTAMP NOT NULL,
    image_name VARCHAR(255),
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    input_cost DECIMAL(10,6),
    output_cost DECIMAL(10,6),
    total_cost DECIMAL(10,6),
    request_metadata JSONB
);

CREATE TABLE pricing_history (
    id UUID PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    effective_date DATE NOT NULL,
    input_price_per_1k DECIMAL(10,6),
    output_price_per_1k DECIMAL(10,6),
    request_price DECIMAL(10,6),
    notes TEXT
);
```

## Implementation Strategy

### 1. Integration with Benchmark Base Class

```python
class Benchmark(ABC):
    def __init__(self, config, api_key, benchmark_directory, date=None):
        # Existing initialization...
        self.cost_tracker = self._initialize_cost_tracker()
        self.benchmark_run_id = None
    
    def _initialize_cost_tracker(self):
        """Initialize appropriate cost tracker for provider"""
        trackers = {
            'openai': OpenAICostTracker(),
            'anthropic': AnthropicCostTracker(),
            'genai': GeminiCostTracker(),
            'mistral': MistralCostTracker()
        }
        return trackers.get(self.provider)
    
    def run(self):
        """Enhanced run method with cost tracking"""
        # Start benchmark run tracking
        self.benchmark_run_id = self.cost_tracker.start_benchmark_run(
            benchmark_name=self.name,
            provider=self.provider,
            model=self.model,
            total_images=len(self.get_all_images())
        )
        
        try:
            # Existing benchmark logic...
            results = self._execute_benchmark()
            
            # Finalize cost tracking
            self.cost_tracker.finalize_benchmark_run(
                self.benchmark_run_id,
                results['total_requests'],
                results['total_cost'],
                results['metadata']
            )
            
            return results
        
        except Exception as e:
            self.cost_tracker.mark_benchmark_failed(self.benchmark_run_id, str(e))
            raise
    
    def query_model(self, images, prompt):
        """Enhanced model query with cost tracking"""
        start_time = time.time()
        
        # Make API request
        response = self.client.query(images, prompt)
        
        # Track costs
        if self.cost_tracker:
            self.cost_tracker.track_request(
                provider=self.provider,
                model=self.model,
                benchmark_name=self.name,
                image_count=len(images),
                prompt_tokens=response.get('usage', {}).get('prompt_tokens', 0),
                completion_tokens=response.get('usage', {}).get('completion_tokens', 0),
                request_metadata={
                    'response_time': time.time() - start_time,
                    'image_names': [img.name for img in images],
                    'prompt_length': len(prompt)
                }
            )
        
        return response
```

### 2. Cost Estimation Engine

```python
class CostEstimator:
    """Estimate costs before running benchmarks"""
    
    def __init__(self, pricing_config: Dict):
        self.pricing = pricing_config
    
    def estimate_benchmark_cost(self, 
                               benchmark_name: str,
                               provider: str, 
                               model: str,
                               num_images: int,
                               avg_prompt_tokens: int = None,
                               avg_completion_tokens: int = None) -> Dict:
        """Estimate total cost for a benchmark run"""
        
        # Load benchmark-specific estimates if not provided
        if not avg_prompt_tokens:
            avg_prompt_tokens = self._estimate_prompt_tokens(benchmark_name)
        if not avg_completion_tokens:
            avg_completion_tokens = self._estimate_completion_tokens(benchmark_name)
        
        pricing = self.pricing[provider][model]
        
        total_prompt_tokens = num_images * avg_prompt_tokens
        total_completion_tokens = num_images * avg_completion_tokens
        
        input_cost = (total_prompt_tokens / 1000) * pricing['input']
        output_cost = (total_completion_tokens / 1000) * pricing['output']
        total_cost = input_cost + output_cost
        
        return {
            'benchmark': benchmark_name,
            'provider': provider,
            'model': model,
            'num_images': num_images,
            'estimated_prompt_tokens': total_prompt_tokens,
            'estimated_completion_tokens': total_completion_tokens,
            'estimated_input_cost': input_cost,
            'estimated_output_cost': output_cost,
            'estimated_total_cost': total_cost,
            'cost_per_image': total_cost / num_images
        }
    
    def compare_models(self, benchmark_name: str, models: List[Tuple[str, str]]):
        """Compare estimated costs across multiple models"""
        num_images = self._get_benchmark_image_count(benchmark_name)
        
        estimates = []
        for provider, model in models:
            estimate = self.estimate_benchmark_cost(
                benchmark_name, provider, model, num_images
            )
            estimates.append(estimate)
        
        # Sort by cost
        estimates.sort(key=lambda x: x['estimated_total_cost'])
        
        return estimates
```

## Cost Analysis Features

### 1. Real-Time Cost Monitoring

```python
class CostMonitor:
    """Real-time cost monitoring during benchmark runs"""
    
    def __init__(self, budget_limit: float = None):
        self.budget_limit = budget_limit
        self.current_costs = {}
        self.alerts = []
    
    def check_budget(self, benchmark_run_id: str) -> Dict:
        """Check if benchmark is within budget limits"""
        current_cost = self._get_current_cost(benchmark_run_id)
        
        if self.budget_limit and current_cost > self.budget_limit:
            return {
                'status': 'OVER_BUDGET',
                'current_cost': current_cost,
                'budget_limit': self.budget_limit,
                'overage': current_cost - self.budget_limit
            }
        
        warning_threshold = self.budget_limit * 0.8 if self.budget_limit else None
        if warning_threshold and current_cost > warning_threshold:
            return {
                'status': 'APPROACHING_LIMIT',
                'current_cost': current_cost,
                'budget_limit': self.budget_limit,
                'percentage_used': (current_cost / self.budget_limit) * 100
            }
        
        return {
            'status': 'OK',
            'current_cost': current_cost,
            'budget_limit': self.budget_limit
        }
```

### 2. Cost Breakdown Analysis

```python
class CostAnalyzer:
    """Analyze cost patterns and trends"""
    
    def analyze_benchmark_costs(self, benchmark_name: str, 
                               date_range: Tuple[datetime, datetime]) -> Dict:
        """Comprehensive cost analysis for a benchmark"""
        
        costs = self.cost_tracker.get_costs(
            start_date=date_range[0],
            end_date=date_range[1],
            filters={'benchmark': benchmark_name}
        )
        
        return {
            'total_cost': sum(c['total_cost'] for c in costs),
            'total_runs': len(set(c['benchmark_run_id'] for c in costs)),
            'average_cost_per_run': self._calculate_avg_cost_per_run(costs),
            'cost_per_image': self._calculate_cost_per_image(costs),
            'token_efficiency': self._analyze_token_efficiency(costs),
            'cost_breakdown_by_model': self._breakdown_by_model(costs),
            'cost_trends': self._analyze_cost_trends(costs),
            'optimization_suggestions': self._suggest_optimizations(costs)
        }
    
    def compare_models_actual_costs(self, benchmark_name: str,
                                   models: List[Tuple[str, str]]) -> Dict:
        """Compare actual costs across models for same benchmark"""
        
        comparisons = {}
        
        for provider, model in models:
            costs = self.cost_tracker.get_costs(
                filters={
                    'benchmark': benchmark_name,
                    'provider': provider,
                    'model': model
                }
            )
            
            if costs:
                comparisons[f"{provider}/{model}"] = {
                    'total_cost': sum(c['total_cost'] for c in costs),
                    'avg_cost_per_image': self._calculate_cost_per_image(costs),
                    'token_efficiency': self._calculate_token_efficiency(costs),
                    'total_runs': len(costs)
                }
        
        # Rank by cost effectiveness
        ranked = sorted(
            comparisons.items(),
            key=lambda x: x[1]['avg_cost_per_image']
        )
        
        return {
            'model_comparison': dict(ranked),
            'most_cost_effective': ranked[0][0] if ranked else None,
            'cost_savings_analysis': self._calculate_savings_potential(ranked)
        }
```

## Reporting and Visualization

### 1. Cost Reports

```python
class CostReporter:
    """Generate cost reports and visualizations"""
    
    def generate_monthly_report(self, year: int, month: int) -> Dict:
        """Generate comprehensive monthly cost report"""
        
        start_date = datetime(year, month, 1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        costs = self.cost_tracker.get_costs(start_date, end_date)
        
        return {
            'period': f"{year}-{month:02d}",
            'total_cost': sum(c['total_cost'] for c in costs),
            'total_requests': len(costs),
            'breakdown_by_benchmark': self._breakdown_by_benchmark(costs),
            'breakdown_by_provider': self._breakdown_by_provider(costs),
            'breakdown_by_model': self._breakdown_by_model(costs),
            'daily_costs': self._calculate_daily_costs(costs),
            'trends': self._analyze_monthly_trends(costs),
            'top_expensive_runs': self._get_top_expensive_runs(costs, limit=10)
        }
    
    def generate_cost_dashboard_data(self) -> Dict:
        """Generate data for real-time cost dashboard"""
        
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        return {
            'today_total': self._get_daily_total(today),
            'week_total': self._get_period_total(week_ago, today),
            'month_total': self._get_period_total(month_ago, today),
            'active_runs': self._get_active_benchmark_runs(),
            'recent_expensive_runs': self._get_recent_expensive_runs(limit=5),
            'cost_trend_7_days': self._get_daily_trend(7),
            'budget_status': self._get_budget_status(),
            'model_usage_distribution': self._get_model_usage_stats()
        }
```

### 2. Visualization Components

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class CostVisualizer:
    """Create cost visualization charts"""
    
    def plot_cost_trends(self, costs: List[Dict], save_path: str = None):
        """Plot cost trends over time"""
        df = pd.DataFrame(costs)
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily_costs = df.groupby('date')['total_cost'].sum()
        
        plt.figure(figsize=(12, 6))
        plt.plot(daily_costs.index, daily_costs.values, marker='o')
        plt.title('Daily Cost Trends')
        plt.xlabel('Date')
        plt.ylabel('Total Cost ($)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        plt.show()
    
    def plot_model_comparison(self, comparison_data: Dict, save_path: str = None):
        """Plot cost comparison across models"""
        models = list(comparison_data.keys())
        costs = [data['avg_cost_per_image'] for data in comparison_data.values()]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(models, costs)
        plt.title('Average Cost per Image by Model')
        plt.xlabel('Model')
        plt.ylabel('Cost per Image ($)')
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for bar, cost in zip(bars, costs):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                    f'${cost:.4f}', ha='center', va='bottom')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path)
        plt.show()
    
    def plot_benchmark_cost_breakdown(self, costs_by_benchmark: Dict, save_path: str = None):
        """Plot cost breakdown by benchmark"""
        plt.figure(figsize=(10, 8))
        
        benchmarks = list(costs_by_benchmark.keys())
        costs = list(costs_by_benchmark.values())
        
        plt.pie(costs, labels=benchmarks, autopct='%1.1f%%', startangle=90)
        plt.title('Cost Distribution by Benchmark')
        plt.axis('equal')
        
        if save_path:
            plt.savefig(save_path)
        plt.show()
```

## Budget Management

### 1. Budget Controls

```python
class BudgetManager:
    """Manage budgets and spending limits"""
    
    def __init__(self, database_connection):
        self.db = database_connection
        self.budgets = self._load_budgets()
    
    def set_budget(self, 
                   budget_type: str,  # 'monthly', 'project', 'benchmark'
                   identifier: str,   # month, project_name, benchmark_name
                   amount: float,
                   alert_threshold: float = 0.8):
        """Set budget limit with alert threshold"""
        
        budget = {
            'type': budget_type,
            'identifier': identifier,
            'amount': amount,
            'alert_threshold': alert_threshold,
            'created_date': datetime.now()
        }
        
        self._store_budget(budget)
        self.budgets[f"{budget_type}:{identifier}"] = budget
    
    def check_budget_status(self, budget_type: str, identifier: str) -> Dict:
        """Check current spending against budget"""
        
        budget_key = f"{budget_type}:{identifier}"
        budget = self.budgets.get(budget_key)
        
        if not budget:
            return {'status': 'NO_BUDGET_SET'}
        
        current_spending = self._get_current_spending(budget_type, identifier)
        usage_percentage = (current_spending / budget['amount']) * 100
        
        if current_spending > budget['amount']:
            status = 'OVER_BUDGET'
        elif current_spending > budget['amount'] * budget['alert_threshold']:
            status = 'ALERT_THRESHOLD_EXCEEDED'
        else:
            status = 'OK'
        
        return {
            'status': status,
            'budget_amount': budget['amount'],
            'current_spending': current_spending,
            'remaining_budget': budget['amount'] - current_spending,
            'usage_percentage': usage_percentage,
            'alert_threshold': budget['alert_threshold']
        }
    
    def get_spending_projection(self, budget_type: str, identifier: str) -> Dict:
        """Project spending based on current trends"""
        
        historical_data = self._get_historical_spending(budget_type, identifier)
        
        if len(historical_data) < 7:  # Need at least a week of data
            return {'status': 'INSUFFICIENT_DATA'}
        
        # Calculate daily average spending
        daily_avg = sum(historical_data[-7:]) / 7
        
        # Project to end of period
        if budget_type == 'monthly':
            days_remaining = self._get_days_remaining_in_month()
            projected_total = sum(historical_data) + (daily_avg * days_remaining)
        else:
            # For project budgets, use different projection logic
            projected_total = self._project_for_project_budget(historical_data, daily_avg)
        
        budget = self.budgets.get(f"{budget_type}:{identifier}")
        budget_amount = budget['amount'] if budget else None
        
        return {
            'current_spending': sum(historical_data),
            'daily_average': daily_avg,
            'projected_total': projected_total,
            'budget_amount': budget_amount,
            'projected_overrun': max(0, projected_total - budget_amount) if budget_amount else 0,
            'recommendation': self._get_spending_recommendation(projected_total, budget_amount)
        }
```

### 2. Cost Alerts and Notifications

```python
class CostAlertManager:
    """Manage cost alerts and notifications"""
    
    def __init__(self, notification_config: Dict):
        self.notifications = notification_config
        self.alert_rules = []
    
    def add_alert_rule(self, 
                       name: str,
                       condition: Dict,
                       action: str,
                       recipients: List[str]):
        """Add custom alert rule"""
        
        rule = {
            'name': name,
            'condition': condition,
            'action': action,
            'recipients': recipients,
            'created_date': datetime.now(),
            'last_triggered': None
        }
        
        self.alert_rules.append(rule)
    
    def check_alerts(self):
        """Check all alert conditions and trigger notifications"""
        
        for rule in self.alert_rules:
            if self._evaluate_condition(rule['condition']):
                self._trigger_alert(rule)
                rule['last_triggered'] = datetime.now()
    
    def _evaluate_condition(self, condition: Dict) -> bool:
        """Evaluate alert condition"""
        
        condition_type = condition['type']
        
        if condition_type == 'budget_exceeded':
            budget_status = self.budget_manager.check_budget_status(
                condition['budget_type'], 
                condition['identifier']
            )
            return budget_status['status'] in ['OVER_BUDGET', 'ALERT_THRESHOLD_EXCEEDED']
        
        elif condition_type == 'cost_spike':
            current_daily_cost = self._get_daily_cost(datetime.now().date())
            avg_daily_cost = self._get_average_daily_cost(days=7)
            return current_daily_cost > avg_daily_cost * condition['spike_multiplier']
        
        elif condition_type == 'expensive_request':
            recent_requests = self._get_recent_requests(hours=1)
            return any(req['cost'] > condition['cost_threshold'] for req in recent_requests)
        
        return False
    
    def _trigger_alert(self, rule: Dict):
        """Trigger alert notification"""
        
        message = self._format_alert_message(rule)
        
        if rule['action'] == 'email':
            self._send_email_alert(rule['recipients'], message)
        elif rule['action'] == 'slack':
            self._send_slack_alert(message)
        elif rule['action'] == 'log':
            logging.warning(f"COST_ALERT: {message}")
```

This comprehensive cost tracking strategy provides:

1. **Real-time cost monitoring** during benchmark runs
2. **Detailed cost analysis** and optimization suggestions  
3. **Budget management** with alerts and projections
4. **Visual reporting** for stakeholders
5. **Historical cost tracking** for trend analysis
6. **Multi-provider support** with provider-specific pricing models

The system is designed to integrate seamlessly with the existing benchmark framework while providing the financial visibility needed for research project management.