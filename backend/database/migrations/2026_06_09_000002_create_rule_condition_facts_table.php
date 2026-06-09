<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('rule_condition_facts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('rule_id')->constrained('knowledge_rules')->cascadeOnDelete();
            $table->string('subject', 255); // e.g. age, income, water
            $table->string('operator', 50); // > < >= <= = IN BETWEEN
            $table->string('logical_operator', 10)->nullable(); // AND | OR
            $table->integer('group_id')->nullable(); // for grouping with parentheses
            $table->timestamps();

            $table->index('rule_id');
            $table->index('group_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('rule_condition_facts');
    }
};
