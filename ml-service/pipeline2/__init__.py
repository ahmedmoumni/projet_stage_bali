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
            "classified": 0
        }
    
    # Extract texts for classification
    texts = [item["text"] for item in unclassified]
    
    # Classify
    predictions = classifier.predict(texts)
    
    # Merge with item metadata
    classifications = []
    for item, prediction in zip(unclassified, predictions):
        classification = {
            "id": item["id"],
            "type": item["type"],
            "predicted_domain": prediction["predicted_domain"],
            "algorithm_used": prediction["algorithm_used"],
            "confidence": prediction["confidence"]
        }
        classifications.append(classification)
    
    # Update database
    update_results = storage.batch_update_domains(classifications)
    
    return {
        "status": "success",
        "message": f"Classification complete. Updated {update_results['updated_rules'] + update_results['updated_facts']} items",
        "updated_rules": update_results["updated_rules"],
        "updated_facts": update_results["updated_facts"],
        "failed": update_results["failed"],
        "classifications": classifications[:10]  # Return first 10 for preview
    }

__all__ = [
    "train_pipeline2",
    "classify_pipeline2", 
    "classify_and_update",
    "classifier",
    "storage"
]
