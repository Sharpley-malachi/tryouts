from agents.ingestor import IngestionAgent
from agents.normalizer import NormalizationAgent
from agents.deduplicator import DeduplicationAgent
from agents.context_evaluator import ContextEvaluator
from agents.scorer import ScorerAgent
from core_types import Trend
from datetime import datetime
import config

def main():
    print("AI #2: Strategy Interpretation Engine Initialized")
    print("===============================================")
    
    # 1. Ingestion
    ingestor = IngestionAgent("knowledge_base")
    raw_strategies = ingestor.load_strategies()
    print(f"Loaded {len(raw_strategies)} raw strategies.")
    
    # 2. Normalization
    normalizer = NormalizationAgent()
    normalized_strategies = [normalizer.normalize(s) for s in raw_strategies]
    print(f"Normalized {len(normalized_strategies)} strategies.")
    
    # 3. De-Duplication
    deduplicator = DeduplicationAgent()
    unique_strategies = deduplicator.process(normalized_strategies)
    print(f"Unique Logic Profiles remaining: {len(unique_strategies)}")
    
    # 4. Mock Market Data (Would come from AI #1)
    # Scenario: It is 3 AM (London Open), Trend is Mixed
    mock_market_state = {
        "current_time": datetime(2025, 12, 18, 3, 30), # 3:30 AM
        "htf_trend": Trend.BULLISH,
        "ltf_trend": Trend.BEARISH # Divergence
    }
    
    # 5. Context Evaluation
    evaluator = ContextEvaluator()
    scores = {}
    print("\n--- Context Evaluation ---")
    for strat in unique_strategies:
        score = evaluator.check_market_conditions(strat, mock_market_state)
        scores[strat.strategy_id] = score
        print(f"Strategy {strat.strategy_id} ({strat.original_name}) Context Score: {score:.2f}")

    # 6. Final Scoring & Conflict Check
    scorer = ScorerAgent()
    final_report = scorer.evaluate_batch(unique_strategies, scores)
    
    print("\n--- FINAL STRATEGY EVALUATION REPORT ---")
    for report in final_report:
        status = " ACTIVE" if report.is_applicable else " INACTIVE"
        print(f"[{status}] Strategy: {report.strategy_id}")
        print(f"  Confidence: {report.confidence_score:.1f}%")
        print(f"  Confluence: {report.confluence_count} other strategies aligned")
        
        if report.active_conflicts:
             print(f"  CONFLICT: Contradicted by {report.active_conflicts}")
        
        print(f"  Notes: {report.notes}")
        print("-" * 30)

if __name__ == "__main__":
    main()
