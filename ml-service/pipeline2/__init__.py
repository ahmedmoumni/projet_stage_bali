"""
Pipeline 2: Domain Classification
Exports main functions for domain classification
"""

from .classifier import classifier, DomainClassifier
from .storage import storage, DomainStorage

def train_pipeline2():
    """Train both classifiers and return evaluation results"""
    return classifier.train()

def classify_pipeline2(texts):
    """Classify texts into domains"""
    if not texts:
        return []
    return classifier.predict(texts if isinstance(texts, list) else [texts])

def classify_and_update():
    """Classify all unclassified items and update database"""
    unclassified = storage.get_all_unclassified()
    
    if not unclassified:
        return {
            "status": "success",
            "message": "No unclassified items found",
            "rules_classified": 0,
            "facts_classified": 0,
            "domain_distribution": {}
        }
    
    # Classify items (pass full item dicts with all required fields)
    predictions = classifier.predict(unclassified)
    
    # Merge with item metadata
    classifications = []
    domain_distribution = {}
    for item, prediction in zip(unclassified, predictions):
        domain = prediction.get("predicted_domain", "unknown")
        classification = {
            "id": item["id"],
            "type": item["type"],
            "predicted_domain": domain,
            "algorithm_used": prediction.get("algorithm_used", "unknown"),
            "confidence": prediction.get("confidence", 0)
        }
        classifications.append(classification)
        
        # Count domain distribution
        domain_distribution[domain] = domain_distribution.get(domain, 0) + 1
    
    # Update database
    update_results = storage.batch_update_domains(classifications)
    
    # Separate counts by type
    rules_classified = update_results.get("updated_rules", 0)
    facts_classified = update_results.get("updated_facts", 0)
    
    return {
        "status": "success",
        "message": f"Classification complete. Updated {rules_classified + facts_classified} items",
        "rules_classified": rules_classified,
        "facts_classified": facts_classified,
        "domain_distribution": domain_distribution,
        "failed": update_results.get("failed", 0),
        "classifications": classifications[:10]  # Return first 10 for preview
    }

__all__ = [
    "train_pipeline2",
    "classify_pipeline2", 
    "classify_and_update",
    "classifier",
    "storage"
]
