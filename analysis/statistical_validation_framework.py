#!/usr/bin/env python3
"""
Statistical Validation Framework for Forgetting Engine Experiments
Pharmaceutical-grade statistical analysis and validation protocols
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy.stats import ttest_ind, mannwhitneyu, chi2_contingency
import json
import os
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

class StatisticalValidator:
    """
    Pharmaceutical-grade statistical validation framework
    Following FDA clinical trial standards for computational experiments
    """
    
    def __init__(self, significance_level: float = 0.05, correction_method: str = 'bonferroni'):
        self.significance_level = significance_level
        self.correction_method = correction_method
        self.results = {}
        
    def calculate_effect_size(self, group1: np.ndarray, group2: np.ndarray) -> Dict[str, float]:
        """Calculate Cohen's d effect size with confidence intervals"""
        n1, n2 = len(group1), len(group2)
        mean1, mean2 = np.mean(group1), np.mean(group2)
        std1, std2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
        
        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
        
        # Cohen's d
        cohens_d = (mean1 - mean2) / pooled_std
        
        # Confidence interval for effect size
        se_d = np.sqrt((n1 + n2) / (n1 * n2) + cohens_d**2 / (2 * (n1 + n2)))
        ci_lower = cohens_d - 1.96 * se_d
        ci_upper = cohens_d + 1.96 * se_d
        
        return {
            'cohens_d': cohens_d,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'interpretation': self._interpret_effect_size(abs(cohens_d))
        }
    
    def _interpret_effect_size(self, d: float) -> str:
        """Interpret Cohen's d effect size"""
        if d < 0.2:
            return "negligible"
        elif d < 0.5:
            return "small"
        elif d < 0.8:
            return "medium"
        elif d < 1.2:
            return "large"
        elif d < 2.0:
            return "very large"
        else:
            return "reality-defying"
    
    def two_sample_test(self, group1: np.ndarray, group2: np.ndarray, 
                        test_type: str = 'auto') -> Dict[str, Any]:
        """Perform appropriate two-sample statistical test"""
        n1, n2 = len(group1), len(group2)
        
        # Check normality
        _, p1_normal = stats.shapiro(group1)
        _, p2_normal = stats.shapiro(group2)
        
        # Choose test based on normality and sample size
        if test_type == 'auto':
            if p1_normal > 0.05 and p2_normal > 0.05 and n1 > 30 and n2 > 30:
                test_type = 'ttest'
            else:
                test_type = 'mannwhitney'
        
        # Perform test
        if test_type == 'ttest':
            statistic, p_value = ttest_ind(group1, group2)
            test_name = "Independent t-test"
        else:
            statistic, p_value = mannwhitneyu(group1, group2, alternative='two-sided')
            test_name = "Mann-Whitney U test"
        
        # Calculate effect size
        effect_size = self.calculate_effect_size(group1, group2)
        
        # Power analysis
        power = self._calculate_power(n1, n2, effect_size['cohens_d'])
        
        return {
            'test_name': test_name,
            'statistic': statistic,
            'p_value': p_value,
            'significant': p_value < self.significance_level,
            'effect_size': effect_size,
            'power': power,
            'sample_sizes': {'group1': n1, 'group2': n2}
        }
    
    def _calculate_power(self, n1: int, n2: int, effect_size: float) -> float:
        """Calculate statistical power (simplified)"""
        # Simplified power calculation
        n_harmonic = 2 * n1 * n2 / (n1 + n2)
        ncp = effect_size * np.sqrt(n_harmonic / 2)
        alpha = self.significance_level
        
        # Critical value for two-tailed test
        z_critical = stats.norm.ppf(1 - alpha/2)
        
        # Power calculation
        power = 1 - stats.norm.cdf(z_critical - ncp) + stats.norm.cdf(-z_critical - ncp)
        
        return max(0, min(1, power))
    
    def proportion_test(self, successes1: int, n1: int, successes2: int, n2: int) -> Dict[str, Any]:
        """Two-proportion z-test"""
        p1 = successes1 / n1
        p2 = successes2 / n2
        p_pooled = (successes1 + successes2) / (n1 + n2)
        
        # Standard error
        se = np.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))
        
        # Z-statistic
        z_stat = (p1 - p2) / se
        
        # Two-tailed p-value
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
        
        # Effect size (Cohen's h)
        cohens_h = 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))
        
        # Odds ratio
        odds_ratio = (p1 / (1 - p1)) / (p2 / (1 - p2))
        
        return {
            'test_name': 'Two-proportion z-test',
            'z_statistic': z_stat,
            'p_value': p_value,
            'significant': p_value < self.significance_level,
            'proportions': {'group1': p1, 'group2': p2},
            'cohens_h': cohens_h,
            'odds_ratio': odds_ratio,
            'sample_sizes': {'group1': n1, 'group2': n2}
        }
    
    def multiple_testing_correction(self, p_values: List[float]) -> List[float]:
        """Apply multiple testing correction"""
        p_values = np.array(p_values)
        
        if self.correction_method == 'bonferroni':
            corrected = p_values * len(p_values)
            corrected = np.minimum(corrected, 1.0)
        elif self.correction_method == 'fdr':
            # Benjamini-Hochberg procedure
            ranks = stats.rankdata(p_values)
            corrected = p_values * len(p_values) / ranks
            corrected = np.minimum(corrected, 1.0)
        else:
            corrected = p_values
        
        return corrected.tolist()
    
    def bootstrap_confidence_interval(self, data: np.ndarray, statistic_func, 
                                    n_bootstrap: int = 10000, ci_level: float = 0.95) -> Tuple[float, float]:
        """Bootstrap confidence interval"""
        bootstrap_stats = []
        n = len(data)
        
        for _ in range(n_bootstrap):
            bootstrap_sample = np.random.choice(data, n, replace=True)
            bootstrap_stats.append(statistic_func(bootstrap_sample))
        
        bootstrap_stats = np.array(bootstrap_stats)
        alpha = 1 - ci_level
        lower = np.percentile(bootstrap_stats, 100 * alpha / 2)
        upper = np.percentile(bootstrap_stats, 100 * (1 - alpha / 2))
        
        return lower, upper
    
    def validate_reproducibility(self, results1: np.ndarray, results2: np.ndarray, 
                                tolerance: float = 1e-10) -> Dict[str, Any]:
        """Validate reproducibility between two sets of results"""
        # Check if results are identical within tolerance
        differences = np.abs(results1 - results2)
        max_diff = np.max(differences)
        mean_diff = np.mean(differences)
        
        # Correlation analysis
        correlation = np.corrcoef(results1, results2)[0, 1]
        
        # Bland-Altman analysis
        mean_values = (results1 + results2) / 2
        differences = results1 - results2
        bias = np.mean(differences)
        limits_of_agreement = [bias - 1.96 * np.std(differences), bias + 1.96 * np.std(differences)]
        
        return {
            'reproducible': max_diff < tolerance,
            'max_difference': max_diff,
            'mean_difference': mean_diff,
            'correlation': correlation,
            'bias': bias,
            'limits_of_agreement': limits_of_agreement,
            'tolerance': tolerance
        }
    
    def analyze_domain_results(self, domain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete statistical analysis for a single domain"""
        results = {}
        
        # Extract data
        baseline_data = np.array(domain_data['baseline_results'])
        fe_data = np.array(domain_data['fe_results'])
        
        # Basic statistics
        results['baseline_stats'] = {
            'mean': np.mean(baseline_data),
            'std': np.std(baseline_data, ddof=1),
            'n': len(baseline_data)
        }
        
        results['fe_stats'] = {
            'mean': np.mean(fe_data),
            'std': np.std(fe_data, ddof=1),
            'n': len(fe_data)
        }
        
        # Statistical test
        test_results = self.two_sample_test(fe_data, baseline_data)
        results['statistical_test'] = test_results
        
        # Improvement calculation
        improvement = (results['baseline_stats']['mean'] - results['fe_stats']['mean']) / results['baseline_stats']['mean'] * 100
        results['improvement_percentage'] = improvement
        
        # Confidence intervals
        baseline_ci = self.bootstrap_confidence_interval(baseline_data, np.mean)
        fe_ci = self.bootstrap_confidence_interval(fe_data, np.mean)
        
        results['baseline_ci'] = {'lower': baseline_ci[0], 'upper': baseline_ci[1]}
        results['fe_ci'] = {'lower': fe_ci[0], 'upper': fe_ci[1]}
        
        return results
    
    def generate_validation_report(self, all_domains: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        report = {
            'validation_date': '2026-02-17',
            'validator_version': '1.0',
            'significance_level': self.significance_level,
            'correction_method': self.correction_method,
            'domains_analyzed': len(all_domains),
            'domain_results': {},
            'summary_statistics': {},
            'cross_domain_analysis': {}
        }
        
        # Analyze each domain
        p_values = []
        effect_sizes = []
        
        for domain_name, domain_data in all_domains.items():
            domain_results = self.analyze_domain_results(domain_data)
            report['domain_results'][domain_name] = domain_results
            
            p_values.append(domain_results['statistical_test']['p_value'])
            effect_sizes.append(abs(domain_results['statistical_test']['effect_size']['cohens_d']))
        
        # Multiple testing correction
        corrected_p_values = self.multiple_testing_correction(p_values)
        
        # Update domain results with corrected p-values
        for i, domain_name in enumerate(report['domain_results']):
            report['domain_results'][domain_name]['statistical_test']['corrected_p_value'] = corrected_p_values[i]
            report['domain_results'][domain_name]['statistical_test']['significant_corrected'] = corrected_p_values[i] < self.significance_level
        
        # Summary statistics
        report['summary_statistics'] = {
            'significant_domains': sum(1 for p in corrected_p_values if p < self.significance_level),
            'total_domains': len(all_domains),
            'average_effect_size': np.mean(effect_sizes),
            'min_effect_size': np.min(effect_sizes),
            'max_effect_size': np.max(effect_sizes),
            'significant_effect_sizes': [effect_sizes[i] for i, p in enumerate(corrected_p_values) if p < self.significance_level]
        }
        
        # Cross-domain analysis
        report['cross_domain_analysis'] = {
            'universal_superiority': all(corrected_p_values[i] < self.significance_level for i, p in enumerate(corrected_p_values)),
            'effect_size_consistency': np.std(effect_sizes) < 0.5,
            'statistical_power': np.mean([domain['statistical_test']['power'] for domain in report['domain_results'].values()])
        }
        
        return report


def main():
    """Example usage of the statistical validation framework"""
    validator = StatisticalValidator(significance_level=0.05, correction_method='bonferroni')
    
    # Example domain data (replace with actual data)
    example_domain = {
        'baseline_results': [1.0, 1.2, 0.9, 1.1, 1.3, 0.8, 1.0, 1.2],
        'fe_results': [0.7, 0.8, 0.6, 0.75, 0.85, 0.65, 0.7, 0.8]
    }
    
    # Analyze single domain
    results = validator.analyze_domain_results(example_domain)
    print("Single Domain Analysis:")
    print(json.dumps(results, indent=2))
    
    # Generate comprehensive report
    all_domains = {
        'protein_folding_2d': example_domain,
        'protein_folding_3d': example_domain,
        'traveling_salesman': example_domain
    }
    
    report = validator.generate_validation_report(all_domains)
    print("\nComprehensive Validation Report:")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
