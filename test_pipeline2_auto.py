#!/usr/bin/env python3
"""
Test script to verify Pipeline 2 auto-classification flow
Creates test facts with domain=NULL and classifies them
"""

import sys
sys.path.insert(0, '/home/ahmed/Bureau/stage project/ml-service')

from pipeline1.models import get_session, KnowledgeFact, FactValue, ValueTypeEnum, StatusEnum
from pipeline2 import classify_and_update, classifier

session = get_session()

print("=" * 60)
print("TESTING PIPELINE 2 AUTO-CLASSIFICATION")
print("=" * 60)

# Step 1: Create test facts with domain=NULL
print("\n1. Creating test facts with domain=NULL...")

test_facts = [
    {
        "subject": "Health clinic",
        "relation": "has_staff",
        "values": "3 nurses and 1 midwife",
        "source_text": "Health clinic operates with staff of 3 nurses and 1 midwife providing basic healthcare"
    },
    {
        "subject": "Rice farmers",
        "relation": "earn",
        "values": "2-3 million IDR per harvest",
        "source_text": "Rice farmers earn average income of 2-3 million IDR per harvest season"
    },
    {
        "subject": "Main road",
        "relation": "requires",
        "values": "maintenance every monsoon",
        "source_text": "Main road requires maintenance and repair every monsoon season"
    }
]

created_ids = []
for fact_data in test_facts:
    fact = KnowledgeFact(
        subject=fact_data["subject"],
        relation=fact_data["relation"],
        source_text=fact_data["source_text"],
        domain=None,  # Start with NULL
        visibility="public",
        confidence_score=0.8,
        extraction_method="test",
        status=StatusEnum.PENDING_REVIEW
    )
    session.add(fact)
    session.flush()  # Get the ID
    created_ids.append(fact.id)
    
    # Add fact value
    fv = FactValue(
        fact_id=fact.id,
        value_type=ValueTypeEnum.CATEGORICAL,
        value_categorical=fact_data["values"]
    )
    session.add(fv)
    
    print(f"  ✅ Created fact {fact.id}: {fact.subject} {fact.relation}")

session.commit()
print(f"\n✅ Created {len(created_ids)} test facts with domain=NULL")

# Step 2: Verify facts were created with domain=NULL
print("\n2. Verifying facts with domain=NULL...")
unclassified_count = session.query(KnowledgeFact).filter(KnowledgeFact.domain == None).count()
print(f"  Found {unclassified_count} facts with domain=NULL")

# Step 3: Get unclassified items
print("\n3. Getting unclassified items from storage...")
from pipeline2 import storage
items = storage.get_all_unclassified()
print(f"  ✅ Retrieved {len(items)} unclassified items")
if items:
    for item in items[:3]:
        print(f"    - {item['type']}: {item.get('subject', 'N/A')} {item.get('relation', 'N/A')}")

# Step 4: Test classifier prediction
print("\n4. Testing classifier prediction...")
if items:
    predictions = classifier.predict(items)
    print(f"  ✅ Classified {len(predictions)} items")
    for pred in predictions[:3]:
        print(f"    - Domain: {pred['predicted_domain']}, Confidence: {pred['confidence']:.2f}, Status: {pred['status']}")

# Step 5: Run full classify_and_update
print("\n5. Running classify_and_update()...")
result = classify_and_update()
print(f"  Status: {result['status']}")
print(f"  Rules classified: {result.get('rules_classified', 0)}")
print(f"  Facts classified: {result.get('facts_classified', 0)}")
print(f"  Domain distribution: {result.get('domain_distribution', {})}")

# Step 6: Verify domains were updated
print("\n6. Verifying domains were updated...")
for fact_id in created_ids:
    fact = session.query(KnowledgeFact).filter(KnowledgeFact.id == fact_id).first()
    print(f"  Fact {fact_id}: domain={fact.domain}, algorithm={fact.algorithm_used}")

print("\n" + "=" * 60)
print("✅ TEST COMPLETE")
print("=" * 60)
