"""
Pipeline 2: Storage Layer
Handles database operations for knowledge classification
Reads unclassified items and updates them with predicted domains
"""

from typing import List, Dict, Tuple
from sqlalchemy import text
from datetime import datetime
from pipeline1.models import get_session, KnowledgeRule, KnowledgeFact

class DomainStorage:
    """Handle database operations for domain classification"""

    def __init__(self):
        self.session = get_session()

    def get_unclassified_rules(self) -> List[Dict]:
        """
        Fetch all knowledge_rules where domain IS NULL
        Returns list of dicts with id, source_text for classification
        """
        try:
            query = text("""
                SELECT 
                    id,
                    source_text
                FROM knowledge_rules
                WHERE domain IS NULL
                LIMIT 100
            """)
            
            results = self.session.execute(query).fetchall()
            
            items = []
            for row in results:
                items.append({
                    "id": row[0],
                    "type": "rule",
                    "text": row[1],
                    "source_text": row[1]
                })
            
            return items
        except Exception as e:
            print(f"❌ Error fetching unclassified rules: {str(e)}")
            return []

    def get_unclassified_facts(self) -> List[Dict]:
        """
        Fetch all knowledge_facts where domain IS NULL
        Returns list of dicts with id, source_text for classification
        """
        try:
            query = text("""
                SELECT 
                    id,
                    source_text
                FROM knowledge_facts
                WHERE domain IS NULL
                LIMIT 100
            """)
            
            results = self.session.execute(query).fetchall()
            
            items = []
            for row in results:
                items.append({
                    "id": row[0],
                    "type": "fact",
                    "text": row[1],
                    "source_text": row[1]
                })
            
            return items
        except Exception as e:
            print(f" Error fetching unclassified facts: {str(e)}")
            return []

    def get_all_unclassified(self) -> List[Dict]:
        """Fetch all unclassified items (rules + facts)"""
        rules = self.get_unclassified_rules()
        facts = self.get_unclassified_facts()
        return rules + facts

    def update_rule_domain(self, rule_id: int, domain: str, algorithm_used: str) -> bool:
        """Update knowledge_rule with predicted domain and algorithm"""
        try:
            query = text("""
                UPDATE knowledge_rules
                SET domain = :domain, 
                    algorithm_used = :algorithm_used,
                    updated_at = NOW()
                WHERE id = :id
            """)
            
            self.session.execute(query, {
                "domain": domain,
                "algorithm_used": algorithm_used,
                "id": rule_id
            })
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f" Error updating rule domain: {str(e)}")
            return False

    def update_fact_domain(self, fact_id: int, domain: str, algorithm_used: str) -> bool:
        """Update knowledge_fact with predicted domain and algorithm"""
        try:
            query = text("""
                UPDATE knowledge_facts
                SET domain = :domain,
                    algorithm_used = :algorithm_used,
                    updated_at = NOW()
                WHERE id = :id
            """)
            
            self.session.execute(query, {
                "domain": domain,
                "algorithm_used": algorithm_used,
                "id": fact_id
            })
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f" Error updating fact domain: {str(e)}")
            return False

    def batch_update_domains(self, classifications: List[Dict]) -> Dict:
        """
        Batch update multiple items with their predicted domains
        Args:
            classifications: List of dicts with id, type, predicted_domain, algorithm_used
        Returns:
            Dict with success count and errors
        """
        results = {
            "total": len(classifications),
            "updated_rules": 0,
            "updated_facts": 0,
            "failed": 0,
            "errors": []
        }

        for item in classifications:
            try:
                item_id = item.get("id")
                item_type = item.get("type")
                domain = item.get("predicted_domain")
                algorithm = item.get("algorithm_used")

                if item_type == "rule":
                    success = self.update_rule_domain(item_id, domain, algorithm)
                    if success:
                        results["updated_rules"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Failed to update rule {item_id}")
                
                elif item_type == "fact":
                    success = self.update_fact_domain(item_id, domain, algorithm)
                    if success:
                        results["updated_facts"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Failed to update fact {item_id}")
            
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(str(e))

        return results

    def get_classification_stats(self) -> Dict:
        """Get statistics on classified vs unclassified items"""
        try:
            stats_query = text("""
                SELECT 
                    'rules' as type,
                    COUNT(*) as total,
                    SUM(CASE WHEN domain IS NOT NULL THEN 1 ELSE 0 END) as classified,
                    SUM(CASE WHEN domain IS NULL THEN 1 ELSE 0 END) as unclassified,
                    COUNT(DISTINCT domain) as unique_domains
                FROM knowledge_rules
                UNION ALL
                SELECT 
                    'facts' as type,
                    COUNT(*) as total,
                    SUM(CASE WHEN domain IS NOT NULL THEN 1 ELSE 0 END) as classified,
                    SUM(CASE WHEN domain IS NULL THEN 1 ELSE 0 END) as unclassified,
                    COUNT(DISTINCT domain) as unique_domains
                FROM knowledge_facts
            """)
            
            results = self.session.execute(stats_query).fetchall()
            
            stats = {}
            for row in results:
                stats[row[0]] = {
                    "total": row[1],
                    "classified": row[2],
                    "unclassified": row[3],
                    "unique_domains": row[4]
                }
            
            return stats
        except Exception as e:
            print(f"❌ Error getting classification stats: {str(e)}")
            return {}

    def close(self):
        """Close database session"""
        self.session.close()


# Initialize global storage
storage = DomainStorage()
