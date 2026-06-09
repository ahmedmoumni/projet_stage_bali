<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('knowledge_facts', function (Blueprint $table) {
            $table->id();
            $table->text('source_text');
            $table->string('subject', 255); // e.g. north_district, village
            $table->string('relation', 255); // e.g. lacks, has_population, supervised_by
            $table->string('domain', 50); // social | economy | infrastructure | health | culture_art
            $table->enum('visibility', ['public', 'private'])->default('public');
            $table->float('confidence_score')->default(0.0); // 0.0 to 1.0
            $table->enum('extraction_method', ['spacy', 'llm'])->default('spacy');
            $table->string('algorithm_used', 50); // naive_bayes | decision_tree
            $table->enum('status', ['validated', 'pending_review'])->default('pending_review');
            $table->timestamps();

            $table->index('domain');
            $table->index('status');
            $table->index('visibility');
            $table->index('subject');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('knowledge_facts');
    }
};
