<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\KnowledgeRule;

class KnowledgeRuleSeeder extends Seeder
{
    public function run(): void
    {
        KnowledgeRule::query()->delete();

        KnowledgeRule::create([
            'source_text' => 'Desa Punggul has a community center for meetings and gatherings',
            'domain' => 'infrastructure',
            'visibility' => 'public',
            'status' => 'validated',
            'confidence_score' => 0.95,
            'extraction_method' => 'spacy',
            'algorithm_used' => 'ner',
        ]);

        KnowledgeRule::create([
            'source_text' => 'The village economy is based on agriculture and farming',
            'domain' => 'economy',
            'visibility' => 'public',
            'status' => 'validated',
            'confidence_score' => 0.87,
            'extraction_method' => 'llm',
            'algorithm_used' => 'groq',
        ]);

        KnowledgeRule::create([
            'source_text' => 'Cultural events are held monthly at the village square',
            'domain' => 'culture_art',
            'visibility' => 'public',
            'status' => 'pending_review',
            'confidence_score' => 0.72,
            'extraction_method' => 'spacy',
            'algorithm_used' => 'pattern_matching',
        ]);

        KnowledgeRule::create([
            'source_text' => 'Health clinic operates on weekdays from 8am to 4pm',
            'domain' => 'health',
            'visibility' => 'private',
            'status' => 'validated',
            'confidence_score' => 0.91,
            'extraction_method' => 'llm',
            'algorithm_used' => 'groq',
        ]);

        KnowledgeRule::create([
            'source_text' => 'Social assistance program benefits 200 families in the village',
            'domain' => 'social',
            'visibility' => 'public',
            'status' => 'validated',
            'confidence_score' => 0.84,
            'extraction_method' => 'spacy',
            'algorithm_used' => 'ner',
        ]);

        KnowledgeRule::create([
            'source_text' => 'Infrastructure development project planned for next year',
            'domain' => 'infrastructure',
            'visibility' => 'private',
            'status' => 'pending_review',
            'confidence_score' => 0.78,
            'extraction_method' => 'llm',
            'algorithm_used' => 'groq',
        ]);

        KnowledgeRule::create([
            'source_text' => 'Local cooperative market sells fresh produce daily',
            'domain' => 'economy',
            'visibility' => 'public',
            'status' => 'validated',
            'confidence_score' => 0.88,
            'extraction_method' => 'spacy',
            'algorithm_used' => 'ner',
        ]);

        KnowledgeRule::create([
            'source_text' => 'Traditional dance performances happen during festival',
            'domain' => 'culture_art',
            'visibility' => 'public',
            'status' => 'validated',
            'confidence_score' => 0.81,
            'extraction_method' => 'spacy',
            'algorithm_used' => 'pattern_matching',
        ]);

        KnowledgeRule::create([
            'source_text' => 'Community wellness program offers free health checkups',
            'domain' => 'health',
            'visibility' => 'public',
            'status' => 'validated',
            'confidence_score' => 0.93,
            'extraction_method' => 'llm',
            'algorithm_used' => 'groq',
        ]);

        KnowledgeRule::create([
            'source_text' => 'Youth education program targeting disadvantaged families',
            'domain' => 'social',
            'visibility' => 'public',
            'status' => 'pending_review',
            'confidence_score' => 0.76,
            'extraction_method' => 'llm',
            'algorithm_used' => 'groq',
        ]);
    }
}
