from app.services.baselines import (
    random_baseline,
    rule_only_baseline,
    hybrid_baseline,
)

from app.services.metrics_service import calculate_metrics


def evaluate_models(
    outfits,
    weather,
    total_valid_items,
    top_k,
    target_formality,
    weights,
):

    random_results = random_baseline(outfits, top_k)

    rule_results = rule_only_baseline(outfits, top_k)

    hybrid_results = hybrid_baseline(
        outfits=outfits,
        weather=weather,
        top_k=top_k,
        target_formality=target_formality,
        weights=weights,
    )

    return {
        "random_baseline": {
            "metrics": calculate_metrics(random_results, total_valid_items),
            "outfits": random_results,
        },
        "rule_only_baseline": {
            "metrics": calculate_metrics(rule_results, total_valid_items),
            "outfits": rule_results,
        },
        "hybrid_model": {
            "metrics": calculate_metrics(hybrid_results, total_valid_items),
            "outfits": hybrid_results,
        },
    }