"""
Pipeline 1: Knowledge Extraction
Extracts IF-THEN rules and subject-relation-object facts from text
Uses spaCy for parsing and Groq LLM for low-confidence cases
"""

import re
import spacy
import json
import os
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime
from sqlalchemy import text
from .models import (
    get_session, KnowledgeRule, RuleConditionFact, RuleActionFact,
    KnowledgeFact, FactValue, StatusEnum, ValueTypeEnum
)

# Load environment variables
load_dotenv()

# Load spaCy model
nlp = None

def load_spacy_model():
    """Load spaCy model with proper error handling"""
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load('en_core_web_sm')
            print("✅ spaCy model loaded successfully")
        except OSError:
            print("❌ spaCy model not found. Run: python -m spacy download en_core_web_sm")
            nlp = None
    return nlp

# Initialize Groq client directly
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("⚠️  GROQ_API_KEY not set in .env file")
    groq_api_key = ""

# Lazy initialization
_groq_client = None

def get_groq_client():
    """Get or initialize Groq client"""
    global _groq_client
    if _groq_client is None:
        try:
            if groq_api_key:
                _groq_client = Groq(api_key=groq_api_key)
            else:
                print("⚠️  GROQ_API_KEY not set - LLM fallback will be unavailable")
                _groq_client = None
        except Exception as e:
            print(f"⚠️  Failed to initialize Groq client: {str(e)}")
            _groq_client = None
    return _groq_client

client = None  # Will be set on first use


# Stop words to remove
STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'or', 'that',
    'the', 'to', 'was', 'will', 'with'
}

# Conditional markers for RULE detection
RULE_MARKERS = {
    'if', 'when', 'unless', 'rarely', 'tends', 'above', 'below',
    'exceeds', 'more than', 'less than', 'at least', 'at most',
    'usually', 'always', 'never'
}

# Copula and relational verbs for FACT detection
FACT_MARKERS = {
    'is', 'are', 'was', 'were', 'has', 'have', 'contains',
    'lacks', 'manages', 'supervises', 'provides', 'belongs',
    'supervised', 'located'
}


class KnowledgeExtractor:
    """Main extractor class coordinating all 5 stages"""

    def __init__(self):
        global nlp
        # Ensure spaCy model is loaded
        if nlp is None:
            load_spacy_model()
        self.session = get_session()
        self.extraction_log = []

    @staticmethod
    def _get_root_token(doc):
        """Get the root token of a spaCy doc (head of sentence)"""
        for token in doc:
            if token.head == token:
                return token
        return doc[0] if len(doc) > 0 else None

    def extract_from_text(self, text: str, document_id: int = None) -> Dict:
        """
        Main extraction pipeline
        Args:
            text: Input text from document
            document_id: Optional document_log ID for tracking
        Returns:
            Dictionary with extraction results and log
        """
        self.extraction_log = []
        results = {
            'rules_extracted': 0,
            'facts_extracted': 0,
            'rules': [],
            'facts': [],
            'log': self.extraction_log,
            'document_id': document_id
        }

        try:
            # STAGE 1: Pre-processing
            self.log(f" Stage 1: Pre-processing text ({len(text)} chars)")
            sentences = self._preprocess(text)
            self.log(f" Extracted {len(sentences)} sentences")
            results['sentences_count'] = len(sentences)

            # STAGE 2 & 3: Knowledge Type Detection + Extraction
            for idx, sentence in enumerate(sentences):
                self.log(f"\n Processing sentence {idx + 1}: {sentence[:60]}...")

                # Detect type
                knowledge_type = self._detect_knowledge_type(sentence)
                self.log(f"  Type: {knowledge_type}")

                # Extract
                if knowledge_type == 'rule':
                    extracted = self._extract_rule(sentence)
                    if extracted:
                        results['rules'].append(extracted)
                        results['rules_extracted'] += 1
                elif knowledge_type == 'fact':
                    extracted = self._extract_fact(sentence)
                    if extracted:
                        results['facts'].append(extracted)
                        results['facts_extracted'] += 1

            # STAGE 5: Validate and Store
            self.log(f"\n Stage 5: Validating and storing extracted knowledge")
            for rule in results['rules']:
                self._store_rule(rule)
            for fact in results['facts']:
                self._store_fact(fact)

            self.log(f" Extraction complete: {results['rules_extracted']} rules, {results['facts_extracted']} facts")

        except Exception as e:
            self.log(f" Extraction error: {str(e)}")
            results['error'] = str(e)

        return results

    # ============ STAGE 1: PRE-PROCESSING ============

    def _preprocess(self, text: str) -> List[str]:
        """
        Stage 1: Clean text and split into sentences
        - Remove special characters
        - Convert to lowercase
        - Split into sentences
        - Remove stop words
        """
        if not nlp:
            return []

        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.!?,;:\'-]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()

        # Process with spaCy
        doc = nlp(text)

        # Extract sentences
        sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]

        # Lowercase
        sentences = [s.lower() for s in sentences]

        return sentences

    # ============ STAGE 2: KNOWLEDGE TYPE DETECTION ============

    def _detect_knowledge_type(self, sentence: str) -> Optional[str]:
        """
        Stage 2: Classify sentence as RULE or FACT
        Returns: 'rule', 'fact', or None
        """
        sentence_lower = sentence.lower()

        # Check for rule markers
        for marker in RULE_MARKERS:
            if marker in sentence_lower:
                confidence = 0.8
                self.log(f"  Rule marker detected: '{marker}' (confidence: {confidence})")
                return 'rule'

        # Check for fact markers
        for marker in FACT_MARKERS:
            if marker in sentence_lower:
                confidence = 0.8
                self.log(f"  Fact marker detected: '{marker}' (confidence: {confidence})")
                return 'fact'

        # Low confidence - use LLM
        self.log(f"  No clear markers, using LLM for classification")
        llm_type = self._llm_detect_type(sentence)
        return llm_type

    def _llm_detect_type(self, sentence: str) -> Optional[str]:
        """Use Groq API to detect knowledge type"""
        try:
            groq_client = get_groq_client()
            if not groq_client:
                self.log(f"    Groq client not available")
                return None
            
            prompt = f"""Classify this sentence as either 'rule' (if-then statement) or 'fact' (declarative statement).
Respond with only the word 'rule' or 'fact'.

Sentence: {sentence}"""

            response = groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip().lower()
            return 'rule' if 'rule' in result else 'fact' if 'fact' in result else None

        except Exception as e:
            self.log(f"    LLM classification failed: {str(e)}")
            return None

    # ============ STAGE 3: EXTRACTION ============

    def _extract_rule(self, sentence: str) -> Optional[Dict]:
        """
        Extract IF-THEN rule using spaCy
        Returns: Rule dict or None
        """
        if not nlp:
            return None

        try:
            doc = nlp(sentence)

            # Extract conditions (IF part) and actions (THEN part)
            conditions = self._extract_conditions(doc, sentence)
            actions = self._extract_actions(doc, sentence)

            if not conditions or not actions:
                self.log(f"  Missing conditions or actions")
                return None

            # Calculate confidence
            confidence = self._calculate_confidence(conditions, actions)

            # If low confidence, use LLM
            if confidence < 0.8:
                self.log(f"  Low confidence ({confidence}), using LLM")
                return self._llm_extract_rule(sentence)

            return {
                'type': 'rule',
                'source_text': sentence,
                'conditions': conditions,
                'actions': actions,
                'condition_group_operator': 'AND',
                'action_group_operator': 'AND',
                'confidence': confidence,
                'extraction_method': 'spacy'
            }

        except Exception as e:
            self.log(f"   spaCy extraction failed: {str(e)}, trying LLM")
            return self._llm_extract_rule(sentence)

    def _extract_fact(self, sentence: str) -> Optional[Dict]:
        """
        Extract subject-relation-object fact using spaCy
        Returns: Fact dict or None
        """
        if not nlp:
            return None

        try:
            doc = nlp(sentence)

            # Find subject (nsubj) - include modifiers
            subject = None
            subject_token = None
            for token in doc:
                if token.dep_ == "nsubj":
                    subject_token = token
                    # Include compound modifiers (e.g., "north district")
                    subject_parts = []
                    for child in token.subtree:
                        if child.dep_ in ["compound", "amod", "det"]:
                            subject_parts.append(child.text)
                    subject_parts.append(token.text)
                    subject = " ".join(subject_parts)
                    break

            if not subject:
                self.log(f"  No subject found")
                return None

            # Find relation (root verb)
            root = self._get_root_token(doc)
            relation = root.lemma_ if root else None

            if not relation:
                self.log(f"  No relation found")
                return None

            # Find objects (dobj, pobj) - include modifiers
            values = []
            seen_values = set()
            for token in doc:
                if token.dep_ in ["dobj", "pobj", "attr", "nmod"]:
                    # Include modifiers for compound objects
                    value_parts = []
                    for child in token.subtree:
                        if child.dep_ in ["compound", "amod", "det"]:
                            value_parts.append(child.text)
                    value_parts.append(token.text)
                    value_text = " ".join(value_parts)
                    
                    if value_text not in seen_values:
                        seen_values.add(value_text)
                        values.append({
                            'value': value_text,
                            'value_type': 'categorical',
                            'unit': None
                        })

            if not values:
                self.log(f"  No values found")
                return None

            confidence = self._calculate_confidence({'subject': subject}, {'relation': relation, 'values': values})

            if confidence < 0.8:
                self.log(f"  Low confidence ({confidence}), using LLM")
                return self._llm_extract_fact(sentence)

            return {
                'type': 'fact',
                'source_text': sentence,
                'subject': subject,
                'relation': relation,
                'values': values,
                'confidence': confidence,
                'extraction_method': 'spacy'
            }

        except Exception as e:
            self.log(f"   spaCy extraction failed: {str(e)}, trying LLM")
            return self._llm_extract_fact(sentence)

    def _extract_conditions(self, doc, sentence: str) -> List[Dict]:
        """Extract conditions from a rule sentence"""
        conditions = []

        for token in doc:
            if token.dep_ == "nsubj":  # Subject of condition
                # Build subject with modifiers
                subject_parts = []
                for child in token.subtree:
                    if child.dep_ in ["compound", "amod", "det"] and child != token:
                        subject_parts.append(child.text)
                subject_parts.append(token.text)
                subject = " ".join(subject_parts)
                
                condition = {
                    'subject': subject,
                    'operator': '=',
                    'values': [],
                    'logical_operator': None,
                    'group_id': 0
                }

                # Get the root verb (head of this nsubj)
                root_verb = token.head
                
                # Find the operator/comparison verb
                operator_text = root_verb.lemma_.lower() if root_verb else ''
                if operator_text in ['exceed', 'exceed', 'less', 'greater', 'equal']:
                    condition['operator'] = operator_text
                
                # Find objects, numbers, and values
                for child in root_verb.children:
                    if child.dep_ in ["dobj", "attr", "nmod", "compound", "pobj"]:
                        # Add value with modifiers
                        value_parts = []
                        for subchild in child.subtree:
                            if subchild.dep_ in ["compound", "amod", "det"] and subchild != child:
                                value_parts.append(subchild.text)
                        value_parts.append(child.text)
                        value_text = " ".join(value_parts)
                        
                        condition['values'].append({
                            'value': value_text,
                            'value_type': 'categorical',
                            'unit': None
                        })
                    elif child.dep_ == "nummod":  # Numbers
                        condition['values'].append({
                            'value': child.text,
                            'value_type': 'continuous',
                            'unit': None
                        })

                if condition['values'] or root_verb.lemma_ in RULE_MARKERS:
                    conditions.append(condition)

        return conditions

    def _extract_actions(self, doc, sentence: str) -> List[Dict]:
        """Extract actions from a rule sentence"""
        actions = []

        # Find the root verb (main action)
        root = self._get_root_token(doc)
        if root and root.pos_ == "VERB":
            action = {
                'subject': '',
                'operator': '=',
                'values': [],
                'logical_operator': None,
                'group_id': 0
            }

            # Find subject and objects of root verb
            for child in root.children:
                if child.dep_ == "nsubj":
                    # Include subject modifiers
                    subject_parts = []
                    for subchild in child.subtree:
                        if subchild.dep_ in ["compound", "amod", "det"] and subchild != child:
                            subject_parts.append(subchild.text)
                    subject_parts.append(child.text)
                    action['subject'] = " ".join(subject_parts)
                elif child.dep_ in ["dobj", "attr", "pobj"]:
                    # Include value modifiers
                    value_parts = []
                    for subchild in child.subtree:
                        if subchild.dep_ in ["compound", "amod", "det"] and subchild != child:
                            value_parts.append(subchild.text)
                    value_parts.append(child.text)
                    value_text = " ".join(value_parts)
                    
                    action['values'].append({
                        'value': value_text,
                        'value_type': 'categorical',
                        'unit': None
                    })

            if action['subject'] or action['values']:
                actions.append(action)

        # Also find other verbs that might be actions
        for token in doc:
            if token.pos_ in ["VERB"] and token != root:
                action = {
                    'subject': '',
                    'operator': '=',
                    'values': [],
                    'logical_operator': None,
                    'group_id': 0
                }

                # Find subject and object
                for child in token.children:
                    if child.dep_ == "nsubj":
                        # Include subject modifiers
                        subject_parts = []
                        for subchild in child.subtree:
                            if subchild.dep_ in ["compound", "amod", "det"] and subchild != child:
                                subject_parts.append(subchild.text)
                        subject_parts.append(child.text)
                        action['subject'] = " ".join(subject_parts)
                    elif child.dep_ in ["dobj", "attr", "pobj"]:
                        # Include value modifiers
                        value_parts = []
                        for subchild in child.subtree:
                            if subchild.dep_ in ["compound", "amod", "det"] and subchild != child:
                                value_parts.append(subchild.text)
                        value_parts.append(child.text)
                        value_text = " ".join(value_parts)
                        
                        action['values'].append({
                            'value': value_text,
                            'value_type': 'categorical',
                            'unit': None
                        })

                if action['subject'] or action['values']:
                    # Check if not already added
                    if not any(a['subject'] == action['subject'] for a in actions):
                        actions.append(action)

        return actions

    # ============ LLM EXTRACTION FALLBACK ============

    def _llm_extract_rule(self, sentence: str) -> Optional[Dict]:
        """Use Groq API to extract rule"""
        try:
            prompt = f"""Extract a structured IF-THEN rule from this sentence.
Return ONLY a JSON object with no markdown or explanation.

Format:
{{
  "conditions": [
    {{"subject": "string", "operator": "string", "value": "string", "logical_operator": "AND"/"OR"/null}}
  ],
  "actions": [
    {{"subject": "string", "operator": "string", "value": "string", "logical_operator": "AND"/"OR"/null}}
  ],
  "condition_group_operator": "AND"/"OR",
  "action_group_operator": "AND"/"OR",
  "confidence": 0.0-1.0
}}

Sentence: {sentence}"""

            groq_client = get_groq_client()
            if not groq_client:
                self.log(f"  Groq client not available")
                return None
            
            response = groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()

            # Try to parse JSON
            try:
                extracted = json.loads(result_text)
                extracted['source_text'] = sentence
                extracted['type'] = 'rule'
                extracted['extraction_method'] = 'llm'
                return extracted
            except json.JSONDecodeError:
                self.log(f"   Invalid JSON from LLM")
                return None

        except Exception as e:
            self.log(f"   LLM extraction failed: {str(e)}")
            return None

    def _llm_extract_fact(self, sentence: str) -> Optional[Dict]:
        """Use Groq API to extract fact"""
        try:
            prompt = f"""Extract a subject-relation-object fact from this sentence.
Return ONLY a JSON object with no markdown or explanation.

Format:
{{
  "subject": "string",
  "relation": "string",
  "values": [
    {{"value": "string", "value_type": "continuous"/"categorical", "unit": null/"string"}}
  ],
  "confidence": 0.0-1.0
}}

Sentence: {sentence}"""

            groq_client = get_groq_client()
            if not groq_client:
                self.log(f"  Groq client not available")
                return None
            
            response = groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content.strip()

            try:
                extracted = json.loads(result_text)
                extracted['source_text'] = sentence
                extracted['type'] = 'fact'
                extracted['extraction_method'] = 'llm'
                return extracted
            except json.JSONDecodeError:
                self.log(f"    Invalid JSON from LLM")
                return None

        except Exception as e:
            self.log(f"   LLM extraction failed: {str(e)}")
            return None

    # ============ STAGE 4: NORMALIZATION ============

    def _normalize_operator(self, operator_str: str) -> str:
        """Map natural language operators to symbols"""
        operator_str = operator_str.lower()

        if any(x in operator_str for x in ['above', 'exceeds', 'more than', 'greater than']):
            return '>'
        elif any(x in operator_str for x in ['below', 'less than']):
            return '<'
        elif any(x in operator_str for x in ['at least', 'minimum']):
            return '>='
        elif any(x in operator_str for x in ['at most', 'maximum']):
            return '<='
        elif any(x in operator_str for x in ['equals', 'is', '=']):
            return '='
        elif any(x in operator_str for x in ['in', 'one of']):
            return 'IN'
        elif 'between' in operator_str:
            return 'BETWEEN'

        return '='

    def _detect_value_type(self, value: str) -> Tuple[str, Optional[float], Optional[str]]:
        """
        Detect if value is continuous or categorical
        Returns: (value_type, continuous_value, categorical_value)
        """
        try:
            # Try parsing as number
            float_val = float(value)
            return (ValueTypeEnum.CONTINUOUS, float_val, None)
        except (ValueError, TypeError):
            return (ValueTypeEnum.CATEGORICAL, None, value)

    def _detect_unit(self, value_str: str) -> Optional[str]:
        """Detect unit from value string"""
        value_lower = value_str.lower()

        unit_mappings = {
            ('l', 'liter', 'liters'): 'L',
            ('kg', 'kilogram'): 'kg',
            ('idr', 'rupiah'): 'IDR',
            ('person', 'persons', 'inhabitants', 'residents'): 'persons',
            ('%', 'percent'): '%',
        }

        for keywords, unit in unit_mappings.items():
            if any(kw in value_lower for kw in keywords):
                return unit

        return None

    def _calculate_confidence(self, *args) -> float:
        """Calculate confidence score (0.0 - 1.0)"""
        score = 0.8  # Start with base score of 0.8 (increased from 0.7)
        
        # Check if subjects exist
        for arg in args:
            if isinstance(arg, dict):
                if arg.get('subject'):
                    score += 0.05
                if arg.get('relation') or arg.get('operator'):
                    score += 0.05
                if arg.get('values') and len(arg.get('values', [])) > 0:
                    score += 0.05

        return min(score, 1.0)

    # ============ STAGE 5: VALIDATION & STORAGE ============

    def _validate_rule(self, rule: Dict) -> bool:
        """Validate rule structure"""
        return (
            rule.get('conditions') and
            rule.get('actions') and
            all(c.get('subject') for c in rule['conditions']) and
            all(a.get('subject') for a in rule['actions'])
        )

    def _validate_fact(self, fact: Dict) -> bool:
        """Validate fact structure"""
        return (
            fact.get('subject') and
            fact.get('relation') and
            fact.get('values')
        )

    def _store_rule(self, rule: Dict):
        """Store rule in database"""
        try:
            # All extracted data starts as PENDING_REVIEW for admin review
            # Validation only checks if data is well-formed
            status = StatusEnum.PENDING_REVIEW

            # Create knowledge rule
            kb_rule = KnowledgeRule(
                source_text=rule['source_text'],
                domain='',  # Empty string instead of None (Laravel doesn't allow NULL)
                visibility='private',
                confidence_score=rule['confidence'],
                extraction_method=rule['extraction_method'],
                algorithm_used='',  # Empty string instead of None
                condition_group_operator=rule.get('condition_group_operator', 'AND'),
                action_group_operator=rule.get('action_group_operator', 'AND'),
                status=status
            )
            self.session.add(kb_rule)
            self.session.flush()  # Get the ID

            # Store conditions
            for cond in rule['conditions']:
                cond_fact = RuleConditionFact(
                    rule_id=kb_rule.id,
                    subject=cond['subject'],
                    operator=self._normalize_operator(cond.get('operator', '=')),
                    logical_operator=cond.get('logical_operator'),
                    group_id=cond.get('group_id')
                )
                self.session.add(cond_fact)
                self.session.flush()

                # Store condition values using raw SQL (Laravel-compatible structure)
                for val in cond.get('values', []):
                    val_type, cont, cat = self._detect_value_type(val['value'])
                    unit = self._detect_unit(val['value'])
                    
                    # Use raw SQL to insert into fact_values table (Laravel compatible)
                    insert_query = text("""
                        INSERT INTO fact_values (parent_type, parent_id, value_type, value_continuous, value_categorical, unit, created_at)
                        VALUES ('condition_fact', :parent_id, :value_type, :value_continuous, :value_categorical, :unit, NOW())
                    """)
                    self.session.execute(insert_query, {
                        'parent_id': cond_fact.id,
                        'value_type': val_type.value,
                        'value_continuous': cont,
                        'value_categorical': cat,
                        'unit': unit
                    })

            # Store actions
            for act in rule['actions']:
                act_fact = RuleActionFact(
                    rule_id=kb_rule.id,
                    subject=act['subject'],
                    operator=self._normalize_operator(act.get('operator', '=')),
                    logical_operator=act.get('logical_operator'),
                    group_id=act.get('group_id')
                )
                self.session.add(act_fact)
                self.session.flush()

                # Store action values using raw SQL (Laravel-compatible structure)
                for val in act.get('values', []):
                    val_type, cont, cat = self._detect_value_type(val['value'])
                    unit = self._detect_unit(val['value'])
                    
                    # Use raw SQL to insert into fact_values table (Laravel compatible)
                    insert_query = text("""
                        INSERT INTO fact_values (parent_type, parent_id, value_type, value_continuous, value_categorical, unit, created_at)
                        VALUES ('action_fact', :parent_id, :value_type, :value_continuous, :value_categorical, :unit, NOW())
                    """)
                    self.session.execute(insert_query, {
                        'parent_id': act_fact.id,
                        'value_type': val_type.value,
                        'value_continuous': cont,
                        'value_categorical': cat,
                        'unit': unit
                    })

            self.session.commit()
            self.log(f"   Stored rule: {rule['source_text'][:50]}...")

        except Exception as e:
            self.session.rollback()
            self.log(f"   Error storing rule: {str(e)}")

    def _store_fact(self, fact: Dict):
        """Store fact in database"""
        try:
            # All extracted data starts as PENDING_REVIEW for admin review
            # Validation only checks if data is well-formed
            status = StatusEnum.PENDING_REVIEW

            # Create knowledge fact
            kb_fact = KnowledgeFact(
                source_text=fact['source_text'],
                subject=fact['subject'],
                relation=fact['relation'],
                domain='',  # Empty string instead of None (Laravel doesn't allow NULL)
                visibility='private',
                confidence_score=fact['confidence'],
                extraction_method=fact['extraction_method'],
                algorithm_used='',  # Empty string instead of None
                status=status
            )
            self.session.add(kb_fact)
            self.session.flush()

            # Store values using raw SQL (Laravel-compatible structure)
            for val in fact.get('values', []):
                val_type, cont, cat = self._detect_value_type(val['value'])
                unit = self._detect_unit(val['value'])
                
                # Use raw SQL to insert into fact_values table (Laravel compatible)
                insert_query = text("""
                    INSERT INTO fact_values (parent_type, parent_id, value_type, value_continuous, value_categorical, unit, created_at)
                    VALUES ('knowledge_fact', :parent_id, :value_type, :value_continuous, :value_categorical, :unit, NOW())
                """)
                self.session.execute(insert_query, {
                    'parent_id': kb_fact.id,
                    'value_type': val_type.value,
                    'value_continuous': cont,
                    'value_categorical': cat,
                    'unit': unit
                })

            self.session.commit()
            self.log(f"  ✅ Stored fact: {fact['subject']} {fact['relation']} ...")

        except Exception as e:
            self.session.rollback()
            self.log(f"   Error storing fact: {str(e)}")

    # ============ LOGGING ============

    def log(self, message: str):
        """Add message to extraction log"""
        self.extraction_log.append(message)
        print(message)


def extract_pipeline1(text: str, document_id: int = None) -> Dict:
    """
    Main entry point for Pipeline 1 extraction
    """
    extractor = KnowledgeExtractor()
    return extractor.extract_from_text(text, document_id)
