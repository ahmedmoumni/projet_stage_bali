# Semantic Structure for CSV Processing - Implementation Summary

## Problem Identified

Previously, the system would treat each CSV row as a single fact with multiple values mixed together:

```
❌ OLD STRUCTURE:
CSV Row: Kelodan, 516, partial
Result: 1 fact
  - subject: Kelodan
  - relation: imported_from_csv (generic)
  - values: [516, partial] (mixed)
```

This was semantically incorrect because:
- The relation name was generic and meaningless
- All data was flattened into a single fact
- Column semantics were lost

## Solution Implemented

The system now correctly understands CSV structure and creates one fact per relation:

```
✅ NEW STRUCTURE:
CSV Row: Kelodan, 516, partial
CSV Headers: dusun, population, water_access
Result: 2 facts (one per relation column)
  
  Fact 1:
  - subject: Kelodan
  - relation: has_population
  - value: 516 (continuous, persons)
  
  Fact 2:
  - subject: Kelodan
  - relation: has_water_access
  - value: partial (categorical)
```

## Changes Made

### 1. Pipeline 0 (ml-service/pipeline0/router.py)

Added semantic structure identification:
- Identifies first column as SUBJECT
- Identifies remaining columns as RELATION columns
- Returns metadata: `subject_column` and `relation_columns` in response data

```python
# Before: just returned headers and rows
'data': {'headers': headers, 'rows': rows}

# After: includes semantic structure
'data': {
    'headers': headers,
    'rows': rows,
    'subject_column': headers[0],
    'relation_columns': headers[1:]
}
```

### 2. Pipeline 2 (ml-service/app.py)

Modified classify endpoint to process structured data correctly:
- Receives subject_column and relation_columns metadata
- Creates N predictions per row (one per relation column)
- Each prediction includes:
  - `subject`: from first column
  - `relation`: format "has_{column_name}"
  - `relation_column`: original column header
  - `relation_value`: single cell value
  - `domain`: classified domain
  - `confidence`: classification confidence

```python
# Creates N facts per row
for row in rows:
    subject = row[subject_column]
    for relation_col in relation_columns:
        # Create separate prediction for each relation
        pred_obj = {
            'subject': subject,
            'relation': f'has_{relation_col.lower()}',
            'relation_column': relation_col,
            'relation_value': row[relation_col],
            ...
        }
        predictions.append(pred_obj)
```

### 3. Backend DocumentController (backend/app/Http/Controllers/DocumentController.php)

Updated to:
- Extract semantic metadata from Pipeline 0: `subject_column` and `relation_columns`
- Pass metadata to Pipeline 2
- Create one fact per prediction (not one fact per row)
- Create one fact_value per fact (not multiple)

```php
// Extract metadata
$subjectColumn = $structuredData['subject_column'];
$relationColumns = $structuredData['relation_columns'];

// Pass to Pipeline 2
->post($pipeline2Url . '/pipeline2/classify', [
    'data' => [
        'headers' => $headers,
        'rows' => $rows,
        'subject_column' => $subjectColumn,
        'relation_columns' => $relationColumns
    ]
]);

// Create facts: one per prediction (not per row)
foreach ($pipeline2Result['predictions'] as $prediction) {
    // Each prediction already has subject, relation, column, and value
    KnowledgeFact::create([
        'subject' => $prediction['subject'],
        'relation' => $prediction['relation'],  // e.g., 'has_population'
        'domain' => $prediction['domain'],
        ...
    ]);
    
    // One fact_value per fact
    FactValue::create([
        'parent_id' => $fact->id,
        'value_type' => $valueType,
        'value_continuous' => $relationValue,
        'column_name' => $relationColumn
    ]);
}
```

## Example

### Input CSV
```
dusun,population,water_access
Kelodan,516,partial
Denpasar,2000,full
```

### Processing
1. Pipeline 0 detects:
   - subject_column: "dusun"
   - relation_columns: ["population", "water_access"]

2. Pipeline 2 creates 4 predictions:
   - Kelodan | has_population | 516
   - Kelodan | has_water_access | partial
   - Denpasar | has_population | 2000
   - Denpasar | has_water_access | full

3. Backend creates 4 facts with proper semantics

4. Database stores:
   ```
   knowledge_facts:
   ├─ ID 1: Kelodan | has_population | culture_art (20%)
   ├─ ID 2: Kelodan | has_water_access | infrastructure (90%)
   ├─ ID 3: Denpasar | has_population | social (85%)
   └─ ID 4: Denpasar | has_water_access | infrastructure (90%)
   
   fact_values:
   ├─ Parent: Fact 1 → value: 516 (continuous, persons)
   ├─ Parent: Fact 2 → value: partial (categorical)
   ├─ Parent: Fact 3 → value: 2000 (continuous, persons)
   └─ Parent: Fact 4 → value: full (categorical)
   ```

## Benefits

✅ **Semantically Correct**: Each fact represents a single relation
✅ **Proper Naming**: Relations are named based on column headers (has_population, has_water_access)
✅ **Preserved Context**: Column names and value types are preserved
✅ **Scalable**: Works with any number of columns
✅ **Domain Classification**: Each relation is classified to a domain independently
✅ **Value Type Detection**: Values properly detected as continuous or categorical
✅ **Unit Inference**: Units are guessed from column names (population→persons, temperature→°C)

## Verification

Test with any CSV file:
- Upload CSV with headers
- System automatically detects subject column (first) and relation columns (rest)
- Creates N predictions per row (1 per relation)
- Creates N facts (1 per prediction)
- Each fact has 1 fact_value with proper metadata
