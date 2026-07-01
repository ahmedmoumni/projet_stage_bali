<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\KnowledgeFact;
use App\Models\FactValue;

class KnowledgeFactSeeder extends Seeder
{
    public function run(): void
    {
        KnowledgeFact::query()->delete();
        FactValue::query()->delete();

        // Fact 1
        $fact1 = KnowledgeFact::create([
            'source_text' => 'Desa Punggul has clean water access for 3400 persons',
            'subject' => 'Desa Punggul',
            'relation' => 'has_water_access',
            'domain' => 'infrastructure',
            'visibility' => 'public',
            'status' => 'validated',
            'confidence_score' => 0.92,
            'extraction_method' => 'spacy',
            'algorithm_used' => 'triplet_extraction',
        ]);

        FactValue::create([
            'parent_type' => 'knowledge_fact',
            'parent_id' => $fact1->id,
            'value_type' => 'continuous',
            'value_continuous' => 3400,
            'value_categorical' => null,
            'unit' => 'persons',
        ]);

        // Fact 2
        $fact2 = KnowledgeFact::create([
            'source_text' => 'Primary crops in the village are rice, corn and cassava',
            'subject' => 'Desa Punggul',
            'relation' => 'primary_crops',
            'domain' => 'economy',
            'visibility' => 'public',
            'status' => 'validated',
            'confidence_score' => 0.88,
            'extraction_method' => 'llm',
            'algorithm_used' => 'groq_extraction',
        ]);

        FactValue::create([
            'parent_type' => 'knowledge_fact',
            'parent_id' => $fact2->id,
            'value_type' => 'categorical',
            'value_continuous' => null,
            'value_categorical' => 'rice',
            'unit' => null,
        ]);

        FactValue::create([
            'parent_type' => 'knowledge_fact',
            'parent_id' => $fact2->id,
            'value_type' => 'categorical',
            'value_continuous' => null,
            'value_categorical' => 'corn',
            'unit' => null,
        ]);

        FactValue::create([
            'parent_type' => 'knowledge_fact',
            'parent_id' => $fact2->id,
            'value_type' => 'categorical',
            'value_continuous' => null,
            'value_categorical' => 'cassava',
            'unit' => null,
        ]);

        // Fact 3
        $fact3 = KnowledgeFact::create([
            'source_text' => 'Traditional weaving is a cultural practice',
            'subject' => 'Traditional weaving',
            'relation' => 'is_cultural_practice',
            'domain' => 'culture_art',
            'visibility' => 'public',
            'status' => 'pending_review',
            'confidence_score' => 0.75,
            'extraction_method' => 'spacy',
            'algorithm_used' => 'ner_based',
        ]);

        FactValue::create([
            'parent_type' => 'knowledge_fact',
            'parent_id' => $fact3->id,
            'value_type' => 'categorical',
            'value_continuous' => null,
            'value_categorical' => 'weaving',
            'unit' => null,
        ]);

        // Fact 4
        $fact4 = KnowledgeFact::create([
            'source_text' => 'Health clinic located 2km from village center',
            'subject' => 'Health clinic',
            'relation' => 'distance_from_center',
            'domain' => 'health',
            'visibility' => 'private',
            'status' => 'validated',
            'confidence_score' => 0.90,
            'extraction_method' => 'llm',
            'algorithm_used' => 'groq_extraction',
        ]);

        FactValue::create([
            'parent_type' => 'knowledge_fact',
            'parent_id' => $fact4->id,
            'value_type' => 'continuous',
            'value_continuous' => 2,
            'value_categorical' => null,
            'unit' => 'km',
        ]);

        // Fact 5
        $fact5 = KnowledgeFact::create([
            'source_text' => 'Community center supports 150 youth members',
            'subject' => 'Community center',
            'relation' => 'supports_youth_members',
            'domain' => 'social',
            'visibility' => 'public',
            'status' => 'validated',
            'confidence_score' => 0.85,
            'extraction_method' => 'spacy',
            'algorithm_used' => 'triplet_extraction',
        ]);

        FactValue::create([
            'parent_type' => 'knowledge_fact',
            'parent_id' => $fact5->id,
            'value_type' => 'continuous',
            'value_continuous' => 150,
            'value_categorical' => null,
            'unit' => 'members',
        ]);

        // Fact 6
        $fact6 = KnowledgeFact::create([
            'source_text' => 'Market operates on Tuesday and Friday',
            'subject' => 'Market',
            'relation' => 'operates_on_days',
            'domain' => 'economy',
            'visibility' => 'public',
            'status' => 'validated',
            'confidence_score' => 0.87,
            'extraction_method' => 'llm',
            'algorithm_used' => 'groq_extraction',
        ]);

        FactValue::create([
            'parent_type' => 'knowledge_fact',
            'parent_id' => $fact6->id,
            'value_type' => 'categorical',
            'value_continuous' => null,
            'value_categorical' => 'Tuesday',
            'unit' => null,
        ]);

        FactValue::create([
            'parent_type' => 'knowledge_fact',
            'parent_id' => $fact6->id,
            'value_type' => 'categorical',
            'value_continuous' => null,
            'value_categorical' => 'Friday',
            'unit' => null,
        ]);

        // Fact 7
        $fact7 = KnowledgeFact::create([
            'source_text' => 'School has 500 students across 12 classrooms',
            'subject' => 'School',
            'relation' => 'has_students',
            'domain' => 'health',
            'visibility' => 'private',
            'status' => 'pending_review',
            'confidence_score' => 0.80,
            'extraction_method' => 'spacy',
            'algorithm_used' => 'ner_based',
        ]);

        FactValue::create([
            'parent_type' => 'knowledge_fact',
            'parent_id' => $fact7->id,
            'value_type' => 'continuous',
            'value_continuous' => 500,
            'value_categorical' => null,
            'unit' => 'students',
        ]);

        // Fact 8
        $fact8 = KnowledgeFact::create([
            'source_text' => 'Irrigation system covers 45 hectares',
            'subject' => 'Irrigation system',
            'relation' => 'covers_area',
            'domain' => 'infrastructure',
            'visibility' => 'public',
            'status' => 'validated',
            'confidence_score' => 0.91,
            'extraction_method' => 'llm',
            'algorithm_used' => 'groq_extraction',
        ]);

        FactValue::create([
            'parent_type' => 'knowledge_fact',
            'parent_id' => $fact8->id,
            'value_type' => 'continuous',
            'value_continuous' => 45,
            'value_categorical' => null,
            'unit' => 'hectares',
        ]);
    }
}
