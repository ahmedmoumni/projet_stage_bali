from typing import List, Dict, Any

from sqlalchemy import text
from pipeline1.models import get_session, KnowledgeRule, RuleConditionFact, RuleActionFact, StatusEnum, ValueTypeEnum


def _resolve_value_type(value: Any) -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return 'continuous'
    return 'categorical'


def _persist_value(parent_type: str, parent_id: int, value: Any, unit: str | None = None) -> None:
    session = get_session()
    try:
        value_type = _resolve_value_type(value)
        value_continuous = float(value) if value_type == 'continuous' else None
        value_categorical = None if value_type == 'continuous' else str(value)

        insert_query = text(
            """
            INSERT INTO fact_values (
                parent_type,
                parent_id,
                value_type,
                value_continuous,
                value_categorical,
                unit,
                created_at
            ) VALUES (
                :parent_type,
                :parent_id,
                :value_type,
                :value_continuous,
                :value_categorical,
                :unit,
                NOW()
            )
            """
        )

        session.execute(insert_query, {
            'parent_type': parent_type,
            'parent_id': parent_id,
            'value_type': value_type,
            'value_continuous': value_continuous,
            'value_categorical': value_categorical,
            'unit': unit,
        })
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def store_rules(rules: List[Dict[str, Any]], filename: str, target_column: str) -> Dict[str, Any]:
    session = get_session()
    created_rule_ids: List[int] = []
    try:
        for index, rule in enumerate(rules, start=1):
            knowledge_rule = KnowledgeRule(
                source_text=f"Generated from CSV: {filename}",
                domain='',
                visibility='private',
                confidence_score=float(rule['confidence']),
                extraction_method='llm',
                algorithm_used='decision_tree',
                condition_group_operator='AND',
                action_group_operator=None,
                status=StatusEnum.VALIDATED if rule['status'] == 'validated' else StatusEnum.PENDING_REVIEW,
            )
            session.add(knowledge_rule)
            session.flush()

            for condition_index, condition in enumerate(rule['conditions']):
                condition_fact = RuleConditionFact(
                    rule_id=knowledge_rule.id,
                    subject=condition['subject'],
                    operator=condition['operator'],
                    logical_operator='AND' if condition_index < len(rule['conditions']) - 1 else None,
                    group_id=1,
                )
                session.add(condition_fact)
                session.flush()
                _persist_value('condition_fact', condition_fact.id, condition['value'])

            action_fact = RuleActionFact(
                rule_id=knowledge_rule.id,
                subject=target_column,
                operator='=',
                logical_operator=None,
                group_id=1,
            )
            session.add(action_fact)
            session.flush()
            _persist_value('action_fact', action_fact.id, rule['action'])

            created_rule_ids.append(knowledge_rule.id)

        session.commit()
        return {
            'stored_rules': len(created_rule_ids),
            'rule_ids': created_rule_ids,
        }
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
