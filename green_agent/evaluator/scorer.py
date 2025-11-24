"""Scoring logic for bug fixes"""
from typing import Dict, List
from dataclasses import dataclass
import time

@dataclass
class FixScore:
    """Score for a bug fix attempt"""
    bug_id: str
    language: str
    correctness: float  # 0-1: Did tests pass?
    code_quality: float  # 0-1: Code quality score
    efficiency: float  # 0-1: Time efficiency
    minimal_change: float  # 0-1: Minimal changes
    total_score: float  # Weighted total
    details: Dict

class Scorer:
    def __init__(self, config: Dict):
        self.weights = config.get('scoring', {
            'correctness': 0.50,
            'code_quality': 0.20,
            'efficiency': 0.15,
            'minimal_change': 0.15
        })
        self.timeout = config.get('timeout_per_bug', 600)
    
    def score_fix(self, 
                  bug_info: Dict,
                  fix_result: Dict,
                  time_taken: float,
                  patch_size: int) -> FixScore:
        """Score a bug fix attempt
        
        Args:
            bug_info: Information about the bug
            fix_result: Result from running tests
            time_taken: Time taken to generate fix (seconds)
            patch_size: Number of lines changed
        """
        
        # 1. Correctness (50%): Did all tests pass?
        correctness = 1.0 if fix_result.get('success', False) else 0.0
        
        # If tests didn't pass, check partial credit
        if not correctness and 'failing_tests' in fix_result:
            total_tests = fix_result.get('total_tests', 1)
            failing_tests = len(fix_result['failing_tests'])
            passing_tests = total_tests - failing_tests
            correctness = max(0, passing_tests / total_tests) * 0.5  # Max 50% for partial
        
        # 2. Code Quality (20%): Based on patch characteristics
        # Simple heuristic: fewer complex changes = better
        code_quality = self._score_code_quality(patch_size)
        
        # 3. Efficiency (15%): Time taken
        efficiency = self._score_efficiency(time_taken)
        
        # 4. Minimal Change (15%): Smaller patches are better
        minimal_change = self._score_minimal_change(patch_size)
        
        # Calculate weighted total
        total_score = (
            correctness * self.weights['correctness'] +
            code_quality * self.weights['code_quality'] +
            efficiency * self.weights['efficiency'] +
            minimal_change * self.weights['minimal_change']
        )
        
        return FixScore(
            bug_id=f"{bug_info['project']}_{bug_info['bug_id']}",
            language=bug_info['language'],
            correctness=correctness,
            code_quality=code_quality,
            efficiency=efficiency,
            minimal_change=minimal_change,
            total_score=total_score,
            details={
                'time_taken': time_taken,
                'patch_size': patch_size,
                'tests_passed': fix_result.get('success', False),
                'timeout': time_taken >= self.timeout
            }
        )
    
    def _score_code_quality(self, patch_size: int) -> float:
        """Score code quality based on patch characteristics"""
        # Simple heuristic: prefer smaller, focused changes
        if patch_size == 0:
            return 0.0
        elif patch_size <= 5:
            return 1.0
        elif patch_size <= 20:
            return 0.8
        elif patch_size <= 50:
            return 0.6
        else:
            return 0.4
    
    def _score_efficiency(self, time_taken: float) -> float:
        """Score based on time taken (faster is better)"""
        if time_taken >= self.timeout:
            return 0.0  # Timed out
        
        # Scale: < 1min = 1.0, 5min = 0.5, timeout = 0.0
        ratio = time_taken / self.timeout
        return max(0.0, 1.0 - ratio)
    
    def _score_minimal_change(self, patch_size: int) -> float:
        """Score based on patch size (smaller is better)"""
        if patch_size == 0:
            return 0.0
        elif patch_size == 1:
            return 1.0  # Single line fix
        elif patch_size <= 5:
            return 0.9
        elif patch_size <= 10:
            return 0.7
        elif patch_size <= 20:
            return 0.5
        else:
            return max(0.1, 1.0 - (patch_size / 100))
    
    def aggregate_scores(self, scores: List[FixScore]) -> Dict:
        """Aggregate scores across multiple bugs"""
        if not scores:
            return {
                'total_bugs': 0,
                'bugs_fixed': 0,
                'average_score': 0.0,
                'by_language': {}
            }
        
        total_bugs = len(scores)
        bugs_fixed = sum(1 for s in scores if s.correctness >= 0.99)
        average_score = sum(s.total_score for s in scores) / total_bugs
        
        # Group by language
        by_language = {}
        for score in scores:
            lang = score.language
            if lang not in by_language:
                by_language[lang] = {
                    'count': 0,
                    'fixed': 0,
                    'average_score': 0.0,
                    'scores': []
                }
            by_language[lang]['count'] += 1
            by_language[lang]['scores'].append(score.total_score)
            if score.correctness >= 0.99:
                by_language[lang]['fixed'] += 1
        
        # Calculate averages
        for lang in by_language:
            scores_list = by_language[lang]['scores']
            by_language[lang]['average_score'] = sum(scores_list) / len(scores_list)
            del by_language[lang]['scores']  # Remove raw scores
        
        return {
            'total_bugs': total_bugs,
            'bugs_fixed': bugs_fixed,
            'fix_rate': bugs_fixed / total_bugs if total_bugs > 0 else 0.0,
            'average_score': average_score,
            'by_language': by_language
        }
