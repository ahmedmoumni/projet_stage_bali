import os
from typing import List, Dict, Any, Optional

import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn import tree

from pipeline1.models import get_session, KnowledgeRule, RuleConditionFact, RuleActionFact, FactValue, StatusEnum, ValueTypeEnum


class RuleDiscoveryError(Exception):
    pass


def _is_numeric(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series)


def _coerce_feature_values(feature_values: pd.Series) -> List[Any]:
    values = []
    for value in feature_values.tolist():
        if pd.isna(value):
            values.append('')
        elif isinstance(value, (int, float)):
            values.append(float(value))
        else:
            values.append(str(value))
    return values


def _simplify_conditions(path: List[Dict[str, Any]], feature_order: List[str]) -> List[Dict[str, Any]]:
    bounds: Dict[str, Dict[str, Optional[float]]] = {}

    for condition in path:
        feature = condition['subject']
        if feature not in bounds:
            bounds[feature] = {'lower': None, 'upper': None}

        if condition['operator'] == '>':
            lower = bounds[feature]['lower']
            bounds[feature]['lower'] = condition['value'] if lower is None else max(lower, condition['value'])
        elif condition['operator'] == '<=':
            upper = bounds[feature]['upper']
            bounds[feature]['upper'] = condition['value'] if upper is None else min(upper, condition['value'])

    simplified = []
    for feature in feature_order:
        if feature not in bounds:
            continue
        lower = bounds[feature]['lower']
        upper = bounds[feature]['upper']

        if lower is not None and upper is not None and lower >= upper:
            # This path is degenerate; keep no condition for the feature.
            continue

        if lower is not None:
            simplified.append({
                'subject': feature,
                'operator': '>',
                'value': lower,
                'value_type': 'continuous',
            })
        if upper is not None:
            simplified.append({
                'subject': feature,
                'operator': '<=',
                'value': upper,
                'value_type': 'continuous',
            })

    return simplified


def _normalize_threshold(feature_values: List[float], threshold: float) -> float:
    actual_values = [value for value in feature_values if value <= threshold]
    if not actual_values:
        return threshold
    return float(max(actual_values))


def _build_rule_path(
    tree_model: DecisionTreeClassifier,
    feature_names: List[str],
    class_names: List[str],
    feature_value_map: Dict[str, List[float]],
    node_id: int = 0,
    path: Optional[List[Dict[str, Any]]] = None,
    rules: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    if rules is None:
        rules = []
    if path is None:
        path = []

    tree_ = tree_model.tree_
    if tree_.children_left[node_id] == tree_.children_right[node_id]:
        predicted_value = class_names[tree_.value[node_id].argmax()]
        confidence = float(tree_.value[node_id].max() / tree_.value[node_id].sum())
        simplified_conditions = _simplify_conditions(path, feature_names)
        rules.append({
            'conditions': simplified_conditions,
            'action': predicted_value,
            'confidence': confidence,
            'samples': int(tree_.n_node_samples[node_id]),
        })
        return rules

    left_child = tree_.children_left[node_id]
    right_child = tree_.children_right[node_id]
    feature_idx = int(tree_.feature[node_id])
    threshold = float(tree_.threshold[node_id])
    feature_name = feature_names[feature_idx]

    normalized_value = threshold
    if feature_name in feature_value_map:
        normalized_value = _normalize_threshold(feature_value_map[feature_name], threshold)

    left_condition = {
        'subject': feature_name,
        'operator': '<=',
        'value': normalized_value,
        'value_type': 'continuous',
    }
    right_condition = {
        'subject': feature_name,
        'operator': '>',
        'value': normalized_value,
        'value_type': 'continuous',
    }

    _build_rule_path(tree_model, feature_names, class_names, feature_value_map, left_child, path + [left_condition], rules)
    _build_rule_path(tree_model, feature_names, class_names, feature_value_map, right_child, path + [right_condition], rules)
    return rules


def discover_rules_from_csv(file_obj, subject_column: str, target_column: str, feature_columns: List[str]) -> Dict[str, Any]:
    if not hasattr(file_obj, 'read'):
        raise RuleDiscoveryError('CSV file object is invalid')

    raw_bytes = file_obj.read()
    if not raw_bytes:
        raise RuleDiscoveryError('Uploaded CSV file is empty')

    try:
        df = pd.read_csv(pd.io.common.BytesIO(raw_bytes))
    except Exception as exc:
        raise RuleDiscoveryError(f'Unable to parse CSV: {exc}') from exc

    if df.empty:
        raise RuleDiscoveryError('CSV file contains no rows')

    missing_columns = [col for col in [subject_column, target_column] + feature_columns if col not in df.columns]
    if missing_columns:
        raise RuleDiscoveryError(f'Missing columns: {", ".join(missing_columns)}')

    prepared_df = df[[subject_column, target_column] + feature_columns].copy()
    X = pd.DataFrame({col: _coerce_feature_values(prepared_df[col]) for col in feature_columns})
    y = prepared_df[target_column]

    feature_value_map = {
        col: [float(value) for value in prepared_df[col].dropna().astype(float).tolist()]
        for col in feature_columns
        if _is_numeric(prepared_df[col])
    }

    tree_model = DecisionTreeClassifier(criterion='gini', max_depth=5, random_state=42)
    tree_model.fit(X, y)

    feature_names = list(X.columns)
    class_names = [str(v) for v in sorted(set(y.tolist()))]
    rules = _build_rule_path(tree_model, feature_names, class_names, feature_value_map)

    log_lines = []
    log_lines.append(f"✅ CSV loaded: {len(df)} rows, {len(df.columns)} columns")
    log_lines.append('✅ Decision Tree trained')
    log_lines.append(f"✅ {len(rules)} rules extracted from tree")

    formatted_rules = []
    for index, rule in enumerate(rules, start=1):
        condition_text = ' AND '.join(
            f"{item['subject']} {item['operator']} {item['value']}" for item in rule['conditions']
        )
        if condition_text:
            rule_text = f"IF {condition_text} THEN {target_column} = {rule['action']}"
        else:
            rule_text = f"THEN {target_column} = {rule['action']}"
        confidence = round(rule['confidence'], 2)
        status = 'validated' if confidence >= 0.80 else 'pending_review'
        log_lines.append(f"✅ Rule {index}: {rule_text} (confidence: {confidence})")
        formatted_rules.append({
            'rule_text': rule_text,
            'confidence': confidence,
            'status': status,
            'conditions': rule['conditions'],
            'action': rule['action'],
        })

    return {
        'rules_discovered': len(formatted_rules),
        'algorithm': 'decision_tree',
        'log': log_lines,
        'rules': formatted_rules,
        'filename': getattr(file_obj, 'filename', 'uploaded.csv'),
    }


def extract_rules_from_tree(model: DecisionTreeClassifier, feature_names: List[str], class_names: List[str]) -> List[Dict[str, Any]]:
    return _build_rule_path(model, feature_names, class_names)
