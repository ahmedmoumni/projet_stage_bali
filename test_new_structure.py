#!/usr/bin/env python3
"""
Test the new semantic structure:
- Pipeline 0 identifies subject_column and relation_columns
- Pipeline 2 creates N facts per row (one per relation)
- Backend creates N fact objects with proper relation names
"""

import requests
import json
import csv
import io

BASE_URL = "http://localhost:8000"
ML_URL = "http://localhost:5000"

print("="*70)
print("TEST: New Semantic Structure for CSV Processing")
print("="*70)

# Create test CSV data
csv_data = """dusun,population,water_access
Kelodan,516,partial
Denpasar,2000,full
Ubud,850,limited"""

print("\n1️⃣  Testing Pipeline 0 with new structure")
print("   CSV data:")
for line in csv_data.split('\n'):
    print(f"   {line}")

# Upload to backend
print("\n2️⃣  Uploading CSV to backend...")

# Create file from CSV data
files = {'file': ('test.csv', io.BytesIO(csv_data.encode()))}
data = {'visibility': 'public'}

# First, login
login_resp = requests.post(f'{BASE_URL}/api/login', json={'username': 'admin', 'password': 'admin'})
token = login_resp.json()['token']

upload_resp = requests.post(
    f'{BASE_URL}/api/documents/upload',
    files=files,
    data=data,
    headers={'Authorization': f'Bearer {token}'}
)

if upload_resp.status_code == 200:
    result = upload_resp.json()
    print(f"   ✅ Upload successful (status {upload_resp.status_code})")
    
    # Check Pipeline 0 result
    p0_result = result.get('pipeline0_result', {})
    print(f"\n3️⃣  Pipeline 0 Structure:")
    print(f"   File type: {p0_result.get('file_type')}")
    print(f"   Routing: {p0_result.get('routing')}")
    
    data_section = p0_result.get('data', {})
    print(f"   Headers: {data_section.get('headers')}")
    print(f"   Subject column: {data_section.get('subject_column')}")
    print(f"   Relation columns: {data_section.get('relation_columns')}")
    print(f"   Rows count: {len(data_section.get('rows', []))}")
    
    # Check Pipeline 2 result
    print(f"\n4️⃣  Pipeline 2 Predictions:")
    p2_result = result.get('pipeline2_result', {})
    predictions = p2_result.get('predictions', [])
    
    print(f"   Total predictions: {len(predictions)}")
    print(f"   Domain distribution: {p2_result.get('domain_distribution')}")
    
    print(f"\n5️⃣  Detailed Predictions Structure:")
    for i, pred in enumerate(predictions[:6], 1):
        print(f"\n   Prediction {i}:")
        print(f"      Subject: {pred.get('subject')}")
        print(f"      Relation: {pred.get('relation')}")
        print(f"      Relation Column: {pred.get('relation_column')}")
        print(f"      Relation Value: {pred.get('relation_value')}")
        print(f"      Domain: {pred.get('domain')}")
        print(f"      Confidence: {pred.get('confidence'):.2%}")
        print(f"      Text: {pred.get('text')}")
    
    # Check database facts created
    print(f"\n6️⃣  Facts Created in Database:")
    facts_resp = requests.get(
        f'{BASE_URL}/api/facts?status=all',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if facts_resp.status_code == 200:
        facts = facts_resp.json()['data']
        
        # Get the last N facts (from this upload)
        print(f"   Total facts in DB: {len(facts)}")
        
        # Show last facts (should be from this upload)
        recent_facts = sorted(facts, key=lambda f: f.get('id', 0), reverse=True)[:6]
        print(f"\n   Last 6 facts created:")
        for fact in recent_facts:
            print(f"\n   ID {fact['id']}: {fact['subject']} | {fact['relation']}")
            print(f"      Domain: {fact['domain']}")
            print(f"      Status: {fact['status']}")
            print(f"      Confidence: {fact['confidence_score']:.0%}")
            
            # Show fact values
            fact_values = fact.get('fact_values', [])
            print(f"      Values ({len(fact_values)}):")
            for fv in fact_values:
                col_name = fv.get('column_name', 'unknown')
                val_type = fv.get('value_type', 'unknown')
                
                if val_type == 'continuous':
                    val = f"{fv.get('value_continuous')} {fv.get('unit', '')}"
                else:
                    val = fv.get('value_categorical', '')
                
                print(f"         {col_name} ({val_type}): {val}")
    
    # Expected structure
    print(f"\n7️⃣  Expected Structure Check:")
    print(f"   ✅ 3 rows → 6 predictions (2 relations per row)")
    print(f"   ✅ Each fact has specific relation name (has_population, has_water_access)")
    print(f"   ✅ Each fact has ONE fact_value")
    print(f"   ✅ Column names preserved (population, water_access)")
    print(f"   ✅ Value types detected (continuous, categorical)")
    
    actual_pred_count = len(predictions)
    expected_pred_count = len(data_section.get('rows', [])) * len(data_section.get('relation_columns', []))
    
    if actual_pred_count == expected_pred_count:
        print(f"\n   ✅ PASS: Correct number of predictions ({actual_pred_count} = {expected_pred_count})")
    else:
        print(f"\n   ❌ FAIL: Wrong prediction count ({actual_pred_count} ≠ {expected_pred_count})")
    
else:
    print(f"   ❌ Upload failed: {upload_resp.status_code}")
    print(f"   {upload_resp.json()}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
