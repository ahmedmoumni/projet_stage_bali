<?php

namespace Database\Seeders;

use App\Models\DocumentLog;
use App\Models\FactValue;
use App\Models\KnowledgeFact;
use App\Models\KnowledgeRule;
use App\Models\RuleActionFact;
use App\Models\RuleConditionFact;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class KnowledgeSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        // ========================================
        // RULE 1: Water Access Rule
        // ========================================
        $rule1 = KnowledgeRule::create([
            'source_text' => 'IF household lacks water access AND has low income THEN recommend water_program',
            'domain' => 'infrastructure',
            'visibility' => 'public',
            'confidence_score' => 0.92,
            'extraction_method' => 'spacy',
            'algorithm_used' => 'decision_tree',
            'condition_group_operator' => 'AND',
            'action_group_operator' => null,
            'status' => 'validated',
        ]);

        // Conditions for Rule 1
        $cond1_1 = RuleConditionFact::create([
            'rule_id' => $rule1->id,
            'subject' => 'water_access',
            'operator' => '=',
            'logical_operator' => null,
            'group_id' => 1,
        ]);

        FactValue::create([
            'parent_type' => 'condition_fact',
            'parent_id' => $cond1_1->id,
            'value_type' => 'categorical',
            'value_categorical' => 'lacks',
            'unit' => null,
        ]);

        $cond1_2 = RuleConditionFact::create([
            'rule_id' => $rule1->id,
            'subject' => 'income_level',
            'operator' => '<',
            'logical_operator' => 'AND',
            'group_id' => 1,
        ]);

        FactValue::create([
            'parent_type' => 'condition_fact',
            'parent_id' => $cond1_2->id,
            'value_type' => 'continuous',
            'value_continuous' => 2000000.0,
            'unit' => 'IDR',
        ]);

        // Actions for Rule 1
        $action1 = RuleActionFact::create([
            'rule_id' => $rule1->id,
            'subject' => 'recommendation',
            'operator' => '=',
            'logical_operator' => null,
            'group_id' => null,
        ]);

        FactValue::create([
            'parent_type' => 'action_fact',
            'parent_id' => $action1->id,
            'value_type' => 'categorical',
            'value_categorical' => 'water_program',
            'unit' => null,
        ]);

        // ========================================
        // RULE 2: Digital Access Rule
        // ========================================
        $rule2 = KnowledgeRule::create([
            'source_text' => 'IF household has no internet OR age > 60 THEN needs_digital_support',
            'domain' => 'economy',
            'visibility' => 'public',
            'confidence_score' => 0.85,
            'extraction_method' => 'llm',
            'algorithm_used' => 'naive_bayes',
            'condition_group_operator' => 'OR',
            'action_group_operator' => null,
            'status' => 'validated',
        ]);

        // Conditions for Rule 2
        $cond2_1 = RuleConditionFact::create([
            'rule_id' => $rule2->id,
            'subject' => 'internet_access',
            'operator' => '=',
            'logical_operator' => null,
            'group_id' => 2,
        ]);

        FactValue::create([
            'parent_type' => 'condition_fact',
            'parent_id' => $cond2_1->id,
            'value_type' => 'categorical',
            'value_categorical' => 'no',
            'unit' => null,
        ]);

        $cond2_2 = RuleConditionFact::create([
            'rule_id' => $rule2->id,
            'subject' => 'age',
            'operator' => '>',
            'logical_operator' => 'OR',
            'group_id' => 2,
        ]);

        FactValue::create([
            'parent_type' => 'condition_fact',
            'parent_id' => $cond2_2->id,
            'value_type' => 'continuous',
            'value_continuous' => 60.0,
            'unit' => 'years',
        ]);

        // Actions for Rule 2
        $action2 = RuleActionFact::create([
            'rule_id' => $rule2->id,
            'subject' => 'support_needed',
            'operator' => '=',
            'logical_operator' => null,
            'group_id' => null,
        ]);

        FactValue::create([
            'parent_type' => 'action_fact',
            'parent_id' => $action2->id,
            'value_type' => 'categorical',
            'value_categorical' => 'digital_support',
            'unit' => null,
        ]);

        // ========================================
        // RULE 3: Health Screening Rule
        // ========================================
        $rule3 = KnowledgeRule::create([
            'source_text' => 'IF disease_status = chronic AND visits_health_facility < 2 THEN recommend_health_program',
            'domain' => 'health',
            'visibility' => 'public',
            'confidence_score' => 0.88,
            'extraction_method' => 'spacy',
            'algorithm_used' => 'decision_tree',
            'condition_group_operator' => 'AND',
            'action_group_operator' => null,
            'status' => 'pending_review',
        ]);

        // Conditions for Rule 3
        $cond3_1 = RuleConditionFact::create([
            'rule_id' => $rule3->id,
            'subject' => 'disease_status',
            'operator' => '=',
            'logical_operator' => null,
            'group_id' => 3,
        ]);

        FactValue::create([
            'parent_type' => 'condition_fact',
            'parent_id' => $cond3_1->id,
            'value_type' => 'categorical',
            'value_categorical' => 'chronic',
            'unit' => null,
        ]);

        $cond3_2 = RuleConditionFact::create([
            'rule_id' => $rule3->id,
            'subject' => 'health_facility_visits',
            'operator' => '<',
            'logical_operator' => 'AND',
            'group_id' => 3,
        ]);

        FactValue::create([
            'parent_type' => 'condition_fact',
            'parent_id' => $cond3_2->id,
            'value_type' => 'continuous',
            'value_continuous' => 2.0,
            'unit' => 'times_per_year',
        ]);

        // Actions for Rule 3
        $action3 = RuleActionFact::create([
            'rule_id' => $rule3->id,
            'subject' => 'program_recommendation',
            'operator' => '=',
            'logical_operator' => null,
            'group_id' => null,
        ]);

        FactValue::create([
            'parent_type' => 'action_fact',
            'parent_id' => $action3->id,
            'value_type' => 'categorical',
            'value_categorical' => 'health_program',
            'unit' => null,
        ]);

        // ========================================
        // KNOWLEDGE FACTS
        // ========================================

        // Fact 1: North district population
        $fact1 = KnowledgeFact::create([
            'source_text' => 'North district has population of 5000 persons',
            'subject' => 'north_district',
            'relation' => 'has_population',
            'domain' => 'social',
            'visibility' => 'public',
            'confidence_score' => 0.95,
            'extraction_method' => 'spacy',
            'algorithm_used' => 'naive_bayes',
            'status' => 'validated',
        ]);

        FactValue::create([
            'parent_type' => 'knowledge_fact',
            'parent_id' => $fact1->id,
            'value_type' => 'continuous',
            'value_continuous' => 5000.0,
            'unit' => 'persons',
        ]);

        // Fact 2: West sector lacks electricity
        $fact2 = KnowledgeFact::create([
            'source_text' => 'West sector lacks reliable electricity infrastructure',
            'subject' => 'west_sector',
            'relation' => 'lacks',
            'domain' => 'infrastructure',
            'visibility' => 'public',
            'confidence_score' => 0.98,
            'extraction_method' => 'spacy',
            'algorithm_used' => 'decision_tree',
            'status' => 'validated',
        ]);

        FactValue::create([
            'parent_type' => 'knowledge_fact',
            'parent_id' => $fact2->id,
            'value_type' => 'categorical',
            'value_categorical' => 'electricity',
            'unit' => null,
        ]);

        // Fact 3: Village is supervised by district health office
        $fact3 = KnowledgeFact::create([
            'source_text' => 'Village is supervised by district health office',
            'subject' => 'village',
            'relation' => 'supervised_by',
            'domain' => 'health',
            'visibility' => 'public',
            'confidence_score' => 0.99,
            'extraction_method' => 'llm',
            'algorithm_used' => 'naive_bayes',
            'status' => 'validated',
        ]);

        FactValue::create([
            'parent_type' => 'knowledge_fact',
            'parent_id' => $fact3->id,
            'value_type' => 'categorical',
            'value_categorical' => 'district_health_office',
            'unit' => null,
        ]);

        // ========================================
        // DOCUMENT LOGS
        // ========================================

        DocumentLog::create([
            'filename' => 'village_report_2024.pdf',
            'file_type' => 'pdf_native',
            'routing' => 'pipeline1',
            'pages' => 15,
            'rules_extracted' => 3,
            'facts_extracted' => 3,
            'processed_at' => now(),
        ]);

        DocumentLog::create([
            'filename' => 'health_survey.csv',
            'file_type' => 'csv',
            'routing' => 'pipeline2_direct',
            'pages' => null,
            'rules_extracted' => 1,
            'facts_extracted' => 5,
            'processed_at' => now()->subDay(),
        ]);

        DocumentLog::create([
            'filename' => 'scanned_regulation.pdf',
            'file_type' => 'pdf_scanned',
            'routing' => 'ocr_then_pipeline1',
            'pages' => 8,
            'rules_extracted' => 2,
            'facts_extracted' => 4,
            'processed_at' => now()->subDays(2),
        ]);
    }
}
